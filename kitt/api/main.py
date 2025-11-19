from fastapi import FastAPI, WebSocket, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import asyncio

from config.settings import settings
from api.websockets import (
    handle_freight_websocket,
    handle_packing_websocket,
    handle_notifications_websocket,
    manager
)
from api.routes import shipments, optimization, graph, analytics, agent
from kitt_mcp.database import db
from services.neo4j_service import get_neo4j_service

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.DEBUG else logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="KITT - AI Freight Optimizer",
    description="Real-time freight loading optimization with AI-powered route intelligence",
    version="1.0.0",
    debug=settings.DEBUG
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(shipments.router)
app.include_router(optimization.router)
app.include_router(graph.router)
app.include_router(analytics.router)
app.include_router(agent.router)


@app.on_event("startup")
async def startup_event():
    """Application startup tasks"""
    logger.info("🚀 Starting KITT Freight Optimizer API")
    logger.info(f"Debug mode: {settings.DEBUG}")
    logger.info(f"Redpanda: {settings.REDPANDA_BOOTSTRAP_SERVERS}")

    # Initialize Database
    try:
        await db.initialize_schema()
        logger.info("✅ Database initialized")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")

    # Test Neo4j connection
    try:
        neo4j = await get_neo4j_service()
        stats = await neo4j.get_network_stats()
        logger.info(f"✅ Neo4j connected - Network: {stats}")
    except Exception as e:
        logger.error(f"❌ Neo4j connection failed: {e}")

    # Start heartbeat checker
    asyncio.create_task(manager.heartbeat_check(interval=30))
    logger.info("✅ Heartbeat checker started")
    logger.info("✅ API ready - Docs at http://localhost:8000/docs")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown tasks"""
    logger.info("🛑 Shutting down KITT Freight Optimizer API")


@app.get("/")
async def root():
    """Root endpoint - API health check"""
    return {
        "name": "KITT Freight Optimizer",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "websocket": {
                "freight": "/ws/freight",
                "packing": "/ws/packing",
                "notifications": "/ws/notifications"
            },
            "rest": {
                "health": "/health",
                "stats": "/stats"
            }
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "connections": {
            "freight": manager.get_connection_count("freight"),
            "packing": manager.get_connection_count("packing"),
            "notifications": manager.get_connection_count("notifications"),
            "total": manager.get_connection_count()
        }
    }


@app.get("/stats")
async def get_stats():
    """Get WebSocket connection statistics"""
    return {
        "total_connections": manager.get_connection_count(),
        "connections_by_endpoint": {
            "freight": manager.get_connection_count("freight"),
            "packing": manager.get_connection_count("packing"),
            "notifications": manager.get_connection_count("notifications")
        },
        "connection_details": [
            {
                "endpoint": metadata["endpoint"],
                "client_id": metadata["client_id"],
                "connected_at": metadata["connected_at"].isoformat(),
                "last_heartbeat": metadata["last_heartbeat"].isoformat()
            }
            for metadata in manager.connection_metadata.values()
        ]
    }


@app.websocket("/ws/freight")
async def freight_websocket_endpoint(
    websocket: WebSocket,
    client_id: str = Query(default="unknown")
):
    """
    WebSocket endpoint for real-time freight data

    Usage:
        ws://localhost:8000/ws/freight?client_id=client-123

    Message Types:
        - shipment_request
        - route_update
        - heartbeat
    """
    await handle_freight_websocket(websocket, client_id)


@app.websocket("/ws/packing")
async def packing_websocket_endpoint(
    websocket: WebSocket,
    client_id: str = Query(default="unknown")
):
    """
    WebSocket endpoint for packing optimization updates

    Usage:
        ws://localhost:8000/ws/packing?client_id=client-123

    Message Types:
        - packing_result
        - damage_prediction
        - heartbeat
    """
    await handle_packing_websocket(websocket, client_id)


@app.websocket("/ws/notifications")
async def notifications_websocket_endpoint(
    websocket: WebSocket,
    client_id: str = Query(default="unknown")
):
    """
    WebSocket endpoint for system notifications

    Usage:
        ws://localhost:8000/ws/notifications?client_id=client-123

    Message Types:
        - notification
        - weather_alert
        - traffic_update
        - error
        - heartbeat
    """
    await handle_notifications_websocket(websocket, client_id)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api.main:app",
        host=settings.FASTAPI_HOST,
        port=settings.FASTAPI_PORT,
        reload=settings.DEBUG,
        log_level="info" if settings.DEBUG else "warning"
    )
