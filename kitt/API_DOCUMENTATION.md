# KITT REST API Documentation

**Version**: 1.0.0
**Base URL**: `http://localhost:8000`
**Interactive Docs**: `http://localhost:8000/docs`
**Alternative Docs**: `http://localhost:8000/redoc`

---

## 🚀 Quick Start

### Start the API Server
```bash
cd /home/yab/KTT/kitt
source venv/bin/activate
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000` with:
- ✅ **REST API** endpoints for all freight operations
- ✅ **WebSocket** endpoints for real-time updates
- ✅ **Interactive API docs** at `/docs`
- ✅ **CORS enabled** for frontend integration

---

## 📚 API Endpoints

### 1. Health & Status

#### `GET /`
Root endpoint with API information

**Response**:
```json
{
  "name": "KITT - AI Freight Optimizer",
  "version": "1.0.0",
  "status": "operational",
  "endpoints": {
    "websocket": {...},
    "rest": {...}
  }
}
```

#### `GET /health`
Comprehensive health check

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2025-11-19T10:00:00",
  "services": {
    "database": "operational",
    "neo4j": "operational"
  }
}
```

---

### 2. Shipment Management

#### `POST /api/shipments`
Create a new shipment

**Request Body**:
```json
{
  "origin": "Los Angeles",
  "destination": "New York",
  "items": [
    {
      "width": 50,
      "height": 40,
      "depth": 30,
      "weight": 25,
      "fragile": false,
      "stackable": true,
      "description": "Electronics"
    }
  ],
  "priority": "high",
  "deadline": "2025-11-22T00:00:00"
}
```

**Response** (201 Created):
```json
{
  "success": true,
  "shipment_id": "SH-ABC123",
  "origin": "Los Angeles",
  "destination": "New York",
  "items_count": 1,
  "priority": "high"
}
```

#### `GET /api/shipments/{shipment_id}`
Get shipment by ID

**Response**:
```json
{
  "shipment_id": "SH-ABC123",
  "origin": "Los Angeles",
  "destination": "New York",
  "status": "pending",
  "priority": "high",
  "items": [...],
  "created_at": "2025-11-19T10:00:00"
}
```

#### `GET /api/shipments`
List all shipments with optional filters

**Query Parameters**:
- `status`: `pending|packed|in_transit|delivered|cancelled`
- `priority`: `low|medium|high|critical`
- `limit`: Number of results (default: 100, max: 1000)

**Response**:
```json
{
  "count": 10,
  "shipments": [...]
}
```

#### `GET /api/shipments/{shipment_id}/items`
Get all items for a shipment

**Response**:
```json
{
  "shipment_id": "SH-ABC123",
  "count": 5,
  "items": [...]
}
```

#### `DELETE /api/shipments/{shipment_id}`
Delete a shipment

**Response**:
```json
{
  "success": true,
  "shipment_id": "SH-ABC123"
}
```

---

### 3. Optimization & Packing

#### `POST /api/optimize`
**MOST POWERFUL ENDPOINT** - Full autonomous optimization

**Request Body**:
```json
{
  "shipment_id": "SH-ABC123",
  "truck_id": null,
  "include_ai_analysis": true,
  "store_in_graph": true
}
```

**What It Does**:
1. ✅ 3D bin packing with DeepPack3D
2. ✅ Real weather analysis (OpenWeatherMap)
3. ✅ Real traffic analysis (TomTom)
4. ✅ AI damage risk prediction
5. ✅ AI shipment analysis
6. ✅ Knowledge graph storage

**Response**:
```json
{
  "shipment_id": "SH-ABC123",
  "optimized_at": "2025-11-19T10:00:00",
  "packing": {
    "utilization_percentage": 85.2,
    "items_packed": 10,
    "packing_method": "deeppack3d-bl",
    "placements": [...]
  },
  "route_conditions": {
    "current_weather": {
      "condition": "clear",
      "temperature": 72
    },
    "weather_severity": 1,
    "current_traffic": {
      "level": "low",
      "delay_minutes": 0
    }
  },
  "risk_assessment": {
    "risk_level": "LOW",
    "risk_score": 15
  },
  "ai_analysis": {...},
  "graph_storage": {...},
  "summary": {
    "utilization": 85.2,
    "risk_level": "LOW",
    "ready_for_dispatch": true
  }
}
```

#### `POST /api/packing/{shipment_id}`
3D bin packing only

**Request Body** (optional):
```json
{
  "truck_id": "TRK-001"
}
```

**Response**:
```json
{
  "success": true,
  "plan_id": "PLAN-XYZ789",
  "truck_id": "TRK-001",
  "utilization_percentage": 85.2,
  "items_packed": 10,
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
}
```

#### `GET /api/route-conditions`
Get route conditions with REAL APIs

**Query Parameters**:
- `origin`: Origin city (required)
- `destination`: Destination city (required)

**Response**:
```json
{
  "route_id": "ROUTE-LA-NYC",
  "origin": "Los Angeles",
  "destination": "New York",
  "current_weather": {
    "condition": "clear",
    "temperature": 72,
    "wind_speed": 5
  },
  "destination_weather": {...},
  "weather_severity": 1,
  "weather_warnings": [],
  "current_traffic": {
    "level": "low",
    "delay_minutes": 0,
    "incidents": []
  },
  "road_quality": {
    "score": 10.0,
    "surface_condition": "excellent"
  }
}
```

#### `POST /api/risk/{shipment_id}`
Predict damage risk with AI

**Response**:
```json
{
  "risk_level": "LOW",
  "risk_score": 15,
  "risk_factors": [
    "No severe weather conditions",
    "Low traffic congestion"
  ],
  "recommendations": [
    "Standard packing procedures sufficient",
    "No special handling required"
  ]
}
```

#### `POST /api/analyze/{shipment_id}`
AI-powered shipment analysis (Claude API)

**Response**:
```json
{
  "loading_strategy": "Heavy items on bottom, fragile on top",
  "special_handling_items": ["Item-002: Fragile electronics"],
  "truck_selection_criteria": [
    "Requires climate control",
    "Minimum 500 cubic feet"
  ]
}
```

---

### 4. Knowledge Graph

#### `GET /api/graph/shipment/{shipment_id}`
Get complete knowledge graph view

**Response**:
```json
{
  "shipment": {...},
  "items": [...],
  "origin": {"name": "Los Angeles"},
  "destination": {"name": "New York"},
  "similar_shipments": [...]
}
```

#### `GET /api/graph/location/{location_name}`
Get location analytics

**Response**:
```json
{
  "location": "Los Angeles",
  "shipments_originated": 50,
  "shipments_received": 30,
  "total_freight_volume": 125000
}
```

#### `GET /api/graph/patterns`
Find historical patterns

**Query Parameters**:
- `origin`: Origin city
- `destination`: Destination city

**Response**:
```json
{
  "origin": "Los Angeles",
  "destination": "New York",
  "patterns": [
    {
      "shipment_id": "SH-XYZ",
      "utilization": 87.5,
      "delivery_time_hours": 48
    }
  ]
}
```

#### `GET /api/graph/network`
Get network overview

**Response**:
```json
{
  "total_shipments": 100,
  "total_locations": 25,
  "total_items": 500,
  "total_trucks": 15
}
```

#### `GET /api/graph/trucks/optimal`
Find optimal trucks from knowledge graph

**Query Parameters**:
- `weight`: Total weight in kg (required)
- `volume`: Total volume in cm³ (required)
- `origin`: Origin location (required)

**Response**:
```json
{
  "trucks": [
    {
      "truck_id": "TRK-001",
      "type": "box_truck",
      "max_weight": 5000,
      "capacity_volume": 1000000
    }
  ],
  "count": 1
}
```

#### `POST /api/graph/query`
Execute custom Cypher query

**Request Body**:
```json
{
  "query": "MATCH (s:Shipment) WHERE s.priority = 'high' RETURN s LIMIT 10",
  "parameters": {}
}
```

**Response**:
```json
{
  "query": "MATCH...",
  "results": [...]
}
```

---

### 5. Analytics

#### `GET /api/analytics/dashboard`
Complete dashboard statistics

**Response**:
```json
{
  "total_shipments": 100,
  "network": {...},
  "generated_at": "2025-11-19T10:00:00",
  "by_status": {
    "pending": 20,
    "packed": 30,
    "in_transit": 40,
    "delivered": 10
  },
  "by_priority": {
    "low": 10,
    "medium": 50,
    "high": 30,
    "critical": 10
  }
}
```

#### `GET /api/analytics/utilization`
Packing utilization statistics

**Response**:
```json
{
  "average_utilization": 82.5,
  "min_utilization": 45.0,
  "max_utilization": 98.0,
  "total_plans": 50,
  "recent_plans": [...]
}
```

#### `GET /api/analytics/performance`
System performance metrics

**Response**:
```json
{
  "total_optimizations": 50,
  "avg_computation_time_ms": 3.5,
  "min_computation_time_ms": 1.2,
  "max_computation_time_ms": 8.9
}
```

---

## 🔌 WebSocket Endpoints

### `WS /ws/freight?client_id={id}`
Real-time freight data updates

**Message Types**:
- `shipment_request`
- `route_update`
- `heartbeat`

### `WS /ws/packing?client_id={id}`
Real-time packing optimization updates

**Message Types**:
- `packing_result`
- `damage_prediction`
- `heartbeat`

### `WS /ws/notifications?client_id={id}`
System notifications

**Message Types**:
- `notification`
- `weather_alert`
- `traffic_update`
- `error`
- `heartbeat`

---

## 📊 Example Workflow

### Complete Shipment Optimization

```javascript
// 1. Create Shipment
const shipmentResponse = await fetch('http://localhost:8000/api/shipments', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    origin: 'Los Angeles',
    destination: 'New York',
    items: [
      {width: 50, height: 40, depth: 30, weight: 25, fragile: false, stackable: true}
    ],
    priority: 'high'
  })
});
const {shipment_id} = await shipmentResponse.json();

// 2. Optimize Everything
const optimizeResponse = await fetch('http://localhost:8000/api/optimize', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    shipment_id,
    include_ai_analysis: true,
    store_in_graph: true
  })
});
const optimization = await optimizeResponse.json();

console.log(`Utilization: ${optimization.summary.utilization}%`);
console.log(`Risk Level: ${optimization.summary.risk_level}`);
console.log(`Ready: ${optimization.summary.ready_for_dispatch}`);
```

---

## 🛠️ Error Handling

All endpoints return standard HTTP status codes:

- `200`: Success
- `201`: Created
- `400`: Bad Request (validation error)
- `404`: Not Found
- `500`: Internal Server Error

**Error Response Format**:
```json
{
  "detail": "Error message here"
}
```

---

## 🔒 CORS

CORS is enabled for all origins. In production, update `api/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 🚀 Production Deployment

### Using Uvicorn
```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Using Gunicorn
```bash
gunicorn api.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Using Docker
```dockerfile
FROM python:3.12
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## ✅ Testing

Run the API test suite:
```bash
# Start API first
uvicorn api.main:app --reload

# In another terminal
python tests/test_api.py
```

---

## 📈 Performance

- **Average Response Time**: < 100ms (excluding AI/packing operations)
- **3D Packing**: ~3-10ms (DeepPack3D)
- **AI Analysis**: ~1-2s (Claude API)
- **Weather API**: ~200-500ms (OpenWeatherMap)
- **Neo4j Queries**: ~10-50ms

---

## 🎯 Frontend Integration

The API is ready for frontend integration with:
- ✅ RESTful design
- ✅ JSON responses
- ✅ CORS enabled
- ✅ Interactive documentation
- ✅ WebSocket support for real-time
- ✅ Comprehensive error handling

**Recommended Frontend Stack**:
- React/Vue/Angular for UI
- Axios/Fetch for HTTP requests
- WebSocket API for real-time updates
- Charts.js/D3.js for analytics visualization
