"""
Optimization & Packing Routes
"""

from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from kitt_mcp.tools import MCPTools
from kitt_mcp.graph_tools import graph_tools
from kitt_mcp.database import db

router = APIRouter(prefix="/api", tags=["Optimization"])
tools = MCPTools()


class OptimizeRequest(BaseModel):
    shipment_id: str
    truck_id: Optional[str] = None
    include_ai_analysis: bool = True
    store_in_graph: bool = True


@router.post("/optimize")
async def optimize_shipment(request: OptimizeRequest):
    """
    Full autonomous optimization workflow:
    1. 3D bin packing (DeepPack3D + TensorFlow)
    2. Route conditions (real weather + traffic APIs)
    3. AI damage risk prediction
    4. AI shipment analysis
    5. Knowledge graph storage
    """
    try:
        shipment_id = request.shipment_id
        results = {
            "shipment_id": shipment_id,
            "optimized_at": datetime.now().isoformat()
        }

        # Step 1: Get shipment data
        shipment_data = await tools.get_shipment_data(shipment_id)
        if "error" in shipment_data:
            raise HTTPException(status_code=404, detail=shipment_data["error"])

        # Step 2: 3D Packing Optimization
        packing = await tools.optimize_packing(shipment_id, request.truck_id)
        if "error" in packing:
            raise HTTPException(status_code=400, detail=packing["error"])
        results["packing"] = packing

        # Step 3: Route Conditions (Real Weather + Traffic)
        route_conditions = await tools.get_route_conditions(
            route_id=f"ROUTE-{shipment_id}",
            origin=shipment_data.get("origin"),
            destination=shipment_data.get("destination")
        )
        results["route_conditions"] = route_conditions

        # Step 4: Damage Risk Prediction
        risk = await tools.predict_damage_risk(shipment_id, f"ROUTE-{shipment_id}")
        results["risk_assessment"] = risk

        # Step 5: AI Analysis
        if request.include_ai_analysis:
            ai_analysis = await tools.analyze_shipment_with_ai(shipment_id)
            results["ai_analysis"] = ai_analysis

        # Step 6: Store in Knowledge Graph
        if request.store_in_graph:
            try:
                items = await db.get_shipment_items(shipment_id)
                graph_result = await graph_tools.store_shipment_in_graph(
                    shipment_id=shipment_id,
                    origin=shipment_data.get("origin"),
                    destination=shipment_data.get("destination"),
                    items=[dict(item) for item in items],
                    status=shipment_data.get("status", "packed"),
                    priority=shipment_data.get("priority", "medium")
                )
                results["graph_storage"] = graph_result
            except Exception as graph_error:
                # If shipment already exists in graph, just note it
                results["graph_storage"] = {"status": "already_exists", "error": str(graph_error)}

        # Summary
        results["summary"] = {
            "utilization": packing.get("utilization_percentage", 0),
            "risk_level": risk.get("risk_level", "UNKNOWN"),
            "weather_severity": route_conditions.get("weather_severity", 0),
            "traffic_level": route_conditions.get("current_traffic", {}).get("level", "unknown"),
            "ready_for_dispatch": True
        }

        return results
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/packing/{shipment_id}")
async def pack_shipment(shipment_id: str, truck_id: Optional[str] = Body(None)):
    """Run 3D bin packing optimization (DeepPack3D)"""
    try:
        result = await tools.optimize_packing(shipment_id, truck_id)
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/route-conditions")
async def get_route_conditions(
    origin: str = Query(..., min_length=1),
    destination: str = Query(..., min_length=1)
):
    """
    Get route conditions with REAL APIs:
    - OpenWeatherMap for weather
    - TomTom for traffic
    - Calculated road quality
    """
    try:
        result = await tools.get_route_conditions(
            route_id=f"ROUTE-{origin}-{destination}",
            origin=origin,
            destination=destination
        )
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/risk/{shipment_id}")
async def predict_risk(shipment_id: str):
    """Predict damage risk with AI"""
    try:
        result = await tools.predict_damage_risk(shipment_id)
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze/{shipment_id}")
async def analyze_shipment(shipment_id: str):
    """AI-powered shipment analysis (Claude API)"""
    try:
        result = await tools.analyze_shipment_with_ai(shipment_id)
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
