from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError
import json
import logging
from typing import Callable, Optional, Any, Dict
from datetime import datetime

from config.settings import settings

logger = logging.getLogger(__name__)


class RedpandaClient:
    """Redpanda (Kafka-compatible) client for event streaming"""

    # Topic definitions
    TOPICS = {
        "SHIPMENT_REQUESTS": "shipment.requests",
        "PACKING_RESULTS": "packing.results",
        "ROUTE_UPDATES": "route.updates",
        "WEATHER_ALERTS": "weather.alerts",
        "TRAFFIC_UPDATES": "traffic.updates",
        "DAMAGE_PREDICTIONS": "damage.predictions",
        "NOTIFICATIONS": "notifications"
    }

    def __init__(self):
        self.bootstrap_servers = settings.REDPANDA_BOOTSTRAP_SERVERS
        self.producer: Optional[KafkaProducer] = None
        self.consumers: Dict[str, KafkaConsumer] = {}

    def _create_producer(self) -> KafkaProducer:
        """Create Kafka producer"""
        try:
            producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None,
                acks='all',
                retries=3,
                max_in_flight_requests_per_connection=1
            )
            logger.info(f"Created Redpanda producer: {self.bootstrap_servers}")
            return producer
        except Exception as e:
            logger.error(f"Failed to create producer: {e}")
            raise

    def get_producer(self) -> KafkaProducer:
        """Get or create producer instance"""
        if not self.producer:
            self.producer = self._create_producer()
        return self.producer

    def publish(
        self,
        topic: str,
        message: dict,
        key: str = None
    ) -> bool:
        """
        Publish message to Redpanda topic

        Args:
            topic: Topic name (use TOPICS constants)
            message: Message payload (will be JSON serialized)
            key: Optional message key for partitioning

        Returns:
            bool: True if published successfully
        """
        try:
            producer = self.get_producer()

            # Add metadata
            message['_published_at'] = datetime.utcnow().isoformat()
            message['_topic'] = topic

            # Send message
            future = producer.send(topic, value=message, key=key)
            record_metadata = future.get(timeout=10)

            logger.info(
                f"Published to {topic}: partition={record_metadata.partition}, "
                f"offset={record_metadata.offset}"
            )
            return True

        except KafkaError as e:
            logger.error(f"Failed to publish to {topic}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error publishing to {topic}: {e}")
            return False

    # Convenience methods for specific topics

    def publish_shipment_request(self, shipment_data: dict) -> bool:
        """Publish shipment request event"""
        return self.publish(
            self.TOPICS["SHIPMENT_REQUESTS"],
            {
                "event_type": "shipment_request",
                "shipment_data": shipment_data
            },
            key=shipment_data.get("shipment_id")
        )

    def publish_packing_result(self, packing_result: dict) -> bool:
        """Publish packing optimization result"""
        return self.publish(
            self.TOPICS["PACKING_RESULTS"],
            {
                "event_type": "packing_result",
                "result": packing_result
            },
            key=packing_result.get("shipment_id")
        )

    def publish_route_update(self, route_data: dict) -> bool:
        """Publish route condition update"""
        return self.publish(
            self.TOPICS["ROUTE_UPDATES"],
            {
                "event_type": "route_update",
                "route_data": route_data
            },
            key=route_data.get("route_id")
        )

    def publish_weather_alert(self, weather_data: dict) -> bool:
        """Publish weather alert"""
        return self.publish(
            self.TOPICS["WEATHER_ALERTS"],
            {
                "event_type": "weather_alert",
                "weather_data": weather_data
            },
            key=weather_data.get("route_id")
        )

    def publish_traffic_update(self, traffic_data: dict) -> bool:
        """Publish traffic update"""
        return self.publish(
            self.TOPICS["TRAFFIC_UPDATES"],
            {
                "event_type": "traffic_update",
                "traffic_data": traffic_data
            },
            key=traffic_data.get("route_id")
        )

    def publish_damage_prediction(self, prediction_data: dict) -> bool:
        """Publish damage risk prediction"""
        return self.publish(
            self.TOPICS["DAMAGE_PREDICTIONS"],
            {
                "event_type": "damage_prediction",
                "prediction": prediction_data
            },
            key=prediction_data.get("shipment_id")
        )

    def publish_notification(self, notification: dict) -> bool:
        """Publish system notification"""
        return self.publish(
            self.TOPICS["NOTIFICATIONS"],
            {
                "event_type": "notification",
                "notification": notification
            }
        )

    def create_consumer(
        self,
        topics: list[str],
        group_id: str,
        auto_offset_reset: str = 'latest'
    ) -> KafkaConsumer:
        """
        Create Kafka consumer

        Args:
            topics: List of topics to subscribe to
            group_id: Consumer group ID
            auto_offset_reset: 'earliest' or 'latest'

        Returns:
            KafkaConsumer instance
        """
        try:
            consumer = KafkaConsumer(
                *topics,
                bootstrap_servers=self.bootstrap_servers,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                key_deserializer=lambda k: k.decode('utf-8') if k else None,
                group_id=group_id,
                auto_offset_reset=auto_offset_reset,
                enable_auto_commit=True,
                consumer_timeout_ms=1000
            )

            logger.info(
                f"Created consumer for topics {topics} "
                f"with group_id {group_id}"
            )
            return consumer

        except Exception as e:
            logger.error(f"Failed to create consumer: {e}")
            raise

    def consume(
        self,
        topics: list[str],
        group_id: str,
        callback: Callable[[dict], None],
        auto_offset_reset: str = 'latest'
    ):
        """
        Consume messages from topics

        Args:
            topics: List of topics to consume from
            group_id: Consumer group ID
            callback: Function to call for each message
            auto_offset_reset: 'earliest' or 'latest'
        """
        consumer = self.create_consumer(topics, group_id, auto_offset_reset)

        try:
            logger.info(f"Starting consumer for topics: {topics}")
            for message in consumer:
                try:
                    callback(message.value)
                except Exception as e:
                    logger.error(
                        f"Error processing message from {message.topic}: {e}"
                    )
        except KeyboardInterrupt:
            logger.info("Consumer interrupted by user")
        finally:
            consumer.close()
            logger.info("Consumer closed")

    async def consume_async(
        self,
        topics: list[str],
        group_id: str,
        callback: Callable[[dict], Any],
        auto_offset_reset: str = 'latest'
    ):
        """
        Async consumer for integration with FastAPI

        Args:
            topics: List of topics to consume from
            group_id: Consumer group ID
            callback: Async function to call for each message
            auto_offset_reset: 'earliest' or 'latest'
        """
        import asyncio

        consumer = self.create_consumer(topics, group_id, auto_offset_reset)

        try:
            logger.info(f"Starting async consumer for topics: {topics}")
            while True:
                # Poll for messages with timeout
                message_batch = consumer.poll(timeout_ms=100)

                for topic_partition, messages in message_batch.items():
                    for message in messages:
                        try:
                            # Call async callback
                            await callback(message.value)
                        except Exception as e:
                            logger.error(
                                f"Error processing message from {message.topic}: {e}"
                            )

                # Allow other tasks to run
                await asyncio.sleep(0.01)

        except Exception as e:
            logger.error(f"Consumer error: {e}")
        finally:
            consumer.close()
            logger.info("Async consumer closed")

    def close(self):
        """Close producer and consumers"""
        if self.producer:
            self.producer.close()
            logger.info("Producer closed")

        for consumer in self.consumers.values():
            consumer.close()
        logger.info("All consumers closed")


# Global Redpanda client instance
redpanda = RedpandaClient()
