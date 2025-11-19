from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Set
import json
import asyncio
from datetime import datetime
import logging

from models.messages import WebSocketMessage, ErrorMessage

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections for KITT"""

    def __init__(self):
        # Active connections by endpoint
        self.active_connections: Dict[str, Set[WebSocket]] = {
            "freight": set(),
            "packing": set(),
            "notifications": set()
        }
        # Connection metadata
        self.connection_metadata: Dict[WebSocket, dict] = {}

    async def connect(self, websocket: WebSocket, endpoint: str, client_id: str = None):
        """Accept new WebSocket connection"""
        await websocket.accept()
        self.active_connections[endpoint].add(websocket)
        self.connection_metadata[websocket] = {
            "endpoint": endpoint,
            "client_id": client_id,
            "connected_at": datetime.utcnow(),
            "last_heartbeat": datetime.utcnow()
        }
        logger.info(f"Client {client_id} connected to {endpoint} endpoint. "
                   f"Total connections: {len(self.active_connections[endpoint])}")

    def disconnect(self, websocket: WebSocket, endpoint: str):
        """Remove WebSocket connection"""
        if websocket in self.active_connections[endpoint]:
            self.active_connections[endpoint].remove(websocket)
        if websocket in self.connection_metadata:
            client_id = self.connection_metadata[websocket].get("client_id")
            del self.connection_metadata[websocket]
            logger.info(f"Client {client_id} disconnected from {endpoint} endpoint. "
                       f"Total connections: {len(self.active_connections[endpoint])}")

    async def send_message(self, message: WebSocketMessage, websocket: WebSocket):
        """Send message to specific WebSocket"""
        try:
            await websocket.send_text(message.model_dump_json())
        except Exception as e:
            logger.error(f"Error sending message to websocket: {e}")

    async def broadcast(self, message: WebSocketMessage, endpoint: str):
        """Broadcast message to all connections on an endpoint"""
        disconnected = []
        for connection in self.active_connections[endpoint]:
            try:
                await connection.send_text(message.model_dump_json())
            except Exception as e:
                logger.error(f"Error broadcasting to connection: {e}")
                disconnected.append(connection)

        # Clean up disconnected connections
        for conn in disconnected:
            self.disconnect(conn, endpoint)

    async def send_error(self, websocket: WebSocket, error_code: str, error_message: str):
        """Send error message to WebSocket"""
        error = WebSocketMessage(
            type="error",
            payload=ErrorMessage(
                error_code=error_code,
                error_message=error_message
            ).model_dump()
        )
        await self.send_message(error, websocket)

    def get_connection_count(self, endpoint: str = None) -> int:
        """Get number of active connections"""
        if endpoint:
            return len(self.active_connections.get(endpoint, set()))
        return sum(len(conns) for conns in self.active_connections.values())

    async def heartbeat_check(self, interval: int = 30):
        """Periodic heartbeat check for stale connections"""
        while True:
            await asyncio.sleep(interval)
            now = datetime.utcnow()
            stale_connections = []

            for websocket, metadata in self.connection_metadata.items():
                last_heartbeat = metadata.get("last_heartbeat")
                if (now - last_heartbeat).total_seconds() > interval * 2:
                    stale_connections.append((websocket, metadata["endpoint"]))

            for websocket, endpoint in stale_connections:
                logger.warning(f"Removing stale connection from {endpoint}")
                self.disconnect(websocket, endpoint)


# Global connection manager instance
manager = ConnectionManager()


async def handle_freight_websocket(websocket: WebSocket, client_id: str = "unknown"):
    """Handle freight WebSocket connections"""
    await manager.connect(websocket, "freight", client_id)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                # Parse incoming message
                message_data = json.loads(data)
                message = WebSocketMessage(**message_data)

                # Update heartbeat
                if message.type == "heartbeat":
                    manager.connection_metadata[websocket]["last_heartbeat"] = datetime.utcnow()
                    await manager.send_message(
                        WebSocketMessage(type="heartbeat", payload={"status": "ok"}),
                        websocket
                    )
                    continue

                # Echo message back for now (will be replaced with actual processing)
                logger.info(f"Received {message.type} from {client_id}: {message.correlation_id}")

                # Broadcast to all freight connections
                await manager.broadcast(message, "freight")

            except json.JSONDecodeError:
                await manager.send_error(websocket, "INVALID_JSON", "Invalid JSON format")
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                await manager.send_error(websocket, "PROCESSING_ERROR", str(e))

    except WebSocketDisconnect:
        manager.disconnect(websocket, "freight")
        logger.info(f"Client {client_id} disconnected from freight endpoint")


async def handle_packing_websocket(websocket: WebSocket, client_id: str = "unknown"):
    """Handle packing WebSocket connections"""
    await manager.connect(websocket, "packing", client_id)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message_data = json.loads(data)
                message = WebSocketMessage(**message_data)

                # Update heartbeat
                if message.type == "heartbeat":
                    manager.connection_metadata[websocket]["last_heartbeat"] = datetime.utcnow()
                    await manager.send_message(
                        WebSocketMessage(type="heartbeat", payload={"status": "ok"}),
                        websocket
                    )
                    continue

                logger.info(f"Received {message.type} from {client_id}: {message.correlation_id}")
                await manager.broadcast(message, "packing")

            except json.JSONDecodeError:
                await manager.send_error(websocket, "INVALID_JSON", "Invalid JSON format")
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                await manager.send_error(websocket, "PROCESSING_ERROR", str(e))

    except WebSocketDisconnect:
        manager.disconnect(websocket, "packing")
        logger.info(f"Client {client_id} disconnected from packing endpoint")


async def handle_notifications_websocket(websocket: WebSocket, client_id: str = "unknown"):
    """Handle notifications WebSocket connections"""
    await manager.connect(websocket, "notifications", client_id)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message_data = json.loads(data)
                message = WebSocketMessage(**message_data)

                # Update heartbeat
                if message.type == "heartbeat":
                    manager.connection_metadata[websocket]["last_heartbeat"] = datetime.utcnow()
                    await manager.send_message(
                        WebSocketMessage(type="heartbeat", payload={"status": "ok"}),
                        websocket
                    )
                    continue

                logger.info(f"Received {message.type} from {client_id}: {message.correlation_id}")
                await manager.broadcast(message, "notifications")

            except json.JSONDecodeError:
                await manager.send_error(websocket, "INVALID_JSON", "Invalid JSON format")
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                await manager.send_error(websocket, "PROCESSING_ERROR", str(e))

    except WebSocketDisconnect:
        manager.disconnect(websocket, "notifications")
        logger.info(f"Client {client_id} disconnected from notifications endpoint")
