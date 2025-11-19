from typing import Optional, List, Dict, Any
import logging
from datetime import datetime
from uuid import uuid4

from kitt_mcp.database import db
from kitt_mcp.redpanda_client import redpanda
from kitt_mcp.claude_client import claude
from services.deeppack3d_service import get_deeppack_service
from services.weather_service import get_weather_service
from services.traffic_service import get_traffic_service
from services.geocoding_service import get_geocoding_service

logger = logging.getLogger(__name__)


class MCPTools:
    """MCP Tools for KITT freight optimization"""

    def __init__(self):
        self.db = db
        self.redpanda = redpanda
        self.claude = claude

    # Shipment Management Tools

    async def get_shipment_data(self, shipment_id: str) -> Dict[str, Any]:
        """
        Get complete shipment data including items

        Args:
            shipment_id: Shipment ID

        Returns:
            dict: Shipment data with items
        """
        try:
            shipment = await self.db.get_shipment(shipment_id)
            if not shipment:
                return {"error": f"Shipment {shipment_id} not found"}

            items = await self.db.get_shipment_items(shipment_id)
            packing_plans = await self.db.get_shipment_packing_plans(shipment_id)
            predictions = await self.db.get_shipment_predictions(shipment_id)

            return {
                "shipment": shipment,
                "items": items,
                "packing_plans": packing_plans,
                "ai_predictions": predictions
            }
        except Exception as e:
            logger.error(f"Error getting shipment data: {e}")
            return {"error": str(e)}

    async def create_shipment(
        self,
        origin: str,
        destination: str,
        items: List[dict],
        priority: str = "medium",
        deadline: str = None
    ) -> Dict[str, Any]:
        """
        Create new shipment with items

        Args:
            origin: Origin location
            destination: Destination location
            items: List of items (each with width, height, depth, weight)
            priority: Shipment priority (low/medium/high/critical)
            deadline: Deadline timestamp (ISO format)

        Returns:
            dict: Created shipment data
        """
        try:
            shipment_id = f"SH-{str(uuid4())[:8].upper()}"

            # Create shipment
            await self.db.create_shipment(
                shipment_id=shipment_id,
                origin=origin,
                destination=destination,
                priority=priority,
                deadline=datetime.fromisoformat(deadline) if deadline else None
            )

            # Add items
            for idx, item_data in enumerate(items):
                item_id = f"{shipment_id}-ITEM-{idx:03d}"
                await self.db.add_item(
                    item_id=item_id,
                    shipment_id=shipment_id,
                    width=item_data["width"],
                    height=item_data["height"],
                    depth=item_data["depth"],
                    weight=item_data["weight"],
                    fragile=item_data.get("fragile", False),
                    stackable=item_data.get("stackable", True),
                    description=item_data.get("description")
                )

            # Publish event to Redpanda
            self.redpanda.publish_shipment_request({
                "shipment_id": shipment_id,
                "origin": origin,
                "destination": destination,
                "items_count": len(items),
                "priority": priority
            })

            logger.info(f"Created shipment {shipment_id} with {len(items)} items")

            return {
                "success": True,
                "shipment_id": shipment_id,
                "items_added": len(items)
            }

        except Exception as e:
            logger.error(f"Error creating shipment: {e}")
            return {"error": str(e)}

    # Packing Optimization Tools

    async def optimize_packing(
        self,
        shipment_id: str,
        truck_id: str = None
    ) -> Dict[str, Any]:
        """
        Optimize packing for shipment

        Args:
            shipment_id: Shipment ID
            truck_id: Optional specific truck ID (will auto-select if not provided)

        Returns:
            dict: Packing plan with utilization metrics
        """
        try:
            # Get shipment and items
            shipment = await self.db.get_shipment(shipment_id)
            if not shipment:
                return {"error": f"Shipment {shipment_id} not found"}

            items = await self.db.get_shipment_items(shipment_id)
            if not items:
                return {"error": f"No items found for shipment {shipment_id}"}

            # Get truck (auto-select if not provided)
            if not truck_id:
                available_trucks = await self.db.get_available_trucks()
                if not available_trucks:
                    return {"error": "No available trucks"}
                truck = available_trucks[0]  # Simple selection, can be improved
                truck_id = truck["id"]
            else:
                truck = await self.db.get_truck(truck_id)
                if not truck:
                    return {"error": f"Truck {truck_id} not found"}

            # Use DeepPack3D for real 3D bin packing
            # Reads method and lookahead from environment variables
            deeppack_service = get_deeppack_service(verbose=0)

            # Pack items using DeepPack3D
            packing_result = deeppack_service.pack_items(
                items=items,
                container_dimensions=(
                    truck["width"],
                    truck["height"],
                    truck["depth"]
                ),
                max_weight=truck.get("max_weight")
            )

            if not packing_result.get("success"):
                return {
                    "error": f"Packing failed: {packing_result.get('error', 'Unknown error')}",
                    "fallback": "mock"
                }

            # Extract results from DeepPack3D
            plan_data = {
                "placements": packing_result["placements"],
                "algorithm": packing_result["algorithm"],
                "container_dimensions": packing_result["container_dimensions"],
                "bins_used": packing_result["bins_used"]
            }

            utilization = packing_result["utilization"]
            computation_time_ms = packing_result["computation_time_ms"]

            # Save packing plan
            plan_id = f"PLAN-{str(uuid4())[:8].upper()}"
            await self.db.save_packing_plan(
                plan_id=plan_id,
                shipment_id=shipment_id,
                truck_id=truck_id,
                plan_data=plan_data,
                utilization=utilization,
                risk_score=0.0,  # Will be calculated by damage predictor
                algorithm_used=packing_result["algorithm"],
                computation_time_ms=computation_time_ms
            )

            # Publish result to Redpanda
            self.redpanda.publish_packing_result({
                "plan_id": plan_id,
                "shipment_id": shipment_id,
                "truck_id": truck_id,
                "utilization": utilization
            })

            # Update shipment status
            await self.db.update_shipment_status(shipment_id, "packed")

            logger.info(f"Optimized packing for shipment {shipment_id}")

            return {
                "success": True,
                "plan_id": plan_id,
                "truck_id": truck_id,
                "utilization": round(utilization, 2),
                "utilization_percentage": round(utilization, 2),
                "items_packed": len(items),
                "packing_method": packing_result["algorithm"],
                "placements": packing_result["placements"],
                "bins_used": packing_result["bins_used"],
                "computation_time_ms": computation_time_ms
            }

        except Exception as e:
            logger.error(f"Error optimizing packing: {e}")
            return {"error": str(e)}

    # Route Analysis Tools

    async def get_route_conditions(
        self,
        route_id: str,
        origin: str = None,
        destination: str = None
    ) -> Dict[str, Any]:
        """
        Get current route conditions (weather, traffic, road quality)

        Args:
            route_id: Route ID
            origin: Origin location (if route_id not in DB)
            destination: Destination location (if route_id not in DB)

        Returns:
            dict: Route conditions
        """
        try:
            # Get historical route analytics
            analytics = await self.db.get_route_analytics(route_id, limit=5)

            # Get real weather data
            weather_service = await get_weather_service()
            weather_data = await weather_service.get_route_weather(
                origin or "Los Angeles",
                destination or "New York"
            )

            # Get real traffic data (need coordinates)
            traffic_data = {"level": "medium", "delay_minutes": 0, "incidents": []}
            try:
                geocoding = await get_geocoding_service()
                origin_coords = await geocoding.get_coordinates(origin or "Los Angeles")
                dest_coords = await geocoding.get_coordinates(destination or "New York")

                if origin_coords and dest_coords:
                    traffic_service = await get_traffic_service()
                    traffic_data = await traffic_service.get_route_traffic(
                        origin_coords[0], origin_coords[1],
                        dest_coords[0], dest_coords[1]
                    )
            except Exception as e:
                logger.warning(f"Traffic data unavailable: {e}")

            # Calculate road quality score based on weather and traffic
            road_quality_score = 10.0
            if weather_data.get("severity", 1) > 3:
                road_quality_score -= 3.0
            if traffic_data.get("level") == "heavy":
                road_quality_score -= 2.0
            elif traffic_data.get("level") == "severe":
                road_quality_score -= 4.0

            conditions = {
                "route_id": route_id,
                "origin": origin or "Unknown",
                "destination": destination or "Unknown",
                "current_weather": weather_data.get("origin", {}).get("weather", {}),
                "destination_weather": weather_data.get("destination", {}).get("weather", {}),
                "weather_severity": weather_data.get("severity", 1),
                "weather_warnings": weather_data.get("warnings", []),
                "current_traffic": {
                    "level": traffic_data.get("level", "medium"),
                    "delay_minutes": traffic_data.get("delay_minutes", 0),
                    "incidents": traffic_data.get("incidents", []),
                    "warnings": traffic_data.get("warnings", [])
                },
                "road_quality": {
                    "score": road_quality_score,
                    "surface_condition": "excellent" if road_quality_score > 9 else "good" if road_quality_score > 7 else "fair" if road_quality_score > 5 else "poor"
                },
                "historical_analytics": analytics
            }

            # Save analytics to database
            await self.db.save_route_analytics(
                route_id=route_id,
                origin=origin or "Unknown",
                destination=destination or "Unknown",
                weather_condition=weather_data.get("origin", {}).get("weather", {}).get("condition", "unknown"),
                weather_severity=weather_data.get("severity", 1),
                traffic_level=traffic_data.get("level", "medium"),
                road_quality_score=road_quality_score
            )

            logger.info(f"Retrieved REAL route conditions for {route_id}")

            return conditions

        except Exception as e:
            logger.error(f"Error getting route conditions: {e}")
            return {"error": str(e)}

    # Damage Prediction Tools

    async def predict_damage_risk(
        self,
        shipment_id: str,
        route_id: str = None
    ) -> Dict[str, Any]:
        """
        Predict damage risk for shipment using Claude Haiku

        Args:
            shipment_id: Shipment ID
            route_id: Route ID (optional)

        Returns:
            dict: Risk prediction with contributing factors
        """
        try:
            # Get shipment data
            shipment = await self.db.get_shipment(shipment_id)
            if not shipment:
                return {"error": f"Shipment {shipment_id} not found"}

            # Get route conditions if route_id provided
            route_data = None
            if route_id:
                route_data = await self.get_route_conditions(
                    route_id,
                    origin=shipment["origin"],
                    destination=shipment["destination"]
                )

            # Get packing plan
            packing_plans = await self.db.get_shipment_packing_plans(shipment_id)
            packing_data = packing_plans[0] if packing_plans else None

            # Use Claude to analyze risk
            prediction = await self.claude.analyze_damage_risk(
                shipment_data=shipment,
                route_data=route_data or {},
                weather_data=route_data.get("current_weather") if route_data else None,
                packing_data=packing_data
            )

            # Save prediction
            await self.db.save_ai_prediction(
                shipment_id=shipment_id,
                prediction_type="damage_risk",
                prediction_data=prediction,
                model_version=self.claude.model,
                confidence=0.85
            )

            # Publish to Redpanda
            self.redpanda.publish_damage_prediction({
                "shipment_id": shipment_id,
                "risk_level": prediction.get("risk_level", "UNKNOWN"),
                "risk_score": prediction.get("risk_score", 0)
            })

            logger.info(f"Predicted damage risk for shipment {shipment_id}")

            return prediction

        except Exception as e:
            logger.error(f"Error predicting damage risk: {e}")
            return {"error": str(e)}

    # Event Publishing Tools

    async def publish_event(
        self,
        event_type: str,
        event_data: dict
    ) -> Dict[str, Any]:
        """
        Publish event to Redpanda

        Args:
            event_type: Type of event (shipment_request, packing_result, etc.)
            event_data: Event data payload

        Returns:
            dict: Success status
        """
        try:
            # Map event type to topic
            topic_map = {
                "shipment_request": redpanda.TOPICS["SHIPMENT_REQUESTS"],
                "packing_result": redpanda.TOPICS["PACKING_RESULTS"],
                "route_update": redpanda.TOPICS["ROUTE_UPDATES"],
                "weather_alert": redpanda.TOPICS["WEATHER_ALERTS"],
                "traffic_update": redpanda.TOPICS["TRAFFIC_UPDATES"],
                "damage_prediction": redpanda.TOPICS["DAMAGE_PREDICTIONS"],
                "notification": redpanda.TOPICS["NOTIFICATIONS"]
            }

            topic = topic_map.get(event_type)
            if not topic:
                return {"error": f"Unknown event type: {event_type}"}

            success = self.redpanda.publish(topic, event_data)

            return {
                "success": success,
                "event_type": event_type,
                "topic": topic
            }

        except Exception as e:
            logger.error(f"Error publishing event: {e}")
            return {"error": str(e)}

    # AI Analysis Tools

    async def analyze_shipment_with_ai(
        self,
        shipment_id: str
    ) -> Dict[str, Any]:
        """
        Analyze shipment using Claude Haiku for recommendations

        Args:
            shipment_id: Shipment ID

        Returns:
            dict: AI analysis with recommendations
        """
        try:
            shipment = await self.db.get_shipment(shipment_id)
            if not shipment:
                return {"error": f"Shipment {shipment_id} not found"}

            items = await self.db.get_shipment_items(shipment_id)

            # Use Claude to analyze
            analysis = await self.claude.analyze_shipment(shipment, items)

            # Save as AI prediction
            await self.db.save_ai_prediction(
                shipment_id=shipment_id,
                prediction_type="shipment_analysis",
                prediction_data=analysis,
                model_version=self.claude.model,
                confidence=0.90
            )

            logger.info(f"Analyzed shipment {shipment_id} with AI")

            return analysis

        except Exception as e:
            logger.error(f"Error analyzing shipment with AI: {e}")
            return {"error": str(e)}


# Global tools instance
tools = MCPTools()
