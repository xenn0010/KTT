"""
Real Truck Packing Test - Production Scenario
Tests DeepPack3D with actual freight dimensions
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.deeppack3d_service import get_deeppack_service


def test_real_truck():
    """Test with real truck and pallet dimensions"""
    print("=" * 70)
    print(" REAL TRUCK PACKING TEST - 20ft Container")
    print("=" * 70)

    service = get_deeppack_service(method="bl", lookahead=5, verbose=0)
    print(f"\nService: {type(service).__name__}")

    # Real 20ft shipping container: 589×235×239 cm
    container = (589, 235, 239)

    # Real freight items (pallets and crates in cm)
    items = [
        {"id": "PALLET-001", "width": 120, "height": 100, "depth": 80, "weight": 500},
        {"id": "PALLET-002", "width": 120, "height": 100, "depth": 80, "weight": 450},
        {"id": "PALLET-003", "width": 120, "height": 100, "depth": 80, "weight": 480},
        {"id": "CRATE-001", "width": 100, "height": 80, "depth": 60, "weight": 200},
        {"id": "CRATE-002", "width": 100, "height": 80, "depth": 60, "weight": 180},
        {"id": "BOX-001", "width": 60, "height": 50, "depth": 40, "weight": 50},
        {"id": "BOX-002", "width": 60, "height": 50, "depth": 40, "weight": 45},
        {"id": "BOX-003", "width": 50, "height": 40, "depth": 30, "weight": 30},
    ]

    print(f"\n📦 Container: 20ft Shipping Container")
    print(f"   Dimensions: {container[0]}×{container[1]}×{container[2]} cm")
    print(f"   Volume: {container[0]*container[1]*container[2]/1000000:.2f} m³")

    print(f"\n📋 Cargo: {len(items)} items")
    total_volume = 0
    total_weight = 0
    for item in items:
        vol = (item['width'] * item['height'] * item['depth']) / 1000000
        total_volume += vol
        total_weight += item['weight']
        print(f"   • {item['id']}: {item['width']}×{item['height']}×{item['depth']} cm "
              f"({vol:.3f}m³, {item['weight']}kg)")

    container_volume = (container[0] * container[1] * container[2]) / 1000000
    print(f"\n📊 Totals:")
    print(f"   Total cargo volume: {total_volume:.3f} m³")
    print(f"   Total weight: {total_weight} kg")
    print(f"   Theoretical utilization: {(total_volume/container_volume)*100:.2f}%")

    print(f"\n{'═' * 70}")
    print(" RUNNING DEEPPACK3D...")
    print(f"{'═' * 70}\n")

    result = service.pack_items(
        items=items,
        container_dimensions=container,
        max_weight=25000  # 20ft container max ~25 tons
    )

    print(f"{'─' * 70}")
    print(" RESULTS")
    print(f"{'─' * 70}")

    if result['success']:
        print(f"✅ Status: SUCCESS")
        print(f"🔧 Algorithm: {result['algorithm']}")
        print(f"📦 Items packed: {result['items_packed']}/{result['items_requested']}")
        print(f"🚚 Bins used: {result['bins_used']}")
        print(f"📈 Space utilization: {result['utilization']:.2f}%")
        print(f"⏱️  Computation time: {result['computation_time_ms']}ms")

        print(f"\n{'─' * 70}")
        print(" LOADING MANIFEST")
        print(f"{'─' * 70}")

        for i, placement in enumerate(result['placements'], 1):
            pos = placement['position']
            dims = placement['dimensions']
            print(f"\n{i}. {placement['item_id']}")
            print(f"   Position: ({pos['x']:.1f}, {pos['y']:.1f}, {pos['z']:.1f}) cm from origin")
            print(f"   Size: {dims['width']:.1f}×{dims['height']:.1f}×{dims['depth']:.1f} cm")
            print(f"   Rotation: {placement['rotation']}°")
            print(f"   Weight: {placement['weight']} kg")
            print(f"   Container: #{placement['bin_number']}")

        # Export for 3D visualization
        export_data = {
            "container": {
                "dimensions": {"width": container[0], "height": container[1], "depth": container[2]},
                "type": "20ft_shipping_container"
            },
            "items": result['placements'],
            "stats": {
                "utilization": result['utilization'],
                "items_packed": result['items_packed'],
                "total_weight_kg": total_weight,
                "algorithm": result['algorithm'],
                "computation_ms": result['computation_time_ms']
            }
        }

        import json
        output_file = Path("/tmp/truck_loading_plan.json")
        with open(output_file, 'w') as f:
            json.dump(export_data, f, indent=2)

        print(f"\n{'─' * 70}")
        print(f"📁 3D visualization data exported to: {output_file}")
        print(f"{'─' * 70}")

        return True, export_data
    else:
        print(f"❌ Status: FAILED")
        print(f"Error: {result.get('error', 'Unknown')}")
        return False, None


if __name__ == "__main__":
    success, data = test_real_truck()

    if success:
        print(f"\n{'█' * 70}")
        print(" ✅ REAL TRUCK PACKING TEST PASSED!")
        print(f"{'█' * 70}")
        print(f"\nNext step: Use /tmp/truck_loading_plan.json for 3D visualization")
        exit(0)
    else:
        print(f"\n❌ Test failed")
        exit(1)
