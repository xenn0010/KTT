"""
3D Truck Loading Visualization
Overlays packed boxes onto a truck/container image
"""

import json
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import argparse


def draw_3d_box(draw, x, y, width, height, depth, color, scale_x, scale_y, offset_x=50, offset_y=50):
    """
    Draw a 3D box in isometric view

    Args:
        draw: PIL ImageDraw object
        x, y: Position in 3D space (cm)
        width, height, depth: Box dimensions (cm)
        color: Box color
        scale_x, scale_y: Scaling factors for visualization
        offset_x, offset_y: Offset from image edge
    """
    # Convert 3D coordinates to 2D isometric projection
    # Isometric: x goes right, y goes up, z goes diagonally down-right

    # Scale down to fit image
    x_scaled = x * scale_x
    y_scaled = y * scale_y
    w_scaled = width * scale_x
    h_scaled = height * scale_y
    d_scaled = depth * scale_x  # depth uses x scaling

    # Isometric projection angles (30° for x and z axes)
    iso_x_angle = 0.866  # cos(30°) ≈ 0.866
    iso_z_angle = 0.5    # sin(30°) = 0.5

    # Calculate 8 corners of the box in isometric 2D space
    # Bottom face (y=0)
    p1 = (
        offset_x + x_scaled,
        offset_y - y_scaled
    )
    p2 = (
        offset_x + x_scaled + w_scaled * iso_x_angle,
        offset_y - y_scaled + w_scaled * iso_z_angle
    )
    p3 = (
        offset_x + x_scaled + w_scaled * iso_x_angle - d_scaled * iso_x_angle,
        offset_y - y_scaled + w_scaled * iso_z_angle + d_scaled * iso_z_angle
    )
    p4 = (
        offset_x + x_scaled - d_scaled * iso_x_angle,
        offset_y - y_scaled + d_scaled * iso_z_angle
    )

    # Top face (y=height)
    p5 = (p1[0], p1[1] - h_scaled)
    p6 = (p2[0], p2[1] - h_scaled)
    p7 = (p3[0], p3[1] - h_scaled)
    p8 = (p4[0], p4[1] - h_scaled)

    # Draw faces
    # Top face (lightest)
    top_color = tuple(min(255, int(c * 1.3)) for c in color)
    draw.polygon([p5, p6, p7, p8], fill=top_color, outline=(0, 0, 0, 255))

    # Right face (medium)
    right_color = color
    draw.polygon([p2, p3, p7, p6], fill=right_color, outline=(0, 0, 0, 255))

    # Left face (darkest)
    left_color = tuple(int(c * 0.7) for c in color)
    draw.polygon([p1, p4, p8, p5], fill=left_color, outline=(0, 0, 0, 255))


def create_loading_visualization(
    truck_image_path: str,
    packing_data_path: str,
    output_path: str,
    image_width: int = 1920,
    image_height: int = 1080
):
    """
    Create visualization of truck loading plan

    Args:
        truck_image_path: Path to truck/container image (optional)
        packing_data_path: Path to JSON packing data
        output_path: Where to save visualization
        image_width: Output image width
        image_height: Output image height
    """
    # Load packing data
    with open(packing_data_path) as f:
        data = json.load(f)

    container = data['container']['dimensions']
    items = data['items']
    stats = data['stats']

    # Create blank canvas or load truck image
    if truck_image_path and Path(truck_image_path).exists():
        img = Image.open(truck_image_path)
        img = img.resize((image_width, image_height))
    else:
        # Create blank white canvas
        img = Image.new('RGB', (image_width, image_height), color=(240, 240, 240))

    draw = ImageDraw.Draw(img, 'RGBA')

    # Calculate scaling to fit container in image
    container_margin = 100
    available_width = image_width - 2 * container_margin
    available_height = image_height - 2 * container_margin

    # Scale based on container dimensions
    scale_x = available_width / (container['width'] + container['depth'])
    scale_y = available_height / container['height']
    scale = min(scale_x, scale_y) * 0.8  # 0.8 for margin

    print(f"Container: {container['width']}×{container['height']}×{container['depth']} cm")
    print(f"Scale factor: {scale:.4f}")
    print(f"Packing {len(items)} items...")

    # Draw container outline first
    draw_3d_box(
        draw, 0, 0,
        container['width'],
        container['height'],
        container['depth'],
        color=(200, 200, 200, 100),  # Semi-transparent gray
        scale_x=scale,
        scale_y=scale,
        offset_x=container_margin,
        offset_y=image_height - container_margin
    )

    # Color palette for different items
    colors = [
        (255, 100, 100, 200),  # Red
        (100, 255, 100, 200),  # Green
        (100, 100, 255, 200),  # Blue
        (255, 255, 100, 200),  # Yellow
        (255, 100, 255, 200),  # Magenta
        (100, 255, 255, 200),  # Cyan
        (255, 150, 100, 200),  # Orange
        (150, 100, 255, 200),  # Purple
    ]

    # Draw each item
    for i, item in enumerate(items):
        pos = item['position']
        dims = item['dimensions']
        color = colors[i % len(colors)]

        draw_3d_box(
            draw,
            pos['x'],
            pos['y'],
            dims['width'],
            dims['height'],
            dims['depth'],
            color=color,
            scale_x=scale,
            scale_y=scale,
            offset_x=container_margin,
            offset_y=image_height - container_margin
        )

        print(f"  ✓ {item['item_id']}: ({pos['x']:.0f}, {pos['y']:.0f}, {pos['z']:.0f})")

    # Add legend/stats
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
        small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
    except:
        font = ImageFont.load_default()
        small_font = ImageFont.load_default()

    # Title
    draw.text((20, 20), "TRUCK LOADING PLAN", fill=(0, 0, 0), font=font)

    # Stats
    y_offset = 60
    stats_text = [
        f"Container: {container['width']}×{container['height']}×{container['depth']} cm",
        f"Items: {stats['items_packed']} packed",
        f"Utilization: {stats['utilization']:.1f}%",
        f"Weight: {stats.get('total_weight_kg', 'N/A')} kg",
        f"Algorithm: {stats['algorithm']}",
        f"Computed in: {stats['computation_ms']}ms"
    ]

    for text in stats_text:
        draw.text((20, y_offset), text, fill=(0, 0, 0), font=small_font)
        y_offset += 25

    # Item legend
    legend_x = image_width - 300
    legend_y = 60
    draw.text((legend_x, 20), "ITEMS", fill=(0, 0, 0), font=font)

    for i, item in enumerate(items):
        color = colors[i % len(colors)]
        # Draw color box
        draw.rectangle(
            [legend_x, legend_y + i*30, legend_x + 20, legend_y + i*30 + 20],
            fill=color,
            outline=(0, 0, 0)
        )
        # Draw label
        dims = item['dimensions']
        label = f"{item['item_id']} ({dims['width']:.0f}×{dims['height']:.0f}×{dims['depth']:.0f})"
        draw.text((legend_x + 30, legend_y + i*30), label, fill=(0, 0, 0), font=small_font)

    # Save
    img.save(output_path, quality=95)
    print(f"\n✅ Visualization saved to: {output_path}")

    return output_path


def main():
    parser = argparse.ArgumentParser(description='Visualize truck loading plan')
    parser.add_argument('--truck-image', type=str, help='Path to truck image (optional)')
    parser.add_argument('--packing-data', type=str, default='/tmp/truck_loading_plan.json',
                       help='Path to packing JSON data')
    parser.add_argument('--output', type=str, default='/tmp/truck_loading_visualization.png',
                       help='Output image path')
    parser.add_argument('--width', type=int, default=1920, help='Image width')
    parser.add_argument('--height', type=int, default=1080, help='Image height')

    args = parser.parse_args()

    if not Path(args.packing_data).exists():
        print(f"❌ Packing data not found: {args.packing_data}")
        print("Run test_real_truck_packing.py first to generate packing data")
        sys.exit(1)

    print("=" * 70)
    print(" 3D TRUCK LOADING VISUALIZATION")
    print("=" * 70)

    output = create_loading_visualization(
        truck_image_path=args.truck_image,
        packing_data_path=args.packing_data,
        output_path=args.output,
        image_width=args.width,
        image_height=args.height
    )

    print("\n" + "=" * 70)
    print(f" ✅ DONE! Open {output} to see your loading plan")
    print("=" * 70)


if __name__ == "__main__":
    main()
