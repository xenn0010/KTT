# KITT MCP Server - Phase 2 Complete ✅

## Overview

The Model Context Protocol (MCP) server provides AI-powered tools for freight optimization, integrating SQLite database, Redpanda event streaming, and Claude Haiku 4.5 for intelligent analysis.

## Features Implemented

### ✅ Database Layer (SQLite + async)

**Tables:**
- `shipments` - Freight shipments with status tracking
- `items` - Individual items in shipments
- `packing_plans` - 3D packing optimization results
- `route_analytics` - Route condition history
- `trucks` - Fleet management
- `damage_incidents` - Historical damage records
- `ai_predictions` - AI analysis results

**Operations:**
- Full CRUD for all entities
- Async operations with aiosqlite
- Transaction support
- Comprehensive indexes for performance

### ✅ Redpanda Event Streaming

**Topics:**
- `shipment.requests` - New shipment events
- `packing.results` - Packing optimization results
- `route.updates` - Route condition changes
- `weather.alerts` - Weather warnings
- `traffic.updates` - Traffic condition updates
- `damage.predictions` - Risk predictions
- `notifications` - System notifications

**Features:**
- Producer with delivery guarantees
- Consumer groups for scaling
- Async consumer support
- Automatic serialization

### ✅ Claude Haiku 4.5 Integration

**AI Capabilities:**
- Shipment analysis and recommendations
- Delay prediction based on conditions
- Damage risk assessment
- Route optimization suggestions

**Model:** `claude-3-5-haiku-20250219`
- Fast inference (<500ms typical)
- Cost-effective for high-volume queries
- Structured JSON output

### ✅ MCP Tools (7 total)

1. **`get_shipment_data`** - Retrieve complete shipment information
2. **`create_shipment`** - Create shipment with items
3. **`optimize_packing`** - Run 3D packing optimization
4. **`get_route_conditions`** - Get weather/traffic/road data
5. **`predict_damage_risk`** - AI-powered risk analysis
6. **`publish_event`** - Send events to Redpanda
7. **`analyze_shipment_with_ai`** - Get AI recommendations

---

## Installation

```bash
# Install MCP dependencies
pip install fastmcp aiosqlite kafka-python anthropic

# Or install all dependencies
pip install -r requirements.txt

# Initialize database
python3 scripts/init_db.py
```

---

## Configuration

Add to `.env`:

```bash
# Database
DATABASE_URL=sqlite:///./kitt.db

# Redpanda (Kafka-compatible)
REDPANDA_BOOTSTRAP_SERVERS=localhost:9092

# Anthropic Claude
ANTHROPIC_API_KEY=sk-ant-xxxxx
ANTHROPIC_MODEL=claude-3-5-haiku-20250219
```

---

## Running the MCP Server

### Standalone MCP Server

```bash
# Run MCP server on port 8001
python3 mcp/server.py
```

### With FastAPI (Integrated)

The MCP server can be imported and used within the main FastAPI application.

---

## Usage Examples

### 1. Create Shipment

```python
from mcp.tools import tools

result = await tools.create_shipment(
    origin="Chicago",
    destination="Dallas",
    items=[
        {
            "width": 50,
            "height": 40,
            "depth": 30,
            "weight": 25,
            "fragile": False,
            "stackable": True,
            "description": "Electronics"
        }
    ],
    priority="high"
)

print(f"Created shipment: {result['shipment_id']}")
```

### 2. Optimize Packing

```python
result = await tools.optimize_packing(
    shipment_id="SH-ABC123"
)

print(f"Utilization: {result['utilization']}%")
print(f"Truck: {result['truck_id']}")
```

### 3. Get Route Conditions

```python
conditions = await tools.get_route_conditions(
    route_id="ROUTE-CHI-DAL",
    origin="Chicago",
    destination="Dallas"
)

print(f"Weather: {conditions['current_weather']['condition']}")
print(f"Traffic: {conditions['current_traffic']['level']}")
```

### 4. Predict Damage Risk (AI)

```python
prediction = await tools.predict_damage_risk(
    shipment_id="SH-ABC123",
    route_id="ROUTE-CHI-DAL"
)

print(f"Risk Level: {prediction['risk_level']}")
print(f"Risk Score: {prediction['risk_score']}/100")
print(f"Factors: {prediction['contributing_factors']}")
```

### 5. AI Shipment Analysis

```python
analysis = await tools.analyze_shipment_with_ai(
    shipment_id="SH-ABC123"
)

print(f"Strategy: {analysis['strategy']}")
print(f"Special Handling: {analysis['special_handling']}")
print(f"Risks: {analysis['risks']}")
```

### 6. Publish Event

```python
result = await tools.publish_event(
    event_type="notification",
    event_data={
        "message": "Shipment ready for loading",
        "shipment_id": "SH-ABC123",
        "severity": "info"
    }
)

print(f"Published to topic: {result['topic']}")
```

---

## Testing

```bash
# Initialize database
python3 scripts/init_db.py

# Run MCP tests
python3 tests/test_mcp_tools.py
```

**Test Coverage:**
- ✅ Database CRUD operations
- ✅ Shipment creation and retrieval
- ✅ Packing optimization
- ✅ Route conditions
- ⚠️ Damage prediction (requires API key)
- ⚠️ AI analysis (requires API key)
- ⚠️ Event publishing (requires Redpanda)

---

## Files Created

```
mcp/
├── __init__.py
├── server.py              # FastMCP server with tool registration
├── tools.py               # MCP tool implementations
├── database.py            # SQLite async operations
├── redpanda_client.py     # Event streaming client
└── claude_client.py       # Claude Haiku AI client

scripts/
└── init_db.py             # Database initialization script

tests/
└── test_mcp_tools.py      # MCP tools test suite

schema.sql                 # Database schema definition
```

---

## Next Steps (Phase 3)

- [ ] Integrate actual DeepPack3D engine
- [ ] Connect real Weather APIs (OpenWeatherMap)
- [ ] Connect Traffic APIs (TomTom)
- [ ] Connect Route APIs (OpenRouteService)
- [ ] Train ML damage prediction model
- [ ] Add caching layer (Redis)

---

**Status:** ✅ Phase 2 Complete - MCP Server Operational
**Next:** Phase 3 - External API Integration & DeepPack3D
