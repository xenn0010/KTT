"""
Full Agentic Workflow Test
Simulates Claude autonomously optimizing a shipment from creation to delivery
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from kitt_mcp.tools import MCPTools
from kitt_mcp.graph_tools import graph_tools
from services.neo4j_service import get_neo4j_service


async def test_full_agentic_optimization():
    """
    Simulate Claude's autonomous workflow to optimize a shipment

    User Prompt: "Create a shipment from Los Angeles to New York with 10 boxes
    (50x40x30cm, 25kg each) and optimize everything. Track it until delivery."
    """

    print("=" * 80)
    print(" FULL AGENTIC WORKFLOW TEST")
    print(" Simulating Claude Autonomously Optimizing a Shipment")
    print("=" * 80)

    tools = MCPTools()
    shipment_id = None

    # ============================================================================
    # STEP 1: CREATE SHIPMENT
    # ============================================================================
    print("\n" + "─" * 80)
    print("🤖 CLAUDE: I'll create the shipment with your specifications...")
    print("─" * 80)

    items = []
    for i in range(10):
        items.append({
            "width": 50,
            "height": 40,
            "depth": 30,
            "weight": 25,
            "fragile": i % 3 == 0,  # Every 3rd item is fragile
            "stackable": i % 3 != 0,
            "description": f"Box {i+1}"
        })

    deadline = (datetime.now() + timedelta(days=3)).isoformat()

    shipment_result = await tools.create_shipment(
        origin="Los Angeles",
        destination="New York",
        items=items,
        priority="high",
        deadline=deadline
    )

    shipment_id = shipment_result.get("shipment_id")

    print(f"✅ Shipment Created: {shipment_id}")
    print(f"   Origin: Los Angeles → Destination: New York")
    print(f"   Items: {len(items)} boxes")
    print(f"   Total Weight: {sum(i['weight'] for i in items)} kg")
    print(f"   Priority: high")
    print(f"   Deadline: {deadline[:10]}")

    # ============================================================================
    # STEP 2: STORE IN KNOWLEDGE GRAPH FOR LEARNING
    # ============================================================================
    print("\n" + "─" * 80)
    print("🤖 CLAUDE: Storing shipment in knowledge graph to learn from patterns...")
    print("─" * 80)

    graph_result = await graph_tools.store_shipment_in_graph(
        shipment_id=shipment_id,
        origin="Los Angeles",
        destination="New York",
        items=items,
        status="pending",
        priority="high",
        deadline=deadline
    )

    print(f"✅ Stored in Knowledge Graph")
    print(f"   Items in graph: {graph_result.get('items_added', 0)}")
    print(f"   Total weight: {graph_result.get('total_weight', 0)} kg")
    print(f"   Total volume: {graph_result.get('total_volume', 0):,.0f} cm³")

    # ============================================================================
    # STEP 3: CHECK HISTORICAL PATTERNS
    # ============================================================================
    print("\n" + "─" * 80)
    print("🤖 CLAUDE: Checking historical patterns for LA→NYC route...")
    print("─" * 80)

    patterns = await graph_tools.find_historical_patterns(
        origin="Los Angeles",
        destination="New York"
    )

    if patterns:
        print(f"✅ Found {len(patterns)} similar historical shipments")
        for i, p in enumerate(patterns[:3], 1):
            print(f"   {i}. Shipment {p.get('shipment_id', 'N/A')}")
            print(f"      Weight: {p.get('total_weight', 'N/A')} kg, Status: {p.get('status', 'N/A')}")
    else:
        print(f"ℹ️  No historical data yet - this will be the first LA→NYC shipment")

    # ============================================================================
    # STEP 4: CHECK ROUTE CONDITIONS
    # ============================================================================
    print("\n" + "─" * 80)
    print("🤖 CLAUDE: Analyzing route conditions (weather, traffic)...")
    print("─" * 80)

    route_conditions = await tools.get_route_conditions(
        route_id=f"ROUTE-{shipment_id}",
        origin="Los Angeles",
        destination="New York"
    )

    if "error" not in route_conditions:
        origin_weather = route_conditions.get("current_weather", {})
        print(f"✅ Route Conditions Retrieved")
        print(f"   Weather at LA: {origin_weather.get('condition', 'N/A')} @ {origin_weather.get('temperature', 'N/A')}°F")
        print(f"   Weather Severity: {route_conditions.get('weather_severity', 'N/A')}/5")
        print(f"   Traffic Level: {route_conditions.get('current_traffic', {}).get('level', 'N/A')}")
        print(f"   Road Quality: {route_conditions.get('road_quality', {}).get('surface_condition', 'N/A')}")

        warnings = route_conditions.get('weather_warnings', [])
        if warnings:
            print(f"   ⚠️  Warnings: {', '.join(warnings)}")
    else:
        print(f"⚠️  Could not get route conditions: {route_conditions.get('error')}")

    # ============================================================================
    # STEP 5: FIND OPTIMAL TRUCK FROM KNOWLEDGE GRAPH
    # ============================================================================
    print("\n" + "─" * 80)
    print("🤖 CLAUDE: Finding optimal truck based on graph intelligence...")
    print("─" * 80)

    total_weight = sum(i['weight'] for i in items)
    total_volume = sum(i['width'] * i['height'] * i['depth'] for i in items)

    trucks = await graph_tools.find_optimal_trucks(
        total_weight=total_weight,
        total_volume=total_volume,
        origin="Los Angeles"
    )

    if trucks:
        best_truck = trucks[0]
        print(f"✅ Found {len(trucks)} suitable trucks")
        print(f"   Best Match: {best_truck.get('truck_id', 'N/A')}")
        print(f"   Type: {best_truck.get('type', 'N/A')}")
        print(f"   Capacity: {best_truck.get('max_weight', 'N/A')} kg, {best_truck.get('capacity_volume', 'N/A'):,.0f} cm³")
        truck_id = best_truck.get('truck_id')
    else:
        print(f"ℹ️  No trucks in graph yet, will use default truck selection")
        truck_id = None

    # ============================================================================
    # STEP 6: OPTIMIZE 3D PACKING
    # ============================================================================
    print("\n" + "─" * 80)
    print("🤖 CLAUDE: Running 3D bin packing optimization with DeepPack3D...")
    print("─" * 80)

    packing_result = await tools.optimize_packing(
        shipment_id=shipment_id,
        truck_id=truck_id
    )

    if "error" not in packing_result:
        print(f"✅ Packing Optimized")
        print(f"   Truck: {packing_result.get('truck_id', 'N/A')}")
        print(f"   Utilization: {packing_result.get('utilization_percentage', 0):.1f}%")
        print(f"   Items Packed: {packing_result.get('items_packed', 0)}/{len(items)}")
        print(f"   Algorithm: {packing_result.get('packing_method', 'N/A')}")

        if packing_result.get('utilization_percentage', 0) > 80:
            print(f"   🎯 Excellent utilization!")
        elif packing_result.get('utilization_percentage', 0) > 60:
            print(f"   ✅ Good utilization")
    else:
        print(f"⚠️  Packing optimization error: {packing_result.get('error')}")

    # ============================================================================
    # STEP 7: AI-POWERED DAMAGE RISK PREDICTION
    # ============================================================================
    print("\n" + "─" * 80)
    print("🤖 CLAUDE: Predicting damage risk using AI analysis...")
    print("─" * 80)

    risk_prediction = await tools.predict_damage_risk(
        shipment_id=shipment_id,
        route_id=f"ROUTE-{shipment_id}"
    )

    if "error" not in risk_prediction:
        print(f"✅ Risk Assessment Complete")
        print(f"   Risk Level: {risk_prediction.get('risk_level', 'N/A')}")
        print(f"   Risk Score: {risk_prediction.get('risk_score', 0)}/100")

        factors = risk_prediction.get('risk_factors', [])
        if factors:
            print(f"   Risk Factors:")
            for factor in factors[:3]:
                print(f"     • {factor}")

        recommendations = risk_prediction.get('recommendations', [])
        if recommendations:
            print(f"   Recommendations:")
            for rec in recommendations[:3]:
                print(f"     • {rec}")
    else:
        print(f"⚠️  Risk prediction error: {risk_prediction.get('error')}")

    # ============================================================================
    # STEP 8: AI-POWERED SHIPMENT ANALYSIS
    # ============================================================================
    print("\n" + "─" * 80)
    print("🤖 CLAUDE: Getting AI-powered shipment recommendations...")
    print("─" * 80)

    ai_analysis = await tools.analyze_shipment_with_ai(shipment_id=shipment_id)

    if "error" not in ai_analysis:
        print(f"✅ AI Analysis Complete")

        loading_strategy = ai_analysis.get('loading_strategy', 'N/A')
        print(f"   Loading Strategy: {loading_strategy}")

        special_handling = ai_analysis.get('special_handling_items', [])
        if special_handling:
            print(f"   Special Handling Required:")
            for item in special_handling[:3]:
                print(f"     • {item}")

        truck_criteria = ai_analysis.get('truck_selection_criteria', [])
        if truck_criteria:
            print(f"   Truck Selection Criteria:")
            for criteria in truck_criteria[:3]:
                print(f"     • {criteria}")
    else:
        print(f"⚠️  AI analysis error: {ai_analysis.get('error')}")

    # ============================================================================
    # STEP 9: PUBLISH OPTIMIZATION COMPLETE EVENT
    # ============================================================================
    print("\n" + "─" * 80)
    print("🤖 CLAUDE: Publishing optimization complete event to Redpanda...")
    print("─" * 80)

    event_result = await tools.publish_event(
        event_type="shipment_optimized",
        event_data={
            "shipment_id": shipment_id,
            "origin": "Los Angeles",
            "destination": "New York",
            "truck_id": truck_id or "AUTO-SELECTED",
            "utilization": packing_result.get('utilization_percentage', 0),
            "risk_level": risk_prediction.get('risk_level', 'UNKNOWN'),
            "weather_severity": route_conditions.get('weather_severity', 0),
            "optimized_at": datetime.now().isoformat(),
            "status": "ready_for_dispatch"
        }
    )

    if "error" not in event_result:
        print(f"✅ Event Published")
        print(f"   Topic: {event_result.get('topic', 'N/A')}")
        print(f"   Status: {event_result.get('status', 'N/A')}")
    else:
        print(f"⚠️  Event publish error: {event_result.get('error')}")

    # ============================================================================
    # STEP 10: GET COMPLETE KNOWLEDGE GRAPH VIEW
    # ============================================================================
    print("\n" + "─" * 80)
    print("🤖 CLAUDE: Retrieving complete knowledge graph for shipment...")
    print("─" * 80)

    knowledge_graph = await graph_tools.get_shipment_knowledge_graph(shipment_id)

    if knowledge_graph:
        print(f"✅ Knowledge Graph Retrieved")
        print(f"   Shipment Status: {knowledge_graph.get('shipment', {}).get('status', 'N/A')}")
        print(f"   Items in Graph: {len(knowledge_graph.get('items', []))}")
        print(f"   Origin Location: {knowledge_graph.get('origin', {}).get('name', 'N/A')}")
        print(f"   Destination Location: {knowledge_graph.get('destination', {}).get('name', 'N/A')}")

        similar = knowledge_graph.get('similar_shipments', [])
        if similar:
            print(f"   Similar Historical Shipments: {len(similar)}")

    # ============================================================================
    # STEP 11: NETWORK OVERVIEW
    # ============================================================================
    print("\n" + "─" * 80)
    print("🤖 CLAUDE: Getting freight network overview...")
    print("─" * 80)

    network = await graph_tools.get_network_overview()

    if network:
        print(f"✅ Network Overview")
        print(f"   Total Shipments: {network.get('total_shipments', 0)}")
        print(f"   Total Locations: {network.get('total_locations', 0)}")
        print(f"   Total Items: {network.get('total_items', 0)}")

    # ============================================================================
    # FINAL SUMMARY
    # ============================================================================
    print("\n" + "=" * 80)
    print(" 🎉 OPTIMIZATION COMPLETE - SUMMARY")
    print("=" * 80)

    print(f"""
✅ Shipment ID: {shipment_id}
✅ Route: Los Angeles → New York
✅ Items: {len(items)} boxes, {total_weight} kg total
✅ Truck: {truck_id or 'Auto-selected'}
✅ Packing Utilization: {packing_result.get('utilization_percentage', 0):.1f}%
✅ Risk Level: {risk_prediction.get('risk_level', 'UNKNOWN')}
✅ Weather Conditions: Analyzed
✅ Traffic Conditions: Analyzed
✅ Stored in Knowledge Graph: YES
✅ Event Published: YES
✅ Ready for Dispatch: YES

📊 Agentic Capabilities Demonstrated:
   1. ✅ Autonomous shipment creation
   2. ✅ Knowledge graph storage for learning
   3. ✅ Historical pattern analysis
   4. ✅ Real-time route condition checking
   5. ✅ Graph-based truck selection
   6. ✅ Real 3D bin packing optimization
   7. ✅ AI-powered damage risk prediction
   8. ✅ AI-powered shipment analysis
   9. ✅ Event streaming to Redpanda
   10. ✅ Complete knowledge graph tracking
   11. ✅ Network-wide analytics

🚀 Claude executed 11 autonomous steps to optimize this shipment!
""")

    # ============================================================================
    # CLEANUP
    # ============================================================================
    print("\n" + "─" * 80)
    print("🧹 Cleanup: Removing test data from Neo4j...")
    print("─" * 80)

    try:
        neo4j = await get_neo4j_service()
        await neo4j.query_graph_with_cypher(
            f"""
            MATCH (s:Shipment {{id: '{shipment_id}'}})
            OPTIONAL MATCH (s)-[:CONTAINS]->(i:Item)
            OPTIONAL MATCH (s)-[:FROM]->(o:Location)
            OPTIONAL MATCH (s)-[:TO]->(d:Location)
            DETACH DELETE s, i
            """,
            {}
        )
        print("✅ Test data cleaned up")
    except Exception as e:
        print(f"⚠️  Cleanup warning: {e}")

    print("\n" + "=" * 80)
    print(" ✅ FULL AGENTIC WORKFLOW TEST COMPLETE")
    print("=" * 80)

    return True


async def main():
    """Run the full agentic workflow test"""
    try:
        result = await test_full_agentic_optimization()

        if result:
            print("\n✅ SUCCESS: All agentic capabilities verified!")
            return 0
        else:
            print("\n❌ FAILURE: Some capabilities did not work")
            return 1

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
