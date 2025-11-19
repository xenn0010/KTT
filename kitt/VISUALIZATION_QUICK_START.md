# Truck Loading Visualization - Quick Start

## Step 1: Generate Packing Data

```bash
cd /home/yab/KTT/kitt
source venv/bin/activate
python3 tests/test_real_truck_packing.py
```

Output: `/tmp/truck_loading_plan.json`

---

## Step 2: Choose Your Visualization Method

### Option 1: Quick Isometric View (PIL - 5 seconds)

**Best for**: Quick previews, no dependencies

```bash
python3 scripts/visualize_truck_loading.py
# Output: /tmp/truck_loading_visualization.png
```

**With your truck image:**
```bash
python3 scripts/visualize_truck_loading.py --truck-image /path/to/truck.png
```

---

### Option 2: Perspective Overlay (PIL - 10 seconds)

**Best for**: Exact matching to your truck photo perspective

```bash
# First, calibrate your truck image
python3 scripts/overlay_boxes_on_truck.py \
    --truck-image /path/to/truck.png \
    --calibrate

# Then overlay boxes
python3 scripts/overlay_boxes_on_truck.py \
    --truck-image /path/to/truck.png \
    --calibration-file truck.calib.json
# Output: /tmp/truck_with_boxes.png
```

---

### Option 3: Blender Photorealistic (30-60 seconds)

**Best for**: Professional presentations, marketing materials

```bash
# Install Blender first (one time)
sudo apt-get install blender

# Render with truck background
blender --background --python scripts/blender_truck_visualization.py -- \
    --truck-image /path/to/truck.png \
    --packing-data /tmp/truck_loading_plan.json \
    --output /tmp/truck_blender_render.png
# Output: /tmp/truck_blender_render.png
```

**Features:**
- Photorealistic lighting and materials
- Truck image as camera background (50% transparency)
- Metallic box materials with beveled edges
- Optional text labels above each item

---

### Option 4: Interactive 3D Viewer (Web - instant)

**Best for**: Exploring packing from all angles, client demos

```bash
# Save this HTML (already in the guide), then:
cd /home/yab/KTT/kitt
python3 -m http.server 8080

# Open browser: http://localhost:8080/truck_viewer.html
```

**Features:**
- Rotate, zoom, pan with mouse
- Real-time 3D rendering
- Color-coded items with stats
- No installation needed (runs in browser)

---

## Comparison Table

| Method | Time | Quality | Use Case | Truck Image |
|--------|------|---------|----------|-------------|
| Option 1: PIL Isometric | 5s | Good | Quick preview | Background |
| Option 2: PIL Overlay | 10s | Good | Exact match | Overlay |
| Option 3: Blender | 60s | Excellent | Marketing | Background |
| Option 4: Three.js | Instant | Good | Interactive | No |

---

## Example Workflow

```bash
# 1. Test packing algorithm
python3 tests/test_real_truck_packing.py

# 2. Quick preview
python3 scripts/visualize_truck_loading.py

# 3. For client presentation, use Blender
blender --background --python scripts/blender_truck_visualization.py -- \
    --truck-image client_truck.png \
    --packing-data /tmp/truck_loading_plan.json \
    --output presentation_render.png \
    --width 3840 \
    --height 2160  # 4K resolution

# 4. For interactive demo, serve Three.js viewer
python3 -m http.server 8080
# Then open browser to localhost:8080/truck_viewer.html
```

---

## All Scripts Location

```
kitt/
├── scripts/
│   ├── visualize_truck_loading.py      # Option 1: PIL isometric
│   ├── overlay_boxes_on_truck.py       # Option 2: PIL overlay
│   └── blender_truck_visualization.py  # Option 3: Blender render
├── tests/
│   └── test_real_truck_packing.py      # Generate packing data
└── TRUCK_VISUALIZATION_GUIDE.md        # Full documentation
```

---

## FAQ

**Q: Which method should I use?**
- For quick testing: Option 1
- For exact truck match: Option 2
- For presentations: Option 3
- For interactive demos: Option 4

**Q: Can I overlay boxes directly on my truck photo?**
- Yes! Use Option 2 with calibration, or Option 3 (Blender) with truck as background

**Q: How do I change box colors?**
- Edit the `colors` array in any of the scripts

**Q: Can I export to CAD software?**
- Yes! See TRUCK_VISUALIZATION_GUIDE.md for DXF export example

**Q: Does this work with real trucks?**
- Yes! Tested with 20ft container (589×235×239 cm)
- Automatically scales to fit DeepPack3D's limits
- All coordinates are in real centimeters

---

**Status**: All 4 visualization methods are production-ready and tested!
