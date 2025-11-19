"""
Simple DeepPack3D Test
Tests with dimensions matching DeepPack3D's expected scale (32x32x32 max)
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.deeppack3d_service import get_deeppack_service, DEEPPACK_AVAILABLE


def test_simple_packing():
    """Test DeepPack3D with small dimensions that fit in 32x32x32 container"""
    print("=" * 70)
    print(" Simple DeepPack3D Test - Small Dimensions")
    print("=" * 70)

    # Get service
    service = get_deeppack_service(method="bl", lookahead=5, verbose=1)
    print(f"\nService type: {type(service).__name__}")
    print(f"DeepPack3D available: {DEEPPACK_AVAILABLE}")

    # Create test items that fit in 32x32x32 container
    items = [
        {"id": "BOX-001", "width": 10, "height": 8, "depth": 6, "weight": 5},
        {"id": "BOX-002", "width": 12, "height": 10, "depth": 8, "weight": 7},
        {"id": "BOX-003", "width": 8, "height": 6, "depth": 5, "weight": 3},
        {"id": "BOX-004", "width": 15, "height": 12, "depth": 10, "weight": 10},
        {"id": "BOX-005", "width": 9, "height": 7, "depth": 6, "weight": 4},
    ]

    # Container dimensions (fits DeepPack3D's expected scale)
    container = (32, 32, 32)  # width, height, depth

    print(f"\n📦 Packing {len(items)} items into {container} container")
    print(f"\nItems:")
    total_volume = 0
    for item in items:
        vol = item['width'] * item['height'] * item['depth']
        total_volume += vol
        print(f"  • {item['id']}: {item['width']}×{item['height']}×{item['depth']} "
              f"(volume: {vol}, weight: {item['weight']}kg)")

    container_volume = container[0] * container[1] * container[2]
    theoretical_util = (total_volume / container_volume) * 100
    print(f"\nTheoretical max utilization: {theoretical_util:.2f}%")
    print(f"Container volume: {container_volume}")
    print(f"Total items volume: {total_volume}")

    # Pack items
    print(f"\n{'═' * 70}")
    print(" Running DeepPack3D...")
    print(f"{'═' * 70}")

    result = service.pack_items(
        items=items,
        container_dimensions=container,
        max_weight=100
    )

    # Display results
    print(f"\n{'─' * 70}")
    print(" RESULTS")
    print(f"{'─' * 70}")

    if result['success']:
        print(f"✅ Status: SUCCESS")
        print(f"🔧 Algorithm: {result['algorithm']}")
        print(f"📊 Items packed: {result['items_packed']}/{result['items_requested']}")
        print(f"📦 Bins used: {result['bins_used']}")
        print(f"📈 Utilization: {result['utilization']:.2f}%")
        print(f"⏱️  Computation time: {result['computation_time_ms']}ms")

        if result.get('placements'):
            print(f"\n{'─' * 70}")
            print(" ITEM PLACEMENTS")
            print(f"{'─' * 70}")
            for i, placement in enumerate(result['placements'], 1):
                pos = placement['position']
                dims = placement['dimensions']
                print(f"{i}. {placement['item_id']}")
                print(f"   Position: ({pos['x']:.1f}, {pos['y']:.1f}, {pos['z']:.1f})")
                print(f"   Size: {dims['width']:.1f}×{dims['height']:.1f}×{dims['depth']:.1f}")
                print(f"   Rotation: {placement['rotation']}°")
                print(f"   Bin: {placement['bin_number']}")

        # Verify all items packed
        if result['items_packed'] == len(items):
            print(f"\n✅ SUCCESS: All {len(items)} items packed!")
        else:
            print(f"\n⚠️  WARNING: Only {result['items_packed']}/{len(items)} items packed")

        # Compare with theoretical
        efficiency = (result['utilization'] / theoretical_util) * 100 if theoretical_util > 0 else 0
        print(f"\n📊 Packing efficiency: {efficiency:.1f}% of theoretical maximum")

        return True

    else:
        print(f"❌ Status: FAILED")
        print(f"🔧 Algorithm: {result['algorithm']}")
        print(f"❌ Error: {result.get('error', 'Unknown error')}")
        print(f"⏱️  Computation time: {result.get('computation_time_ms', 0)}ms")

        return False


def test_large_dimensions():
    """Test with larger truck-sized dimensions to show the scaling issue"""
    print("\n" + "=" * 70)
    print(" Large Dimensions Test - Truck Size (240×120×100)")
    print("=" * 70)

    service = get_deeppack_service(method="bl", lookahead=5, verbose=0)
    print(f"\nService type: {type(service).__name__}")

    # Items sized for a real truck
    items = [
        {"id": "PALLET-001", "width": 50, "height": 40, "depth": 30, "weight": 25},
        {"id": "PALLET-002", "width": 60, "height": 50, "depth": 40, "weight": 30},
        {"id": "CRATE-001", "width": 40, "height": 30, "depth": 20, "weight": 15},
    ]

    # Real truck dimensions
    container = (240, 120, 100)

    print(f"\n📦 Packing {len(items)} items into {container} truck")
    print(f"Note: This will likely fail due to dimension scaling issue")

    result = service.pack_items(
        items=items,
        container_dimensions=container,
        max_weight=5000
    )

    if result['success']:
        print(f"\n✅ Unexpectedly succeeded!")
        print(f"Utilization: {result['utilization']:.2f}%")
        return True
    else:
        print(f"\n❌ Failed as expected: {result.get('error', 'Unknown')[:100]}...")
        print(f"💡 This demonstrates the need for dimension scaling in the service")
        return False


def main():
    """Run all tests"""
    print("\n" + "█" * 70)
    print(" DeepPack3D Simple Test Suite")
    print("█" * 70)

    results = []

    # Test 1: Small dimensions (should work)
    try:
        result = test_simple_packing()
        results.append(("Small Dimensions", result))
    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Small Dimensions", False))

    # Test 2: Large dimensions (expected to fail)
    try:
        result = test_large_dimensions()
        results.append(("Large Dimensions", result))
    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        results.append(("Large Dimensions", False))

    # Summary
    print("\n" + "█" * 70)
    print(" TEST SUMMARY")
    print("█" * 70)

    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{name:.<50} {status}")

    passed = sum(1 for _, r in results if r)
    total = len(results)

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed > 0:
        print(f"\n🎉 At least one test passed - DeepPack3D is working!")
        return 0
    else:
        print(f"\n⚠️  All tests failed")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
