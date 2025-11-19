"""
Blender Script for Photorealistic Truck Loading Visualization
Renders 3D boxes onto truck image with proper lighting and perspective

Usage:
    blender --background --python blender_truck_visualization.py -- \
        --truck-image /path/to/truck.png \
        --packing-data /tmp/truck_loading_plan.json \
        --output /tmp/truck_rendered.png

Or run inside Blender:
    1. Open Blender
    2. Go to Scripting tab
    3. Open this file
    4. Modify paths at bottom
    5. Run script
"""

import bpy
import json
import sys
import math
from pathlib import Path
from mathutils import Vector, Euler


def clear_scene():
    """Remove all objects from scene"""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)


def setup_camera(truck_image_path, image_width=1920, image_height=1080):
    """
    Setup camera with truck image as background

    Args:
        truck_image_path: Path to truck PNG
        image_width: Output width
        image_height: Output height

    Returns:
        camera object
    """
    # Create camera
    bpy.ops.object.camera_add(location=(500, -800, 400))
    camera = bpy.context.active_object
    camera.name = "TruckCamera"

    # Set as active camera
    bpy.context.scene.camera = camera

    # Camera settings
    camera.data.lens = 50  # 50mm lens
    camera.data.sensor_width = 36

    # Point camera at container center
    camera.rotation_euler = Euler((math.radians(60), 0, math.radians(45)), 'XYZ')

    # Setup render settings
    scene = bpy.context.scene
    scene.render.resolution_x = image_width
    scene.render.resolution_y = image_height
    scene.render.resolution_percentage = 100

    # Load truck image as background
    if truck_image_path and Path(truck_image_path).exists():
        # Load image
        img = bpy.data.images.load(truck_image_path)

        # Set as camera background
        camera.data.show_background_images = True
        bg = camera.data.background_images.new()
        bg.image = img
        bg.alpha = 0.5  # 50% transparency to see both truck and boxes

        print(f"✅ Loaded truck background: {truck_image_path}")
    else:
        print(f"⚠️  Truck image not found, rendering boxes only")

    return camera


def create_container_outline(width, height, depth):
    """
    Create wireframe outline of container

    Args:
        width, height, depth: Container dimensions in cm

    Returns:
        container object
    """
    # Create cube
    bpy.ops.mesh.primitive_cube_add(size=1, location=(width/2, depth/2, height/2))
    container = bpy.context.active_object
    container.name = "Container"

    # Scale to container size
    container.scale = (width/2, depth/2, height/2)

    # Make it wireframe
    bpy.ops.object.modifier_add(type='WIREFRAME')
    container.modifiers["Wireframe"].thickness = 0.5

    # Material
    mat = bpy.data.materials.new(name="ContainerMaterial")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()

    # Add emission shader for visibility
    output = nodes.new('ShaderNodeOutputMaterial')
    emission = nodes.new('ShaderNodeEmission')
    emission.inputs[0].default_value = (0.5, 0.5, 0.5, 1.0)  # Gray
    emission.inputs[1].default_value = 1.0  # Strength

    mat.node_tree.links.new(emission.outputs[0], output.inputs[0])
    container.data.materials.append(mat)

    return container


def create_box(item_id, position, dimensions, color):
    """
    Create a 3D box for cargo item

    Args:
        item_id: Item identifier
        position: Dict with x, y, z
        dimensions: Dict with width, height, depth
        color: RGB tuple (0-1 range)

    Returns:
        box object
    """
    # Create cube
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=(
            position['x'] + dimensions['width']/2,
            position['z'] + dimensions['depth']/2,  # Z becomes Y in Blender
            position['y'] + dimensions['height']/2   # Y becomes Z in Blender
        )
    )

    box = bpy.context.active_object
    box.name = item_id

    # Scale to box dimensions
    box.scale = (
        dimensions['width']/2,
        dimensions['depth']/2,
        dimensions['height']/2
    )

    # Create material with color
    mat = bpy.data.materials.new(name=f"Material_{item_id}")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()

    # Create shader nodes
    output = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')

    # Set color and properties
    bsdf.inputs[0].default_value = (*color, 1.0)  # Base Color
    bsdf.inputs[4].default_value = 0.5  # Metallic
    bsdf.inputs[7].default_value = 0.2  # Roughness
    bsdf.inputs[12].default_value = 0.0  # Clearcoat
    bsdf.inputs[18].default_value = (*color, 1.0)  # Emission
    bsdf.inputs[19].default_value = 0.2  # Emission Strength

    # Connect nodes
    mat.node_tree.links.new(bsdf.outputs[0], output.inputs[0])

    # Assign material
    box.data.materials.append(mat)

    # Add edge highlighting
    bpy.ops.object.modifier_add(type='BEVEL')
    box.modifiers["Bevel"].width = 0.5
    box.modifiers["Bevel"].segments = 2

    return box


def setup_lighting():
    """Setup professional lighting for the scene"""
    # Sun light (key light)
    bpy.ops.object.light_add(type='SUN', location=(0, 0, 1000))
    sun = bpy.context.active_object
    sun.data.energy = 2.0
    sun.rotation_euler = Euler((math.radians(45), 0, math.radians(45)), 'XYZ')

    # Area light (fill light)
    bpy.ops.object.light_add(type='AREA', location=(-500, -500, 500))
    fill = bpy.context.active_object
    fill.data.energy = 500
    fill.data.size = 200

    # Rim light
    bpy.ops.object.light_add(type='AREA', location=(500, 500, 300))
    rim = bpy.context.active_object
    rim.data.energy = 300
    rim.data.size = 150


def setup_render_settings(output_path):
    """
    Configure render settings for high quality output

    Args:
        output_path: Where to save rendered image
    """
    scene = bpy.context.scene

    # Use Cycles for photorealistic rendering
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 128  # Increase for better quality (slower)
    scene.cycles.use_denoising = True

    # Or use EEVEE for faster rendering
    # scene.render.engine = 'BLENDER_EEVEE'
    # scene.eevee.taa_render_samples = 64

    # Output settings
    scene.render.filepath = output_path
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    scene.render.film_transparent = False  # Set True for transparent background

    # Quality
    scene.render.image_settings.quality = 95
    scene.render.image_settings.compression = 15


def add_text_labels(items):
    """
    Add text labels for each item

    Args:
        items: List of packing items
    """
    for item in items:
        pos = item['position']
        dims = item['dimensions']

        # Create text
        bpy.ops.object.text_add(
            location=(
                pos['x'] + dims['width']/2,
                pos['z'] + dims['depth']/2,
                pos['y'] + dims['height'] + 10  # 10cm above box
            )
        )

        text = bpy.context.active_object
        text.data.body = item['item_id']
        text.data.size = 15
        text.data.align_x = 'CENTER'

        # Text material
        mat = bpy.data.materials.new(name=f"TextMat_{item['item_id']}")
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        emission = nodes.get('Emission') or nodes.new('ShaderNodeEmission')
        emission.inputs[0].default_value = (1, 1, 1, 1)  # White
        emission.inputs[1].default_value = 2.0
        text.data.materials.append(mat)


def create_visualization(
    truck_image_path,
    packing_data_path,
    output_path,
    image_width=1920,
    image_height=1080,
    add_labels=True
):
    """
    Main function to create Blender visualization

    Args:
        truck_image_path: Path to truck PNG
        packing_data_path: Path to JSON packing data
        output_path: Where to save rendered image
        image_width: Output width
        image_height: Output height
        add_labels: Whether to add text labels
    """
    print("=" * 70)
    print(" BLENDER TRUCK LOADING VISUALIZATION")
    print("=" * 70)

    # Load packing data
    with open(packing_data_path) as f:
        data = json.load(f)

    container = data['container']['dimensions']
    items = data['items']

    print(f"\nContainer: {container['width']}×{container['height']}×{container['depth']} cm")
    print(f"Items: {len(items)}")

    # Clear scene
    clear_scene()

    # Setup camera
    camera = setup_camera(truck_image_path, image_width, image_height)

    # Create container outline
    create_container_outline(
        container['width'],
        container['height'],
        container['depth']
    )

    # Setup lighting
    setup_lighting()

    # Color palette (convert to 0-1 range)
    colors = [
        (1.0, 0.2, 0.2),   # Red
        (0.2, 1.0, 0.2),   # Green
        (0.2, 0.2, 1.0),   # Blue
        (1.0, 1.0, 0.2),   # Yellow
        (1.0, 0.2, 1.0),   # Magenta
        (0.2, 1.0, 1.0),   # Cyan
        (1.0, 0.6, 0.2),   # Orange
        (0.6, 0.2, 1.0),   # Purple
    ]

    # Create boxes
    print("\nCreating 3D boxes...")
    for i, item in enumerate(items):
        color = colors[i % len(colors)]
        box = create_box(
            item['item_id'],
            item['position'],
            item['dimensions'],
            color
        )
        print(f"  ✓ {item['item_id']}")

    # Add labels
    if add_labels:
        print("\nAdding labels...")
        add_text_labels(items)

    # Setup render
    setup_render_settings(output_path)

    # Render
    print(f"\nRendering to: {output_path}")
    print("This may take 30-60 seconds...")

    bpy.ops.render.render(write_still=True)

    print(f"\n✅ Render complete: {output_path}")

    return output_path


def parse_args():
    """Parse command line arguments when run from command line"""
    import argparse

    # Get arguments after '--'
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        argv = []

    parser = argparse.ArgumentParser(description='Blender truck visualization')
    parser.add_argument('--truck-image', help='Path to truck PNG')
    parser.add_argument('--packing-data', default='/tmp/truck_loading_plan.json',
                       help='Path to packing JSON')
    parser.add_argument('--output', default='/tmp/truck_blender_render.png',
                       help='Output image path')
    parser.add_argument('--width', type=int, default=1920, help='Image width')
    parser.add_argument('--height', type=int, default=1080, help='Image height')
    parser.add_argument('--no-labels', action='store_true', help='Skip text labels')

    return parser.parse_args(argv)


# Main execution
if __name__ == "__main__":
    # Check if running in Blender
    try:
        import bpy
        print("✅ Running in Blender")
    except ImportError:
        print("❌ This script must be run in Blender!")
        print("Usage: blender --background --python blender_truck_visualization.py -- [args]")
        sys.exit(1)

    args = parse_args()

    # Run visualization
    create_visualization(
        truck_image_path=args.truck_image,
        packing_data_path=args.packing_data,
        output_path=args.output,
        image_width=args.width,
        image_height=args.height,
        add_labels=not args.no_labels
    )

    print("\n" + "=" * 70)
    print(" ✅ DONE!")
    print("=" * 70)
