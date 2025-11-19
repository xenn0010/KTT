from pydantic import BaseModel, Field
from typing import Any, Literal
from datetime import datetime
from uuid import uuid4


class WebSocketMessage(BaseModel):
    """Base WebSocket message protocol"""

    type: Literal[
        "shipment_request",
        "packing_result",
        "route_update",
        "weather_alert",
        "traffic_update",
        "damage_prediction",
        "notification",
        "error",
        "heartbeat"
    ]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    payload: dict[str, Any]
    correlation_id: str = Field(default_factory=lambda: str(uuid4()))

    class Config:
        json_schema_extra = {
            "example": {
                "type": "shipment_request",
                "timestamp": "2025-01-19T10:30:00Z",
                "payload": {
                    "shipment_id": "SH-001",
                    "items": [
                        {"width": 50, "height": 40, "depth": 30, "weight": 25}
                    ]
                },
                "correlation_id": "550e8400-e29b-41d4-a716-446655440000"
            }
        }


class ShipmentRequest(BaseModel):
    """Shipment request payload"""

    shipment_id: str
    origin: str
    destination: str
    items: list[dict[str, Any]]
    priority: Literal["low", "medium", "high", "critical"] = "medium"
    deadline: datetime | None = None


class PackingResult(BaseModel):
    """Packing optimization result payload"""

    shipment_id: str
    truck_id: str
    placements: list[dict[str, Any]]
    utilization: float
    risk_score: float
    bins_used: int


class RouteUpdate(BaseModel):
    """Route condition update payload"""

    route_id: str
    weather_condition: str
    weather_severity: int = Field(ge=1, le=5)
    traffic_level: Literal["low", "medium", "high", "severe"]
    estimated_delay_minutes: int


class WeatherAlert(BaseModel):
    """Weather alert payload"""

    route_id: str
    alert_type: Literal["rain", "snow", "wind", "fog", "storm"]
    severity: int = Field(ge=1, le=5)
    description: str
    valid_until: datetime


class DamagePrediction(BaseModel):
    """Damage risk prediction payload"""

    shipment_id: str
    risk_score: float = Field(ge=0, le=100)
    risk_level: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    contributing_factors: list[dict[str, float]]
    recommendations: list[str]


class Notification(BaseModel):
    """System notification payload"""

    message: str
    severity: Literal["info", "warning", "error", "critical"]
    details: dict[str, Any] | None = None


class ErrorMessage(BaseModel):
    """Error message payload"""

    error_code: str
    error_message: str
    details: dict[str, Any] | None = None
