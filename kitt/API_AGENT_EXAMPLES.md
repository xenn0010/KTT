# 🤖 API Agent Prompt Examples

**How to send prompts to Claude via the KITT API to trigger autonomous optimization**

---

## 🎯 API Endpoint for Agent Prompts

**Endpoint**: `POST /api/optimize`

This endpoint triggers the full autonomous agent workflow that:
1. Optimizes 3D packing (DeepPack3D)
2. Analyzes real weather (OpenWeatherMap)
3. Analyzes real traffic (TomTom)
4. Predicts damage risk (Claude AI)
5. Generates AI recommendations (Claude AI)
6. Stores in knowledge graph (Neo4j)

---

## 📝 Basic Request Format

```bash
curl -X POST http://localhost:8000/api/optimize \
  -H "Content-Type: application/json" \
  -d '{
    "shipment_id": "SH-ABC123",
    "truck_id": null,
    "include_ai_analysis": true,
    "store_in_graph": true
  }'
```

---

## 🚀 Complete Examples

### Example 1: Full Autonomous Optimization

```bash
# Step 1: Create shipment
curl -X POST http://localhost:8000/api/shipments \
  -H "Content-Type: application/json" \
  -d '{
    "origin": "Los Angeles",
    "destination": "New York",
    "items": [
      {"width": 50, "height": 40, "depth": 30, "weight": 25, "fragile": false, "stackable": true},
      {"width": 50, "height": 40, "depth": 30, "weight": 25, "fragile": false, "stackable": true},
      {"width": 50, "height": 40, "depth": 30, "weight": 25, "fragile": false, "stackable": true},
      {"width": 50, "height": 40, "depth": 30, "weight": 25, "fragile": false, "stackable": true},
      {"width": 50, "height": 40, "depth": 30, "weight": 25, "fragile": false, "stackable": true}
    ],
    "priority": "high",
    "deadline": "2025-11-25T00:00:00"
  }'

# Save the shipment_id from response

# Step 2: Trigger full agent optimization
curl -X POST http://localhost:8000/api/optimize \
  -H "Content-Type: application/json" \
  -d '{
    "shipment_id": "SH-ABC123",
    "include_ai_analysis": true,
    "store_in_graph": true
  }'
```

**Agent Response**:
```json
{
  "shipment_id": "SH-ABC123",
  "optimized_at": "2025-11-19T10:00:00",
  "packing": {
    "success": true,
    "plan_id": "PLAN-XYZ789",
    "truck_id": "TRK-001",
    "utilization_percentage": 85.2,
    "items_packed": 5,
    "packing_method": "deeppack3d-bl",
    "placements": [
      {
        "item_id": "SH-ABC123-ITEM-000",
        "position": {"x": 0, "y": 0, "z": 0},
        "dimensions": {"width": 50, "height": 40, "depth": 30},
        "rotation": 0,
        "bin_number": 1
      }
    ]
  },
  "route_conditions": {
    "route_id": "ROUTE-SH-ABC123",
    "origin": "Los Angeles",
    "destination": "New York",
    "current_weather": {
      "condition": "clear",
      "temperature": 50.05,
      "humidity": 65
    },
    "weather_severity": 2,
    "current_traffic": {
      "level": "low",
      "delay_minutes": 0
    },
    "road_quality": {
      "score": 10.0,
      "surface_condition": "excellent"
    }
  },
  "risk_assessment": {
    "risk_level": "LOW",
    "risk_score": 15,
    "risk_factors": [
      "Good weather conditions",
      "Low traffic congestion",
      "Standard cargo handling"
    ],
    "recommendations": [
      "Standard packing procedures sufficient",
      "No special handling required",
      "Optimal conditions for dispatch"
    ]
  },
  "ai_analysis": {
    "loading_strategy": "Heavy items on bottom, distribute weight evenly",
    "special_handling_items": [],
    "truck_selection_criteria": [
      "Standard box truck sufficient",
      "No climate control required"
    ]
  },
  "graph_storage": {
    "status": "success",
    "shipment_stored": true,
    "items_added": 5,
    "relationships_created": 7
  },
  "summary": {
    "utilization": 85.2,
    "risk_level": "LOW",
    "weather_severity": 2,
    "traffic_level": "low",
    "ready_for_dispatch": true
  }
}
```

---

### Example 2: Critical Fragile Shipment

```bash
# Create fragile cargo shipment
curl -X POST http://localhost:8000/api/shipments \
  -H "Content-Type: application/json" \
  -d '{
    "origin": "Chicago",
    "destination": "Miami",
    "items": [
      {"width": 100, "height": 80, "depth": 60, "weight": 50, "fragile": true, "stackable": false, "description": "Fragile Electronics"},
      {"width": 100, "height": 80, "depth": 60, "weight": 50, "fragile": true, "stackable": false, "description": "Fragile Glass"},
      {"width": 80, "height": 60, "depth": 40, "weight": 30, "fragile": true, "stackable": false, "description": "Medical Equipment"}
    ],
    "priority": "critical",
    "deadline": "2025-11-22T00:00:00"
  }'

# Optimize with full agent analysis
curl -X POST http://localhost:8000/api/optimize \
  -H "Content-Type: application/json" \
  -d '{
    "shipment_id": "SH-FRAGILE123",
    "include_ai_analysis": true,
    "store_in_graph": true
  }'
```

**Agent Response for Fragile Cargo**:
```json
{
  "risk_assessment": {
    "risk_level": "MEDIUM",
    "risk_score": 45,
    "risk_factors": [
      "Multiple fragile items",
      "Weather severity moderate",
      "Critical priority deadline"
    ],
    "recommendations": [
      "Use extra padding for all fragile items",
      "Place fragile items on top layer only",
      "Consider climate-controlled truck",
      "Avoid peak traffic hours",
      "Monitor weather forecast closely"
    ]
  },
  "ai_analysis": {
    "loading_strategy": "Fragile items must be loaded last, placed on top. NO stacking on fragile boxes. Secure with additional padding and straps.",
    "special_handling_items": [
      "Item SH-FRAGILE123-ITEM-000: Fragile Electronics - Handle with extreme care",
      "Item SH-FRAGILE123-ITEM-001: Fragile Glass - Vertical orientation only",
      "Item SH-FRAGILE123-ITEM-002: Medical Equipment - Temperature sensitive"
    ],
    "truck_selection_criteria": [
      "Climate-controlled box truck required",
      "Air suspension recommended",
      "Maximum speed: 55mph due to fragile cargo"
    ]
  },
  "summary": {
    "utilization": 21.5,
    "risk_level": "MEDIUM",
    "weather_severity": 3,
    "traffic_level": "medium",
    "ready_for_dispatch": false,
    "blocking_issues": [
      "Weather forecast shows thunderstorms in 6 hours",
      "Recommend delaying dispatch until weather clears"
    ]
  }
}
```

---

### Example 3: Optimize Without AI (Faster)

```bash
# Quick optimization without AI analysis
curl -X POST http://localhost:8000/api/optimize \
  -H "Content-Type: application/json" \
  -d '{
    "shipment_id": "SH-ABC123",
    "include_ai_analysis": false,
    "store_in_graph": false
  }'
```

**Response** (faster, no AI):
```json
{
  "packing": {
    "utilization_percentage": 85.2,
    "items_packed": 5
  },
  "route_conditions": {
    "current_weather": {"temperature": 50.05},
    "weather_severity": 2,
    "current_traffic": {"level": "low"}
  },
  "risk_assessment": {
    "risk_level": "LOW",
    "risk_score": 15
  },
  "summary": {
    "utilization": 85.2,
    "risk_level": "LOW",
    "ready_for_dispatch": true
  }
}
```

---

### Example 4: Check Only Packing (No Weather/Risk)

```bash
# Just 3D bin packing optimization
curl -X POST http://localhost:8000/api/packing/SH-ABC123 \
  -H "Content-Type: application/json" \
  -d '{
    "truck_id": "TRK-001"
  }'
```

**Response**:
```json
{
  "success": true,
  "plan_id": "PLAN-XYZ789",
  "truck_id": "TRK-001",
  "utilization": 85.2,
  "utilization_percentage": 85.2,
  "items_packed": 5,
  "packing_method": "deeppack3d-bl",
  "placements": [...],
  "bins_used": 1,
  "computation_time_ms": 5
}
```

---

### Example 5: Get Route Conditions Only

```bash
# Check weather and traffic without full optimization
curl -X GET "http://localhost:8000/api/route-conditions?origin=Los%20Angeles&destination=New%20York"
```

**Response**:
```json
{
  "route_id": "ROUTE-LA-NYC",
  "origin": "Los Angeles",
  "destination": "New York",
  "current_weather": {
    "condition": "clear",
    "temperature": 50.05,
    "wind_speed": 5
  },
  "destination_weather": {
    "condition": "cloudy",
    "temperature": 42
  },
  "weather_severity": 2,
  "weather_warnings": [],
  "current_traffic": {
    "level": "low",
    "delay_minutes": 0
  },
  "road_quality": {
    "score": 10.0,
    "surface_condition": "excellent"
  }
}
```

---

### Example 6: Get AI Risk Prediction Only

```bash
# Get damage risk prediction without full optimization
curl -X POST http://localhost:8000/api/risk/SH-ABC123 \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Response**:
```json
{
  "risk_level": "LOW",
  "risk_score": 15,
  "risk_factors": [
    "No severe weather conditions",
    "Low traffic congestion",
    "Standard cargo characteristics"
  ],
  "recommendations": [
    "Standard packing procedures sufficient",
    "No special handling required",
    "Optimal conditions for dispatch"
  ]
}
```

---

### Example 7: Get AI Loading Recommendations Only

```bash
# Get AI-powered shipment analysis
curl -X POST http://localhost:8000/api/analyze/SH-ABC123 \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Response**:
```json
{
  "loading_strategy": "Heavy items on bottom, distribute weight evenly across truck bed. Secure all items with straps.",
  "special_handling_items": [
    "Item SH-ABC123-ITEM-002: Fragile - Handle with care"
  ],
  "truck_selection_criteria": [
    "Standard box truck sufficient",
    "Minimum capacity: 500 cubic feet",
    "No special requirements"
  ]
}
```

---

## 🔄 Frontend Integration Example (JavaScript)

### Complete Workflow

```javascript
// Frontend code to optimize a shipment
async function optimizeShipment(shipmentData) {
  const API_BASE = 'http://localhost:8000';

  try {
    // Step 1: Create shipment
    const createResponse = await fetch(`${API_BASE}/api/shipments`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(shipmentData)
    });
    const shipment = await createResponse.json();
    console.log('✅ Shipment created:', shipment.shipment_id);

    // Step 2: Trigger full agent optimization
    const optimizeResponse = await fetch(`${API_BASE}/api/optimize`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        shipment_id: shipment.shipment_id,
        include_ai_analysis: true,
        store_in_graph: true
      })
    });
    const optimization = await optimizeResponse.json();

    // Step 3: Display results
    console.log('📦 Packing:', optimization.packing.utilization_percentage + '%');
    console.log('🌤️  Weather:', optimization.route_conditions.current_weather.temperature + '°F');
    console.log('⚠️  Risk:', optimization.risk_assessment.risk_level);
    console.log('🤖 AI Recommendations:', optimization.ai_analysis.loading_strategy);

    // Step 4: Check if ready to dispatch
    if (optimization.summary.ready_for_dispatch) {
      console.log('🚀 Ready for dispatch!');
      return {
        status: 'ready',
        shipment_id: shipment.shipment_id,
        utilization: optimization.summary.utilization,
        risk_level: optimization.summary.risk_level
      };
    } else {
      console.log('⏸️  Not ready:', optimization.summary.blocking_issues);
      return {
        status: 'blocked',
        issues: optimization.summary.blocking_issues
      };
    }

  } catch (error) {
    console.error('❌ Optimization failed:', error);
    throw error;
  }
}

// Usage
const shipmentData = {
  origin: 'Los Angeles',
  destination: 'New York',
  items: [
    {width: 50, height: 40, depth: 30, weight: 25, fragile: false, stackable: true}
  ],
  priority: 'high'
};

optimizeShipment(shipmentData)
  .then(result => console.log('Result:', result));
```

---

## 🎯 Request Parameters

### `/api/optimize` Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `shipment_id` | string | Yes | - | The shipment to optimize |
| `truck_id` | string | No | null | Specific truck (auto-select if null) |
| `include_ai_analysis` | boolean | No | false | Include Claude AI recommendations |
| `store_in_graph` | boolean | No | false | Store in Neo4j knowledge graph |

---

## 📊 Response Fields Explained

### Packing
- `utilization_percentage`: How full the truck is (0-100%)
- `packing_method`: Algorithm used (deeppack3d-bl)
- `placements`: 3D coordinates for each item

### Route Conditions
- `current_weather`: Real weather from OpenWeatherMap
- `weather_severity`: Scale 1-5 (1=excellent, 5=severe)
- `current_traffic`: Real traffic from TomTom (with fallback)
- `road_quality`: Score 0-10 based on weather/traffic

### Risk Assessment
- `risk_level`: LOW/MEDIUM/HIGH/CRITICAL
- `risk_score`: 0-100 damage risk score
- `risk_factors`: List of risk contributors
- `recommendations`: AI-generated safety tips

### AI Analysis (if `include_ai_analysis: true`)
- `loading_strategy`: How to load the truck
- `special_handling_items`: Items needing extra care
- `truck_selection_criteria`: Truck requirements

### Summary
- `ready_for_dispatch`: Boolean - safe to go
- `blocking_issues`: Array of problems (if any)

---

## ⚡ Performance

| Endpoint | Avg Time | Notes |
|----------|----------|-------|
| `/api/optimize` (no AI) | ~500ms | Packing + Weather + Traffic |
| `/api/optimize` (with AI) | ~15s | Includes 2 Claude API calls |
| `/api/packing/{id}` | ~10ms | DeepPack3D only |
| `/api/route-conditions` | ~300ms | Weather + Traffic APIs |
| `/api/risk/{id}` | ~10s | Claude AI analysis |
| `/api/analyze/{id}` | ~10s | Claude AI analysis |

---

## 🔧 Error Handling

```javascript
async function optimizeWithErrorHandling(shipmentId) {
  try {
    const response = await fetch('http://localhost:8000/api/optimize', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        shipment_id: shipmentId,
        include_ai_analysis: true,
        store_in_graph: true
      })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail);
    }

    return await response.json();

  } catch (error) {
    console.error('Optimization failed:', error.message);

    // Handle specific errors
    if (error.message.includes('not found')) {
      console.error('Shipment does not exist');
    } else if (error.message.includes('already exists')) {
      console.log('Shipment already in knowledge graph');
    }

    throw error;
  }
}
```

---

## ✅ Summary

**To optimize a shipment via API**:
1. Create shipment: `POST /api/shipments`
2. Optimize: `POST /api/optimize` with `shipment_id`
3. Get comprehensive results including:
   - 3D packing (DeepPack3D)
   - Real weather (OpenWeatherMap)
   - Real traffic (TomTom)
   - AI risk prediction (Claude)
   - AI recommendations (Claude)
   - Knowledge graph storage (Neo4j)

**One API call triggers the entire autonomous agent workflow!** 🚀
