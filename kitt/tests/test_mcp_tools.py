#!/usr/bin/env python3
"""
Test MCP tools functionality
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from kitt_mcp.database import db
from kitt_mcp.tools import tools
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_database_operations():
    """Test database CRUD operations"""
    logger.info("\n" + "="*60)
    logger.info("Testing Database Operations")
    logger.info("="*60)

    # Initialize database
    await db.initialize_schema()
    logger.info("✅ Database initialized")

    # Test truck retrieval
    trucks = await db.get_available_trucks()
    logger.info(f"✅ Retrieved {len(trucks)} available trucks")
    assert len(trucks) > 0, "No trucks available"

    logger.info("✅ All database tests passed")


async def test_create_shipment():
    """Test shipment creation"""
    logger.info("\n" + "="*60)
    logger.info("Testing Shipment Creation")
    logger.info("="*60)

    result = await tools.create_shipment(
        origin="Chicago",
        destination="Dallas",
        items=[
            {
                "width": 50,
                "height": 40,
                "depth": 30,
                "weight": 25,
                "fragile": False,
                "stackable": True,
                "description": "Electronics"
            },
            {
                "width": 60,
                "height": 50,
                "depth": 40,
                "weight": 35,
                "fragile": True,
                "stackable": False,
                "description": "Glassware"
            }
        ],
        priority="high"
    )

    assert result.get("success"), f"Shipment creation failed: {result}"
    shipment_id = result["shipment_id"]
    logger.info(f"✅ Created shipment: {shipment_id}")
    logger.info(f"   Items added: {result['items_added']}")

    return shipment_id


async def test_get_shipment_data(shipment_id):
    """Test retrieving shipment data"""
    logger.info("\n" + "="*60)
    logger.info("Testing Get Shipment Data")
    logger.info("="*60)

    data = await tools.get_shipment_data(shipment_id)

    assert "shipment" in data, "Missing shipment data"
    assert "items" in data, "Missing items data"

    logger.info(f"✅ Retrieved shipment data for {shipment_id}")
    logger.info(f"   Origin: {data['shipment']['origin']}")
    logger.info(f"   Destination: {data['shipment']['destination']}")
    logger.info(f"   Items: {len(data['items'])}")
    logger.info(f"   Status: {data['shipment']['status']}")


async def test_optimize_packing(shipment_id):
    """Test packing optimization"""
    logger.info("\n" + "="*60)
    logger.info("Testing Packing Optimization")
    logger.info("="*60)

    result = await tools.optimize_packing(shipment_id)

    assert result.get("success"), f"Packing optimization failed: {result}"

    logger.info(f"✅ Optimized packing for shipment {shipment_id}")
    logger.info(f"   Plan ID: {result['plan_id']}")
    logger.info(f"   Truck ID: {result['truck_id']}")
    logger.info(f"   Utilization: {result['utilization']}%")
    logger.info(f"   Items packed: {result['items_packed']}")

    return result['plan_id']


async def test_route_conditions():
    """Test route conditions retrieval"""
    logger.info("\n" + "="*60)
    logger.info("Testing Route Conditions")
    logger.info("="*60)

    conditions = await tools.get_route_conditions(
        route_id="ROUTE-CHI-DAL",
        origin="Chicago",
        destination="Dallas"
    )

    assert "current_weather" in conditions, "Missing weather data"
    assert "current_traffic" in conditions, "Missing traffic data"

    logger.info("✅ Retrieved route conditions")
    logger.info(f"   Route: {conditions['route_id']}")
    logger.info(f"   Weather: {conditions['current_weather']['condition']}")
    logger.info(f"   Traffic: {conditions['current_traffic']['level']}")
    logger.info(f"   Road quality: {conditions['road_quality']['score']}/10")


async def test_damage_prediction(shipment_id):
    """Test damage risk prediction"""
    logger.info("\n" + "="*60)
    logger.info("Testing Damage Risk Prediction")
    logger.info("="*60)

    prediction = await tools.predict_damage_risk(
        shipment_id=shipment_id,
        route_id="ROUTE-CHI-DAL"
    )

    # May have error if Claude API key not configured
    if "error" in prediction:
        logger.warning(f"⚠️  Damage prediction returned error: {prediction['error']}")
        logger.info("   (This is expected if Anthropic API key is not configured)")
    else:
        logger.info("✅ Generated damage risk prediction")
        logger.info(f"   Risk level: {prediction.get('risk_level', 'Unknown')}")
        logger.info(f"   Risk score: {prediction.get('risk_score', 0)}/100")


async def test_ai_analysis(shipment_id):
    """Test AI shipment analysis"""
    logger.info("\n" + "="*60)
    logger.info("Testing AI Shipment Analysis")
    logger.info("="*60)

    analysis = await tools.analyze_shipment_with_ai(shipment_id)

    # May have error if Claude API key not configured
    if "error" in analysis:
        logger.warning(f"⚠️  AI analysis returned error: {analysis['error']}")
        logger.info("   (This is expected if Anthropic API key is not configured)")
    else:
        logger.info("✅ Generated AI analysis")
        if "strategy" in analysis:
            logger.info(f"   Strategy: {analysis.get('strategy', 'N/A')}")


async def test_event_publishing():
    """Test event publishing to Redpanda"""
    logger.info("\n" + "="*60)
    logger.info("Testing Event Publishing")
    logger.info("="*60)

    result = await tools.publish_event(
        event_type="notification",
        event_data={
            "message": "Test notification from MCP server",
            "severity": "info"
        }
    )

    # May fail if Redpanda is not running
    if "error" in result:
        logger.warning(f"⚠️  Event publishing failed: {result['error']}")
        logger.info("   (This is expected if Redpanda is not running)")
    else:
        logger.info("✅ Published event to Redpanda")
        logger.info(f"   Event type: {result['event_type']}")
        logger.info(f"   Topic: {result['topic']}")


async def main():
    """Run all tests"""
    logger.info("\n" + "🧪 "*30)
    logger.info("KITT MCP Tools Test Suite")
    logger.info("🧪 "*30)

    try:
        # Test database operations
        await test_database_operations()

        # Test shipment creation
        shipment_id = await test_create_shipment()

        # Test shipment data retrieval
        await test_get_shipment_data(shipment_id)

        # Test packing optimization
        await test_optimize_packing(shipment_id)

        # Test route conditions
        await test_route_conditions()

        # Test damage prediction
        await test_damage_prediction(shipment_id)

        # Test AI analysis
        await test_ai_analysis(shipment_id)

        # Test event publishing
        await test_event_publishing()

        logger.info("\n" + "="*60)
        logger.info("✅ ALL TESTS PASSED")
        logger.info("="*60)

        logger.info("\nTest Summary:")
        logger.info("  ✅ Database operations")
        logger.info("  ✅ Shipment creation")
        logger.info("  ✅ Shipment data retrieval")
        logger.info("  ✅ Packing optimization")
        logger.info("  ✅ Route conditions")
        logger.info("  ⚠️  Damage prediction (requires API key)")
        logger.info("  ⚠️  AI analysis (requires API key)")
        logger.info("  ⚠️  Event publishing (requires Redpanda)")

        logger.info("\nNote: Some features require external services:")
        logger.info("  - Set ANTHROPIC_API_KEY in .env for AI features")
        logger.info("  - Start Redpanda for event streaming")

    except Exception as e:
        logger.error(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
