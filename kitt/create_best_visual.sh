#!/bin/bash
#
# Create Best Visual - One Command Solution
# Generates photorealistic truck loading visualization
#
# Usage:
#   ./create_best_visual.sh                    # Without truck image
#   ./create_best_visual.sh path/to/truck.png  # With truck image
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print functions
print_header() {
    echo -e "${BLUE}================================================================${NC}"
    echo -e "${BLUE} $1${NC}"
    echo -e "${BLUE}================================================================${NC}"
    echo
}

print_step() {
    echo
    echo -e "${GREEN}[Step $1]${NC} $2"
    echo -e "${BLUE}────────────────────────────────────────────────────────────────${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TRUCK_IMAGE="${1:-}"
OUTPUT_FILE="${2:-/tmp/truck_visualization_$(date +%Y%m%d_%H%M%S).png}"
PACKING_DATA="/tmp/truck_loading_plan.json"
RESOLUTION="${RESOLUTION:-3840x2160}"  # Default 4K
WIDTH=$(echo $RESOLUTION | cut -d'x' -f1)
HEIGHT=$(echo $RESOLUTION | cut -d'x' -f2)

print_header "CREATE BEST TRUCK LOADING VISUALIZATION"

echo "Configuration:"
echo "  Script directory: $SCRIPT_DIR"
echo "  Truck image: ${TRUCK_IMAGE:-None (will render 3D boxes only)}"
echo "  Output file: $OUTPUT_FILE"
echo "  Resolution: ${WIDTH}×${HEIGHT}"
echo

# Step 1: Check Blender
print_step 1 "Checking Blender Installation"

if command -v blender &> /dev/null; then
    BLENDER_VERSION=$(blender --version | head -1)
    print_success "Blender found: $BLENDER_VERSION"
else
    print_error "Blender not found!"
    echo
    echo "Please install Blender:"
    echo "  sudo apt-get update"
    echo "  sudo apt-get install -y blender"
    echo
    echo "Or download from: https://www.blender.org/download/"
    exit 1
fi

# Step 2: Check virtual environment
print_step 2 "Checking Python Environment"

if [ ! -d "$SCRIPT_DIR/venv" ]; then
    print_error "Virtual environment not found at $SCRIPT_DIR/venv"
    echo "Please create it first:"
    echo "  cd $SCRIPT_DIR"
    echo "  python3 -m venv venv"
    echo "  source venv/bin/activate"
    echo "  pip install -r requirements.txt"
    exit 1
fi

print_success "Virtual environment found"

# Activate virtual environment
source "$SCRIPT_DIR/venv/bin/activate"
print_success "Virtual environment activated"

# Step 3: Check truck image (if provided)
if [ -n "$TRUCK_IMAGE" ]; then
    print_step 3 "Checking Truck Image"

    if [ ! -f "$TRUCK_IMAGE" ]; then
        print_error "Truck image not found: $TRUCK_IMAGE"
        exit 1
    fi

    # Get absolute path
    TRUCK_IMAGE="$(readlink -f "$TRUCK_IMAGE")"

    FILE_SIZE=$(du -h "$TRUCK_IMAGE" | cut -f1)
    FILE_TYPE=$(file -b "$TRUCK_IMAGE")
    print_success "Truck image found: $TRUCK_IMAGE ($FILE_SIZE)"
    print_success "File type: $FILE_TYPE"
else
    print_step 3 "No Truck Image Provided"
    print_warning "Will render 3D boxes without truck background"
    print_warning "For best results, provide a truck image:"
    echo "  ./create_best_visual.sh /path/to/truck.png"
fi

# Step 4: Generate packing data
print_step 4 "Generating Packing Data with DeepPack3D"

echo "Running real 3D bin-packing algorithm..."
if python3 "$SCRIPT_DIR/tests/test_real_truck_packing.py"; then
    print_success "Packing complete!"
else
    print_error "Packing failed!"
    exit 1
fi

# Verify packing data
if [ ! -f "$PACKING_DATA" ]; then
    print_error "Packing data not found: $PACKING_DATA"
    exit 1
fi

# Show packing summary
echo
echo "Packing Summary:"
python3 -c "
import json
with open('$PACKING_DATA') as f:
    data = json.load(f)
    container = data['container']['dimensions']
    stats = data['stats']
    print(f\"  Container: {container['width']}×{container['height']}×{container['depth']} cm\")
    print(f\"  Items packed: {stats['items_packed']}\")
    print(f\"  Utilization: {stats['utilization']:.2f}%\")
    print(f\"  Algorithm: {stats['algorithm']}\")
    print(f\"  Computation: {stats['computation_ms']}ms\")
"

# Step 5: Create photorealistic render
print_step 5 "Creating Photorealistic Render with Blender"

echo "Resolution: ${WIDTH}×${HEIGHT}"
echo "This may take 30-60 seconds..."
echo

# Build Blender command
BLENDER_CMD="blender --background --python $SCRIPT_DIR/scripts/blender_truck_visualization.py --"
BLENDER_CMD="$BLENDER_CMD --packing-data $PACKING_DATA"
BLENDER_CMD="$BLENDER_CMD --output $OUTPUT_FILE"
BLENDER_CMD="$BLENDER_CMD --width $WIDTH"
BLENDER_CMD="$BLENDER_CMD --height $HEIGHT"

if [ -n "$TRUCK_IMAGE" ]; then
    BLENDER_CMD="$BLENDER_CMD --truck-image $TRUCK_IMAGE"
fi

# Execute Blender render
START_TIME=$(date +%s)

if eval $BLENDER_CMD; then
    END_TIME=$(date +%s)
    RENDER_TIME=$((END_TIME - START_TIME))
    print_success "Render complete in ${RENDER_TIME}s!"
else
    print_error "Render failed!"
    exit 1
fi

# Step 6: Verify output
print_step 6 "Verifying Output"

if [ ! -f "$OUTPUT_FILE" ]; then
    print_error "Output file not found: $OUTPUT_FILE"
    exit 1
fi

FILE_SIZE=$(du -h "$OUTPUT_FILE" | cut -f1)
FILE_TYPE=$(file -b "$OUTPUT_FILE")
IMAGE_INFO=$(identify "$OUTPUT_FILE" 2>/dev/null || echo "N/A")

print_success "Output file created: $OUTPUT_FILE"
print_success "File size: $FILE_SIZE"
print_success "File type: $FILE_TYPE"
if [ "$IMAGE_INFO" != "N/A" ]; then
    print_success "Image info: $IMAGE_INFO"
fi

# Summary
print_header "✅ SUCCESS!"

echo "Your photorealistic truck loading visualization is ready!"
echo
echo "📁 Output file: $OUTPUT_FILE"
echo "📐 Resolution: ${WIDTH}×${HEIGHT}"
echo "💾 Size: $FILE_SIZE"
echo

# Step 7: Open the image
print_step 7 "Opening Visualization"

if command -v xdg-open &> /dev/null; then
    echo "Opening image viewer..."
    xdg-open "$OUTPUT_FILE" &
    print_success "Image viewer launched"
elif command -v open &> /dev/null; then
    # macOS
    open "$OUTPUT_FILE" &
    print_success "Image viewer launched"
else
    print_warning "Could not auto-open image viewer"
    echo "Please open manually: $OUTPUT_FILE"
fi

# Next steps
echo
echo "🎯 Next Steps:"
echo
echo "1. View the visualization:"
echo "   xdg-open $OUTPUT_FILE"
echo
echo "2. Copy to desktop:"
echo "   cp $OUTPUT_FILE ~/Desktop/"
echo
echo "3. Create different resolutions:"
echo "   RESOLUTION=1920x1080 ./create_best_visual.sh $TRUCK_IMAGE  # 1080p"
echo "   RESOLUTION=7680x4320 ./create_best_visual.sh $TRUCK_IMAGE  # 8K"
echo
echo "4. Try with your truck image:"
echo "   ./create_best_visual.sh /path/to/your/truck.png"
echo
echo "5. Customize the render:"
echo "   Edit: scripts/blender_truck_visualization.py"
echo "   - Camera angle (line 58)"
echo "   - Truck transparency (line 75)"
echo "   - Box colors (line 324)"
echo "   - Lighting (line 192)"
echo

print_header "🎉 DONE!"

echo "You now have a professional-quality visualization ready for:"
echo "  • Investor pitches"
echo "  • Client proposals"
echo "  • Marketing materials"
echo "  • Website hero images"
echo "  • Trade show displays"
echo

exit 0
