"""
Test DeepPack3D Integration
Tests both mock and real DeepPack3D service
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.deeppack3d_service import get_deeppack_service, DEEPPACK_AVAILABLE


async def test_mock_service():
    """Test mock service basic functionality"""
    print("=" * 60)
    print("Testing Mock DeepPack3D Service")
    print("=" * 60)

    # Get mock service
    service = get_deeppack_service(force_mock=True)
    print(f"Service type: {type(service).__name__}")

    # Create test items
    items = [
        {"id": "ITEM-001", "width": 50, "height": 40, "depth": 30, "weight": 25},
        {"id": "ITEM-002", "width": 60, "height": 50, "depth": 40, "weight": 30},
        {"id": "ITEM-003", "width": 40, "height": 30, "depth": 20, "weight": 15},
    ]

    # Container dimensions (truck)
    container = (240, 120, 100)  # width, height, depth

    print(f"\nPacking {len(items)} items into container {container}")
    print(f"Items:")
    for item in items:
        print(f"  - {item['id']}: {item['width']}x{item['height']}x{item['depth']} ({item['weight']}kg)")

    # Pack items
    result = service.pack_items(
        items=items,
        container_dimensions=container,
        max_weight=5000
    )

    # Display results
    print(f"\n{'─' * 60}")
    print("Results:")
    print(f"{'─' * 60}")
    print(f"Success: {result['success']}")
    print(f"Algorithm: {result['algorithm']}")
    print(f"Items packed: {result['items_packed']}/{result['items_requested']}")
    print(f"Bins used: {result['bins_used']}")
    print(f"Utilization: {result['utilization']:.2f}%")
    print(f"Computation time: {result['computation_time_ms']}ms")

    print(f"\nPlacements:")
    for placement in result['placements']:
        pos = placement['position']
        dims = placement['dimensions']
        print(f"  {placement['item_id']}: pos({pos['x']:.1f}, {pos['y']:.1f}, {pos['z']:.1f}) "
              f"size({dims['width']:.1f}x{dims['height']:.1f}x{dims['depth']:.1f})")

    assert result['success'], "Packing should succeed"
    assert result['items_packed'] == len(items), "All items should be packed"
    assert result['utilization'] > 0, "Utilization should be positive"

    print("\n✅ Mock service test PASSED")
    return True


async def test_real_service():
    """Test real DeepPack3D service (if available)"""
    if not DEEPPACK_AVAILABLE:
        print("\n" + "=" * 60)
        print("⚠️  DeepPack3D dependencies not available")
        print("=" * 60)
        print("To enable real DeepPack3D testing:")
        print("  1. Install dependencies:")
        print("     pip install -r requirements-deeppack3d.txt")
        print("  Or:")
        print("     sudo apt-get install python3-numpy python3-matplotlib python3-tensorflow")
        print("=" * 60)
        return False

    print("\n" + "=" * 60)
    print("Testing Real DeepPack3D Service")
    print("=" * 60)

    # Get real service
    service = get_deeppack_service(method="bl", lookahead=5)
    print(f"Service type: {type(service).__name__}")

    # Create test items
    items = [
        {"id": "ITEM-001", "width": 50, "height": 40, "depth": 30, "weight": 25},
        {"id": "ITEM-002", "width": 60, "height": 50, "depth": 40, "weight": 30},
        {"id": "ITEM-003", "width": 40, "height": 30, "depth": 20, "weight": 15},
        {"id": "ITEM-004", "width": 55, "height": 45, "depth": 35, "weight": 28},
        {"id": "ITEM-005", "width": 45, "height": 35, "depth": 25, "weight": 20},
    ]

    # Container dimensions (truck)
    container = (240, 120, 100)  # width, height, depth

    print(f"\nPacking {len(items)} items into container {container}")
    print(f"Items:")
    for item in items:
        print(f"  - {item['id']}: {item['width']}x{item['height']}x{item['depth']} ({item['weight']}kg)")

    # Pack items
    result = service.pack_items(
        items=items,
        container_dimensions=container,
        max_weight=5000
    )

    # Display results
    print(f"\n{'─' * 60}")
    print("Results:")
    print(f"{'─' * 60}")
    print(f"Success: {result['success']}")
    print(f"Algorithm: {result['algorithm']}")

    if result['success']:
        print(f"Items packed: {result['items_packed']}/{result['items_requested']}")
        print(f"Bins used: {result['bins_used']}")
        print(f"Utilization: {result['utilization']:.2f}%")
        print(f"Computation time: {result['computation_time_ms']}ms")

        if result.get('placements'):
            print(f"\nPlacements:")
            for placement in result['placements'][:10]:  # Show first 10
                pos = placement['position']
                dims = placement['dimensions']
                print(f"  {placement['item_id']}: pos({pos['x']:.1f}, {pos['y']:.1f}, {pos['z']:.1f}) "
                      f"size({dims['width']:.1f}x{dims['height']:.1f}x{dims['depth']:.1f}) "
                      f"rot={placement['rotation']}")

        assert result['items_packed'] > 0, "At least some items should be packed"
        assert result['utilization'] > 0, "Utilization should be positive"
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")
        print(f"Computation time: {result.get('computation_time_ms', 0)}ms")
        print("\n⚠️  Packing failed - this is expected with dimension scaling issue")
        return False  # Mark as failed but not crash

    assert result['success'], "Packing should succeed"

    print("\n✅ Real service test PASSED")
    return True


async def test_integration_with_mcp():
    """Test integration with MCP tools"""
    print("\n" + "=" * 60)
    print("Testing MCP Tools Integration")
    print("=" * 60)

    # Import MCP tools
    try:
        from kitt_mcp.tools import MCPTools
        from kitt_mcp.database import db

        print("✅ MCP imports successful")

        # Initialize database
        await db.init_db()
        print("✅ Database initialized")

        # Create test shipment
        tools = MCPTools()

        shipment_result = await tools.create_shipment(
            origin="Chicago",
            destination="Dallas",
            items=[
                {"width": 50, "height": 40, "depth": 30, "weight": 25},
                {"width": 60, "height": 50, "depth": 40, "weight": 30},
                {"width": 40, "height": 30, "depth": 20, "weight": 15},
            ],
            priority="high"
        )

        print(f"✅ Shipment created: {shipment_result['shipment_id']}")

        # Optimize packing
        packing_result = await tools.optimize_packing(
            shipment_id=shipment_result['shipment_id']
        )

        print(f"\nPacking optimization result:")
        print(f"  Plan ID: {packing_result['plan_id']}")
        print(f"  Truck ID: {packing_result['truck_id']}")
        print(f"  Utilization: {packing_result['utilization']}%")
        print(f"  Items packed: {packing_result['items_packed']}")

        assert packing_result['success'], "Packing optimization should succeed"
        print("\n✅ MCP integration test PASSED")

        # Cleanup
        await db.close()

        return True

    except ImportError as e:
        print(f"⚠️  Could not import MCP tools: {e}")
        return False
    except Exception as e:
        print(f"❌ MCP integration test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests"""
    print("\n" + "█" * 60)
    print(" DeepPack3D Integration Test Suite")
    print("█" * 60)

    results = []

    # Test 1: Mock service
    try:
        result = await test_mock_service()
        results.append(("Mock Service", result))
    except Exception as e:
        print(f"\n❌ Mock service test FAILED: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Mock Service", False))

    # Test 2: Real service (if available)
    try:
        result = await test_real_service()
        results.append(("Real Service", result))
    except Exception as e:
        print(f"\n❌ Real service test FAILED: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Real Service", False))

    # Test 3: MCP integration
    try:
        result = await test_integration_with_mcp()
        results.append(("MCP Integration", result))
    except Exception as e:
        print(f"\n❌ MCP integration test FAILED: {e}")
        import traceback
        traceback.print_exc()
        results.append(("MCP Integration", False))

    # Summary
    print("\n" + "█" * 60)
    print(" Test Summary")
    print("█" * 60)

    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED/SKIPPED"
        print(f"{name:.<40} {status}")

    passed = sum(1 for _, r in results if r)
    total = len(results)

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests PASSED!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed or skipped")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
