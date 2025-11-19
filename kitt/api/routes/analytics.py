"""
Analytics & Dashboard Routes
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime

from kitt_mcp.database import db
from kitt_mcp.graph_tools import graph_tools

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@router.get("/dashboard")
async def get_dashboard():
    """Complete dashboard statistics"""
    try:
        shipments = await db.get_all_shipments(limit=1000)
        network = await graph_tools.get_network_overview()

        stats = {
            "total_shipments": len(shipments),
            "network": network,
            "generated_at": datetime.now().isoformat(),
            "by_status": {},
            "by_priority": {}
        }

        # Group by status
        for s in shipments:
            status = s.get("status", "unknown")
            stats["by_status"][status] = stats["by_status"].get(status, 0) + 1

        # Group by priority
        for s in shipments:
            priority = s.get("priority", "unknown")
            stats["by_priority"][priority] = stats["by_priority"].get(priority, 0) + 1

        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/utilization")
async def get_utilization():
    """Packing utilization statistics"""
    try:
        plans = await db.get_all_packing_plans(limit=100)

        if not plans:
            return {
                "average_utilization": 0,
                "total_plans": 0,
                "plans": []
            }

        utilizations = [p.get("utilization", 0) for p in plans]

        return {
            "average_utilization": sum(utilizations) / len(utilizations),
            "min_utilization": min(utilizations),
            "max_utilization": max(utilizations),
            "total_plans": len(plans),
            "recent_plans": plans[:10]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/performance")
async def get_performance():
    """System performance metrics"""
    try:
        plans = await db.get_all_packing_plans(limit=50)

        computation_times = [
            p.get("computation_time_ms", 0)
            for p in plans
            if p.get("computation_time_ms")
        ]

        return {
            "total_optimizations": len(plans),
            "avg_computation_time_ms": sum(computation_times) / len(computation_times) if computation_times else 0,
            "min_computation_time_ms": min(computation_times) if computation_times else 0,
            "max_computation_time_ms": max(computation_times) if computation_times else 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
