"""
Knowledge Graph Routes
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, Dict, Any

from kitt_mcp.graph_tools import graph_tools

router = APIRouter(prefix="/api/graph", tags=["Knowledge Graph"])


class CypherQuery(BaseModel):
    query: str
    parameters: Optional[Dict[str, Any]] = {}


@router.get("/shipment/{shipment_id}")
async def get_shipment_graph(shipment_id: str):
    """Get complete knowledge graph view of shipment"""
    try:
        return await graph_tools.get_shipment_knowledge_graph(shipment_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/location/{location_name}")
async def get_location_analytics(location_name: str):
    """Get analytics for a location"""
    try:
        return await graph_tools.get_location_analytics(location_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/patterns")
async def get_patterns(
    origin: str = Query(...),
    destination: str = Query(...)
):
    """Find historical shipment patterns"""
    try:
        result = await graph_tools.find_historical_patterns(origin, destination)
        return {"origin": origin, "destination": destination, "patterns": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/network")
async def get_network():
    """Get network overview"""
    try:
        return await graph_tools.get_network_overview()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trucks/optimal")
async def find_optimal_trucks(
    weight: float = Query(..., gt=0),
    volume: float = Query(..., gt=0),
    origin: str = Query(...)
):
    """Find optimal trucks from knowledge graph"""
    try:
        result = await graph_tools.find_optimal_trucks(weight, volume, origin)
        return {"trucks": result, "count": len(result)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query")
async def execute_cypher(query: CypherQuery):
    """Execute custom Cypher query"""
    try:
        result = await graph_tools.query_graph_with_cypher(query.query, query.parameters)
        return {"query": query.query, "results": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
