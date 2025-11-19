"""
Shipment Management Routes
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from kitt_mcp.tools import MCPTools
from kitt_mcp.database import db

router = APIRouter(prefix="/api/shipments", tags=["Shipments"])
tools = MCPTools()


class ItemCreate(BaseModel):
    width: float = Field(..., gt=0)
    height: float = Field(..., gt=0)
    depth: float = Field(..., gt=0)
    weight: float = Field(..., gt=0)
    fragile: bool = False
    stackable: bool = True
    description: Optional[str] = None


class ShipmentCreate(BaseModel):
    origin: str = Field(..., min_length=1)
    destination: str = Field(..., min_length=1)
    items: List[ItemCreate] = Field(..., min_items=1)
    priority: str = Field(default="medium", pattern="^(low|medium|high|critical)$")
    deadline: Optional[str] = None


@router.post("", status_code=201)
async def create_shipment(shipment: ShipmentCreate):
    """Create a new shipment with items"""
    try:
        items_data = [item.dict() for item in shipment.items]

        result = await tools.create_shipment(
            origin=shipment.origin,
            destination=shipment.destination,
            items=items_data,
            priority=shipment.priority,
            deadline=shipment.deadline
        )

        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{shipment_id}")
async def get_shipment(shipment_id: str):
    """Get shipment by ID with all details"""
    try:
        result = await tools.get_shipment_data(shipment_id)

        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("")
async def list_shipments(
    status: Optional[str] = Query(None, pattern="^(pending|packed|in_transit|delivered|cancelled)$"),
    priority: Optional[str] = Query(None, pattern="^(low|medium|high|critical)$"),
    limit: int = Query(100, ge=1, le=1000)
):
    """List all shipments with optional filters"""
    try:
        shipments = await db.get_all_shipments(limit=limit)

        if status:
            shipments = [s for s in shipments if s.get("status") == status]
        if priority:
            shipments = [s for s in shipments if s.get("priority") == priority]

        return {
            "count": len(shipments),
            "shipments": shipments
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{shipment_id}/items")
async def get_shipment_items(shipment_id: str):
    """Get all items for a shipment"""
    try:
        items = await db.get_shipment_items(shipment_id)
        return {"shipment_id": shipment_id, "count": len(items), "items": items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{shipment_id}")
async def delete_shipment(shipment_id: str):
    """Delete a shipment"""
    try:
        # Delete from graph
        from services.neo4j_service import get_neo4j_service
        neo4j = await get_neo4j_service()
        await neo4j.query_graph_with_cypher(
            "MATCH (s:Shipment {id: $id}) DETACH DELETE s",
            {"id": shipment_id}
        )

        # Delete from DB
        await db.delete_shipment(shipment_id)

        return {"success": True, "shipment_id": shipment_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
