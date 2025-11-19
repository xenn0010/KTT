# KITT Agentic Features with Neo4j Knowledge Graph

## 🧠 Overview

KITT now has **full agentic capabilities** powered by:
- **Neo4j Graph Database** - Knowledge graph for freight relationships
- **15 MCP Tools** - Claude can use these tools autonomously
- **Cypher Query Power** - Claude can write custom graph queries
- **Multi-Agent Coordination** - Tasks can span multiple agents

---

## 🎯 What Makes This Agentic?

### Traditional AI vs Agentic AI

**Traditional AI (Q&A)**:
```
User: "What's the best truck for this shipment?"
AI: "Based on the data, Truck-123 is best."
```

**Agentic AI (Autonomous)**:
```
User: "Optimize shipment S-001"
Claude:
  1. get_shipment_knowledge_graph(S-001) → understand context
  2. find_optimal_trucks_from_graph(weight, volume, origin) → find trucks
  3. optimize_packing(S-001, truck_id) → pack efficiently
  4. predict_damage_risk(S-001) → assess risks
  5. store_shipment_in_knowledge_graph(...) → remember for learning
  6. publish_event("packing_complete") → notify systems

Result: "Shipment optimized! 85% utilization, low risk, dispatched."
```

**Key Difference**: Claude **acts** autonomously, using multiple tools in sequence to accomplish goals.

---

## 🔧 Available MCP Tools

### Core Freight Tools (7)

1. **get_shipment_data** - Get complete shipment information
2. **create_shipment** - Create new shipment with items
3. **optimize_packing** - Run 3D bin packing (DeepPack3D)
4. **get_route_conditions** - Weather, traffic, road conditions
5. **predict_damage_risk** - AI risk assessment
6. **publish_event** - Send events to Redpanda stream
7. **analyze_shipment_with_ai** - AI-powered recommendations

### Neo4j Graph Tools (8)

8. **store_shipment_in_knowledge_graph** - Store shipment + relationships
9. **get_shipment_knowledge_graph** - Get complete graph view
10. **find_optimal_trucks_from_graph** - Graph-based truck selection
11. **get_location_analytics_from_graph** - Location insights
12. **find_historical_shipment_patterns** - Learn from history
13. **get_freight_network_overview** - Network statistics
14. **query_knowledge_graph_with_cypher** - **MOST POWERFUL** - Custom queries
15. (Implicitly: store_route, store_truck, assign_truck)

---

## 🕸️ Neo4j Knowledge Graph Structure

### Graph Schema

```
┌─────────────┐
│  Shipment   │
│  ─────────  │
│  id         │
│  status     │
│  priority   │
│  weight     │
└──────┬──────┘
       │
       │ [:FROM]
       ▼
┌─────────────┐       ┌─────────────┐
│  Location   │       │    Item     │
│  ─────────  │       │  ─────────  │
│  name       │       │  id         │
│  ...        │       │  dimensions │
└─────────────┘       │  weight     │
       ▲              └─────────────┘
       │                      ▲
       │ [:TO]                │
       │                      │ [:CONTAINS]
┌──────┴──────┐              │
│  Shipment   ├──────────────┘
└──────┬──────┘
       │
       │ [:USES_ROUTE]
       ▼
┌─────────────┐
│    Route    │
│  ─────────  │
│  distance   │
│  duration   │
└─────────────┘
       ▲
       │ [:ASSIGNED_TO]
       │
┌──────┴──────┐
│    Truck    │
│  ─────────  │
│  capacity   │
│  status     │
└─────────────┘
```

### Example Relationships

```cypher
// Create shipment graph
(Shipment {id: "S-001"})-[:FROM]->(Location {name: "Los Angeles"})
(Shipment {id: "S-001"})-[:TO]->(Location {name: "New York"})
(Shipment {id: "S-001"})-[:CONTAINS]->(Item {id: "I-001"})
(Truck {id: "T-123"})-[:ASSIGNED_TO {utilization: 85.5}]->(Shipment {id: "S-001"})
```

---

## 🎬 Agentic Workflow Examples

### Example 1: Intelligent Shipment Optimization

**User Request**: "Optimize shipment S-001 from LA to NYC"

**Claude's Autonomous Workflow**:

```typescript
// Step 1: Understand the shipment
const shipment = await get_shipment_data("S-001")

// Step 2: Check if we have historical data for this route
const patterns = await find_historical_shipment_patterns("Los Angeles", "New York")

// Step 3: Find optimal truck using graph intelligence
const trucks = await find_optimal_trucks_from_graph(
  shipment.total_weight,
  shipment.total_volume,
  "Los Angeles"
)

// Step 4: Pack the shipment
const packing = await optimize_packing("S-001", trucks[0].truck_id)

// Step 5: Check route conditions
const conditions = await get_route_conditions(null, "Los Angeles", "New York")

// Step 6: Predict damage risk
const risk = await predict_damage_risk("S-001")

// Step 7: Store everything in knowledge graph for future learning
await store_shipment_in_knowledge_graph(
  "S-001",
  "Los Angeles",
  "New York",
  shipment.items,
  "in_transit",
  "high"
)

// Step 8: Publish event for other systems
await publish_event("shipment_optimized", {
  shipment_id: "S-001",
  utilization: packing.utilization,
  risk_level: risk.level,
  truck_id: trucks[0].truck_id
})

// Claude responds with comprehensive analysis
"Shipment S-001 optimized successfully! Using Truck T-123 with 85.2% utilization.
Route conditions are favorable (clear weather, light traffic).
Damage risk is LOW based on historical patterns.
Similar shipments averaged 48 hours delivery time.
All data stored in knowledge graph for continuous learning."
```

### Example 2: Network Analysis & Optimization

**User Request**: "Which routes are underperforming?"

**Claude's Workflow**:

```typescript
// Step 1: Get network overview
const network = await get_freight_network_overview()

// Step 2: Write custom Cypher query to find underperforming routes
const underperforming = await query_knowledge_graph_with_cypher(`
  MATCH (s:Shipment)-[:USES_ROUTE]->(r:Route)
  OPTIONAL MATCH (t:Truck)-[:ASSIGNED_TO]->(s)
  WITH r, avg(s.utilization) as avg_util, count(s) as shipments
  WHERE shipments > 5 AND avg_util < 60
  RETURN r.id as route,
         r.origin as origin,
         r.destination as destination,
         avg_util,
         shipments
  ORDER BY avg_util ASC
  LIMIT 10
`)

// Step 3: For each underperforming route, analyze why
for (const route of underperforming) {
  // Get historical patterns
  const patterns = await find_historical_shipment_patterns(
    route.origin,
    route.destination
  )

  // Get location analytics
  const originAnalytics = await get_location_analytics_from_graph(route.origin)
  const destAnalytics = await get_location_analytics_from_graph(route.destination)

  // Analyze and make recommendations
}

// Claude provides detailed report with actionable insights
```

### Example 3: Predictive Truck Assignment

**User Request**: "Assign best truck for new shipment from Boston to Miami"

**Claude's Workflow**:

```typescript
// Step 1: Learn from history
const historicalPatterns = await find_historical_shipment_patterns(
  "Boston",
  "Miami"
)

// Step 2: Find what truck types worked best historically
const bestTrucks = await query_knowledge_graph_with_cypher(`
  MATCH (s:Shipment)-[:FROM]->(o:Location {name: 'Boston'})
  MATCH (s)-[:TO]->(d:Location {name: 'Miami'})
  MATCH (t:Truck)-[a:ASSIGNED_TO]->(s)
  WHERE s.status = 'delivered'
  WITH t.type as truck_type, avg(a.utilization) as avg_util, count(*) as uses
  WHERE uses > 3
  RETURN truck_type, avg_util, uses
  ORDER BY avg_util DESC
`)

// Step 3: Find currently available trucks of the best type
const availableTrucks = await find_optimal_trucks_from_graph(
  shipment_weight,
  shipment_volume,
  "Boston"
)

// Step 4: Select and assign
const selectedTruck = availableTrucks.find(t => t.truck_type === bestTrucks[0].truck_type)

// Step 5: Run packing optimization
const packing = await optimize_packing(shipment_id, selectedTruck.truck_id)

// Claude explains the reasoning
"Selected Truck T-456 (box_truck) based on historical data.
This truck type achieved 87% average utilization on Boston-Miami route.
Current packing: 89% utilization - exceeding historical average.
Predicted delivery time: 26-28 hours (based on 8 similar shipments)."
```

---

## 🧪 Custom Cypher Queries

### Most Powerful Agentic Feature

Claude can write **custom Cypher queries** to answer complex questions:

### Query 1: Find Busiest Freight Corridors

```cypher
MATCH (s:Shipment)-[:FROM]->(origin:Location)
MATCH (s)-[:TO]->(dest:Location)
WITH origin.name as from_city, dest.name as to_city, count(s) as volume
WHERE volume > 10
RETURN from_city, to_city, volume
ORDER BY volume DESC
LIMIT 10
```

**Use Case**: "Show me the top 10 busiest shipping routes"

### Query 2: Identify High-Performance Trucks

```cypher
MATCH (t:Truck)-[a:ASSIGNED_TO]->(s:Shipment)
WITH t, avg(a.utilization) as avg_util, count(s) as shipments
WHERE shipments > 5 AND avg_util > 80
RETURN t.id as truck_id,
       t.type as truck_type,
       avg_util,
       shipments
ORDER BY avg_util DESC
```

**Use Case**: "Which trucks consistently achieve >80% utilization?"

### Query 3: Discover Seasonal Patterns

```cypher
MATCH (s:Shipment)-[:FROM]->(origin:Location {name: 'Los Angeles'})
WITH s, s.created_at.month as month
WITH month, count(s) as shipments, avg(s.total_weight) as avg_weight
RETURN month, shipments, avg_weight
ORDER BY month
```

**Use Case**: "Are there seasonal patterns in LA shipments?"

### Query 4: Find Underutilized Trucks

```cypher
MATCH (t:Truck)
WHERE t.status = 'available'
OPTIONAL MATCH (t)-[a:ASSIGNED_TO]->(s:Shipment)
WITH t, count(s) as assignments_last_month
WHERE assignments_last_month < 5
RETURN t.id, t.type, t.capacity_volume, assignments_last_month
ORDER BY t.capacity_volume DESC
```

**Use Case**: "Which trucks are sitting idle?"

### Query 5: Predict Optimal Route

```cypher
MATCH path = shortestPath(
  (start:Location {name: 'Chicago'})-[:STARTS_AT|ENDS_AT*1..5]-(end:Location {name: 'Seattle'})
)
RETURN path, length(path) as hops
```

**Use Case**: "What's the optimal route from Chicago to Seattle?"

---

## 🤖 How to Use Agentic Features

### In Claude Desktop/API

1. **Connect to MCP Server**:
   ```json
   {
     "mcpServers": {
       "kitt": {
         "command": "python",
         "args": ["-m", "uvicorn", "mcp.server:mcp.app", "--port", "8001"],
         "cwd": "/home/yab/KTT/kitt"
       }
     }
   }
   ```

2. **Claude will see 15 tools available**

3. **Ask agentic questions**:
   - "Optimize this shipment and tell me the best approach"
   - "Analyze our freight network and find inefficiencies"
   - "What patterns exist in our LA to NYC shipments?"
   - "Find me the most reliable trucks for heavy loads"

### In FastAPI Application

```python
from mcp.graph_tools import graph_tools

# Store shipment in graph
await graph_tools.store_shipment_in_graph(
    shipment_id="S-123",
    origin="Boston",
    destination="Atlanta",
    items=[...],
    priority="high"
)

# Query the graph
results = await graph_tools.query_graph_with_cypher("""
    MATCH (s:Shipment {id: 'S-123'})-[:FROM]->(origin)
    MATCH (s)-[:TO]->(dest)
    RETURN origin.name, dest.name
""")
```

---

## 📊 Agentic Benefits

### 1. **Autonomous Decision Making**
- Claude can chain multiple tools
- No need to manually orchestrate
- Intelligent fallbacks and error handling

### 2. **Learning from History**
- Every shipment stored in graph
- Patterns emerge over time
- Recommendations improve continuously

### 3. **Complex Query Capability**
- Answer questions spanning multiple entities
- Graph traversal for relationship discovery
- Custom analytics on demand

### 4. **Predictive Intelligence**
- Historical patterns inform predictions
- Risk assessment based on similar shipments
- Realistic timeline estimates

### 5. **Network Optimization**
- Identify bottlenecks automatically
- Discover underutilized resources
- Optimize fleet allocation

---

## 🚀 Quick Start

### 1. Install Neo4j Driver

```bash
cd /home/yab/KTT/kitt
source venv/bin/activate
pip install neo4j==5.14.1
```

### 2. Start MCP Server

```bash
python mcp/server.py
```

Expected output:
```
🚀 Starting KITT MCP Server
✅ SQL Database initialized
✅ Neo4j Graph Database connected
✅ Registered 15 MCP tools (7 core + 8 graph)
```

### 3. Test Graph Connection

```python
from services.neo4j_service import get_neo4j_service

# Connect
neo4j = await get_neo4j_service()

# Test query
stats = await neo4j.get_network_stats()
print(stats)
```

### 4. Use with Claude

Claude will automatically see all 15 tools and can use them agentic ally.

---

## 🎯 Example Agentic Conversations

### Example 1: Full Optimization

**User**: "I have a shipment from Denver to Phoenix with 10 pallets. Optimize everything."

**Claude** (autonomously):
1. Creates shipment
2. Stores in graph with all relationships
3. Finds historical Denver→Phoenix patterns
4. Selects optimal truck based on history
5. Runs 3D packing
6. Checks route conditions
7. Predicts damage risk
8. Publishes events
9. Returns comprehensive optimization report

### Example 2: Network Analysis

**User**: "What are our biggest inefficiencies?"

**Claude** (autonomously):
1. Gets network overview
2. Queries for underutilized trucks
3. Finds low-utilization routes
4. Analyzes location bottlenecks
5. Discovers seasonal patterns
6. Provides ranked list of inefficiencies with solutions

### Example 3: Predictive Assignment

**User**: "Best truck for 5000kg shipment, LA to Seattle?"

**Claude** (autonomously):
1. Finds historical LA→Seattle shipments
2. Analyzes which truck types performed best
3. Checks current truck availability
4. Considers route conditions
5. Predicts utilization and risks
6. Recommends truck with reasoning

---

## ✅ Summary

**You now have a fully agentic KITT system with**:

✅ **15 MCP Tools** for autonomous operations
✅ **Neo4j Knowledge Graph** for relationship intelligence
✅ **Cypher Query Power** for custom analytics
✅ **Historical Learning** from every shipment
✅ **Multi-Tool Workflows** for complex tasks
✅ **Predictive Capabilities** based on patterns
✅ **Network Optimization** insights

**Claude can now**:
- Plan and execute multi-step workflows
- Learn from historical data
- Write custom graph queries
- Make intelligent predictions
- Optimize the entire freight network
- Provide data-driven recommendations

**All autonomously, without manual orchestration!** 🎉
