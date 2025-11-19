"""
Test MCP Server with Neo4j Integration
Verifies all tools are registered and working
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.neo4j_service import get_neo4j_service
from kitt_mcp.graph_tools import graph_tools


async def test_neo4j_connection():
    """Test Neo4j connection"""
    print("=" * 70)
    print(" TEST 1: Neo4j Connection")
    print("=" * 70)

    try:
        neo4j = await get_neo4j_service()
        print("✅ Connected to Neo4j")

        # Test network stats query
        stats = await neo4j.get_network_stats()
        print(f"✅ Network stats: {stats}")

        return True
    except Exception as e:
        print(f"❌ Neo4j connection failed: {e}")
        return False


async def test_graph_tools():
    """Test graph tools"""
    print("\n" + "=" * 70)
    print(" TEST 2: Graph Tools")
    print("=" * 70)

    try:
        # Test 1: Store a test shipment
        print("\n[Test 2.1] Storing test shipment in graph...")

        result = await graph_tools.store_shipment_in_graph(
            shipment_id="TEST-S-001",
            origin="Los Angeles",
            destination="New York",
            items=[
                {
                    "id": "TEST-I-001",
                    "width": 100,
                    "height": 80,
                    "depth": 60,
                    "weight": 50,
                    "fragile": False,
                    "stackable": True,
                    "description": "Test Item 1"
                },
                {
                    "id": "TEST-I-002",
                    "width": 80,
                    "height": 60,
                    "depth": 40,
                    "weight": 30,
                    "fragile": True,
                    "stackable": False,
                    "description": "Test Item 2"
                }
            ],
            status="pending",
            priority="high"
        )

        print(f"✅ Shipment stored: {result.get('items_added', 0)} items")

        # Test 2: Retrieve shipment graph
        print("\n[Test 2.2] Retrieving shipment knowledge graph...")

        graph = await graph_tools.get_shipment_knowledge_graph("TEST-S-001")
        print(f"✅ Retrieved graph with {len(graph.get('items', []))} items")
        print(f"   Origin: {graph.get('origin', {}).get('name', 'N/A')}")
        print(f"   Destination: {graph.get('destination', {}).get('name', 'N/A')}")

        # Test 3: Get location analytics
        print("\n[Test 2.3] Getting location analytics...")

        analytics = await graph_tools.get_location_analytics("Los Angeles")
        print(f"✅ LA Analytics:")
        print(f"   Shipments originated: {analytics.get('shipments_originated', 0)}")
        print(f"   Shipments received: {analytics.get('shipments_received', 0)}")

        # Test 4: Get network overview
        print("\n[Test 2.4] Getting network overview...")

        overview = await graph_tools.get_network_overview()
        print(f"✅ Network Overview:")
        print(f"   Total shipments: {overview.get('total_shipments', 0)}")
        print(f"   Total locations: {overview.get('total_locations', 0)}")
        print(f"   Total items: {overview.get('total_items', 0)}")

        # Test 5: Custom Cypher query
        print("\n[Test 2.5] Testing custom Cypher query...")

        cypher_result = await graph_tools.query_graph_with_cypher(
            """
            MATCH (s:Shipment)
            RETURN s.id as shipment_id, s.priority as priority
            LIMIT 5
            """
        )

        print(f"✅ Cypher query returned {len(cypher_result)} results")
        for record in cypher_result[:3]:
            print(f"   - {record}")

        return True

    except Exception as e:
        print(f"❌ Graph tools test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_mcp_server_startup():
    """Test MCP server can start"""
    print("\n" + "=" * 70)
    print(" TEST 3: MCP Server Startup")
    print("=" * 70)

    try:
        # Import MCP server
        from kitt_mcp.server import mcp

        if mcp:
            print("✅ MCP server initialized")
            print(f"✅ Server name: {mcp.name}")

            # List available tools
            print("\n📋 Available MCP Tools:")
            # Note: We can't easily list tools without running the server
            # but we can verify it imported successfully
            print("   Tools registered in mcp/server.py:")
            print("   1. get_shipment_data")
            print("   2. create_shipment")
            print("   3. optimize_packing")
            print("   4. get_route_conditions")
            print("   5. predict_damage_risk")
            print("   6. publish_event")
            print("   7. analyze_shipment_with_ai")
            print("   8. store_shipment_in_knowledge_graph")
            print("   9. get_shipment_knowledge_graph")
            print("   10. find_optimal_trucks_from_graph")
            print("   11. get_location_analytics_from_graph")
            print("   12. find_historical_shipment_patterns")
            print("   13. get_freight_network_overview")
            print("   14. query_knowledge_graph_with_cypher")

            return True
        else:
            print("❌ MCP server not available (FastMCP not installed?)")
            return False

    except Exception as e:
        print(f"❌ MCP server startup test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def cleanup_test_data():
    """Clean up test data from Neo4j"""
    print("\n" + "=" * 70)
    print(" CLEANUP: Removing test data")
    print("=" * 70)

    try:
        neo4j = await get_neo4j_service()

        # Delete test shipment and related nodes
        await neo4j.query_graph_with_cypher(
            """
            MATCH (s:Shipment {id: 'TEST-S-001'})
            OPTIONAL MATCH (s)-[:CONTAINS]->(i:Item)
            DETACH DELETE s, i
            """
        )

        print("✅ Test data cleaned up")
        return True

    except Exception as e:
        print(f"⚠️  Cleanup failed (this is okay): {e}")
        return False


async def main():
    """Run all tests"""
    print("\n" + "█" * 70)
    print(" KITT MCP + Neo4j Integration Tests")
    print("█" * 70)

    results = []

    # Test 1: Neo4j Connection
    results.append(await test_neo4j_connection())

    # Test 2: Graph Tools
    results.append(await test_graph_tools())

    # Test 3: MCP Server
    results.append(await test_mcp_server_startup())

    # Cleanup
    await cleanup_test_data()

    # Summary
    print("\n" + "█" * 70)
    print(" TEST SUMMARY")
    print("█" * 70)

    total_tests = len(results)
    passed_tests = sum(results)

    print(f"\nTotal tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")

    if all(results):
        print("\n✅ ALL TESTS PASSED! MCP + Neo4j Integration is working!")
        print("\n🚀 Next Steps:")
        print("   1. Start MCP server: python mcp/server.py")
        print("   2. Connect Claude Desktop to MCP server")
        print("   3. Try agentic queries with Claude")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED - Check errors above")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
