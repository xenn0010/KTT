"""
Overlay 3D Boxes onto Truck PNG Image
Uses PIL to draw boxes with manual perspective calibration
"""

import json
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import argparse


def calibrate_perspective(truck_image_path: str):
    """
    Interactive tool to calibrate perspective for your truck image

    You'll need to identify 4 reference points in your truck image:
    1. Container origin (bottom-left-front corner)
    2. X-axis vanishing point (width direction)
    3. Y-axis vanishing point (height direction)
    4. Z-axis vanishing point (depth direction)
    """
    img = Image.open(truck_image_path)

    print("=" * 70)
    print(" TRUCK IMAGE PERSPECTIVE CALIBRATION")
    print("=" * 70)
    print(f"\nImage size: {img.size[0]}×{img.size[1]} pixels")
    print("\nTo overlay boxes accurately, we need to calibrate perspective.")
    print("\nLook at your truck image and identify these points:")
    print("  1. Container origin (where X=0, Y=0, Z=0)")
    print("  2. X-axis direction (width - left to right)")
    print("  3. Y-axis direction (height - bottom to top)")
    print("  4. Z-axis direction (depth - front to back)")

    # Manual calibration values
    calibration = {
        "origin_x": int(input("\nContainer origin X pixel (left edge): ")),
        "origin_y": int(input("Container origin Y pixel (bottom edge): ")),
        "scale_x": float(input("X-axis scale (pixels per cm): ")),
        "scale_y": float(input("Y-axis scale (pixels per cm): ")),
        "scale_z": float(input("Z-axis scale (pixels per cm): ")),
        "angle_x": float(input("X-axis angle in degrees (0=horizontal right): ")),
        "angle_y": float(input("Y-axis angle in degrees (90=vertical up): ")),
        "angle_z": float(input("Z-axis angle in degrees (perspective depth): "))
    }

    # Save calibration
    calib_file = Path(truck_image_path).with_suffix('.calib.json')
    with open(calib_file, 'w') as f:
        json.dump(calibration, f, indent=2)

    print(f"\n✅ Calibration saved to: {calib_file}")
    return calibration


def transform_3d_to_2d(x3d, y3d, z3d, calibration):
    """
    Transform 3D coordinates to 2D image coordinates
    using calibrated perspective
    """
    import math

    # Convert angles to radians
    angle_x = math.radians(calibration['angle_x'])
    angle_y = math.radians(calibration['angle_y'])
    angle_z = math.radians(calibration['angle_z'])

    # Project 3D point to 2D
    x2d = calibration['origin_x'] + \
          x3d * calibration['scale_x'] * math.cos(angle_x) + \
          z3d * calibration['scale_z'] * math.cos(angle_z)

    y2d = calibration['origin_y'] - \
          y3d * calibration['scale_y'] * math.cos(angle_y) - \
          z3d * calibration['scale_z'] * math.sin(angle_z)

    return int(x2d), int(y2d)


def draw_box_on_image(draw, item, calibration, color):
    """
    Draw a 3D box onto the image using calibrated perspective
    """
    pos = item['position']
    dims = item['dimensions']

    # Calculate 8 corners of the box
    corners_3d = [
        # Bottom face
        (pos['x'], pos['y'], pos['z']),
        (pos['x'] + dims['width'], pos['y'], pos['z']),
        (pos['x'] + dims['width'], pos['y'], pos['z'] + dims['depth']),
        (pos['x'], pos['y'], pos['z'] + dims['depth']),
        # Top face
        (pos['x'], pos['y'] + dims['height'], pos['z']),
        (pos['x'] + dims['width'], pos['y'] + dims['height'], pos['z']),
        (pos['x'] + dims['width'], pos['y'] + dims['height'], pos['z'] + dims['depth']),
        (pos['x'], pos['y'] + dims['height'], pos['z'] + dims['depth']),
    ]

    # Transform to 2D
    corners_2d = [transform_3d_to_2d(x, y, z, calibration) for x, y, z in corners_3d]

    # Draw edges
    edges = [
        # Bottom face
        (0, 1), (1, 2), (2, 3), (3, 0),
        # Top face
        (4, 5), (5, 6), (6, 7), (7, 4),
        # Vertical edges
        (0, 4), (1, 5), (2, 6), (3, 7)
    ]

    for start, end in edges:
        draw.line([corners_2d[start], corners_2d[end]], fill=color, width=3)

    # Draw faces (semi-transparent)
    # Front face
    draw.polygon([corners_2d[0], corners_2d[1], corners_2d[5], corners_2d[4]],
                 fill=(*color[:3], 100), outline=color)

    # Top face
    draw.polygon([corners_2d[4], corners_2d[5], corners_2d[6], corners_2d[7]],
                 fill=(*color[:3], 120), outline=color)


def overlay_boxes(
    truck_image_path: str,
    packing_data_path: str,
    output_path: str,
    calibration_file: str = None,
    auto_calibrate: bool = False
):
    """
    Overlay packing boxes onto truck image
    """
    # Load truck image
    if not Path(truck_image_path).exists():
        print(f"❌ Truck image not found: {truck_image_path}")
        return False

    img = Image.open(truck_image_path)
    img = img.convert('RGBA')  # Enable transparency
    draw = ImageDraw.Draw(img, 'RGBA')

    # Load packing data
    with open(packing_data_path) as f:
        data = json.load(f)

    # Load or create calibration
    if calibration_file and Path(calibration_file).exists():
        with open(calibration_file) as f:
            calibration = json.load(f)
        print(f"✅ Loaded calibration from: {calibration_file}")
    elif auto_calibrate:
        print("⚠️  Auto-calibration not yet implemented")
        print("Using default side-view perspective...")
        # Default calibration for side view
        calibration = {
            "origin_x": 100,
            "origin_y": img.size[1] - 100,
            "scale_x": 1.0,
            "scale_y": 1.0,
            "scale_z": 0.5,
            "angle_x": 0,
            "angle_y": 90,
            "angle_z": 30
        }
    else:
        print("\n⚠️  No calibration file provided.")
        print("Options:")
        print("  1. Run with --calibrate to interactively calibrate")
        print("  2. Provide --calibration-file path/to/calibration.json")
        print("  3. Use default perspective (may not align perfectly)")

        use_default = input("\nUse default perspective? (y/n): ").lower() == 'y'
        if not use_default:
            return False

        # Default side view
        calibration = {
            "origin_x": 100,
            "origin_y": img.size[1] - 100,
            "scale_x": 1.0,
            "scale_y": 1.0,
            "scale_z": 0.5,
            "angle_x": 0,
            "angle_y": 90,
            "angle_z": 30
        }

    # Color palette
    colors = [
        (255, 50, 50, 255),    # Red
        (50, 255, 50, 255),    # Green
        (50, 50, 255, 255),    # Blue
        (255, 255, 50, 255),   # Yellow
        (255, 50, 255, 255),   # Magenta
        (50, 255, 255, 255),   # Cyan
    ]

    # Draw boxes
    print(f"\nDrawing {len(data['items'])} boxes...")
    for i, item in enumerate(data['items']):
        color = colors[i % len(colors)]
        draw_box_on_image(draw, item, calibration, color)
        print(f"  ✓ {item['item_id']}")

    # Save result
    # Convert back to RGB for PNG
    img = img.convert('RGB')
    img.save(output_path, quality=95)
    print(f"\n✅ Result saved to: {output_path}")

    return True


def main():
    parser = argparse.ArgumentParser(description='Overlay 3D boxes onto truck image')
    parser.add_argument('--truck-image', required=True, help='Path to truck PNG image')
    parser.add_argument('--packing-data', default='/tmp/truck_loading_plan.json',
                       help='Path to packing JSON data')
    parser.add_argument('--output', default='/tmp/truck_with_boxes.png',
                       help='Output image path')
    parser.add_argument('--calibration-file', help='Path to calibration JSON')
    parser.add_argument('--calibrate', action='store_true',
                       help='Run interactive calibration')

    args = parser.parse_args()

    print("=" * 70)
    print(" OVERLAY 3D BOXES ONTO TRUCK IMAGE")
    print("=" * 70)

    # Calibration mode
    if args.calibrate:
        calibrate_perspective(args.truck_image)
        print("\nNow run again without --calibrate to overlay boxes")
        return

    # Overlay mode
    success = overlay_boxes(
        truck_image_path=args.truck_image,
        packing_data_path=args.packing_data,
        output_path=args.output,
        calibration_file=args.calibration_file
    )

    if success:
        print("\n" + "=" * 70)
        print(f" ✅ DONE! Open {args.output}")
        print("=" * 70)
        print("\nTip: If boxes don't align perfectly, run with --calibrate")
        print("     to adjust perspective for your specific truck image")


if __name__ == "__main__":
    main()
