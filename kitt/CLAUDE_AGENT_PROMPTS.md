# 🤖 Claude Agent Prompts for KITT Freight Optimization

**Purpose**: Example prompts to use with Claude Desktop (via MCP) or the REST API to autonomously optimize shipments

---

## 🎯 Basic Shipment Optimization Prompts

### Prompt 1: Simple Shipment Creation & Optimization

```
Create a shipment from Los Angeles to New York with 5 boxes
(50x40x30cm, 25kg each) and optimize everything.
```

**What Claude Will Do Autonomously**:
1. ✅ Create the shipment in the database
2. ✅ Generate 3D bin packing with DeepPack3D
3. ✅ Check real weather conditions (OpenWeatherMap)
4. ✅ Check traffic conditions (TomTom)
5. ✅ Predict damage risk with AI
6. ✅ Store in Neo4j knowledge graph
7. ✅ Publish events to Redpanda
8. ✅ Return optimization summary

**Expected Response**:
```
✅ Created shipment SH-ABC123 from Los Angeles to New York
✅ Packed 5 items with 85.2% truck utilization
✅ Weather: Clear, 50°F (good conditions)
✅ Traffic: Low congestion
✅ Risk Level: LOW
✅ Ready for dispatch!
```

---

### Prompt 2: Optimization with Specific Requirements

```
I need to ship 10 fragile electronics boxes from Chicago to Miami.
Each box is 100x80x60cm and weighs 50kg. This is critical priority
with a deadline of 3 days. Optimize the shipment and make sure you
account for weather and road conditions.
```

**What Claude Will Do**:
1. ✅ Create shipment with fragile items marked
2. ✅ Select truck appropriate for fragile cargo
3. ✅ Optimize 3D packing considering fragile constraints
4. ✅ Get real weather for Chicago→Miami route
5. ✅ Calculate damage risk based on fragility + weather
6. ✅ Provide AI recommendations for handling fragile items
7. ✅ Store historical pattern in knowledge graph
8. ✅ Generate comprehensive report

**Expected Response**:
```
✅ Created critical priority shipment SH-XYZ789
✅ Route: Chicago → Miami (1,200 miles)
✅ Weather Analysis:
   - Origin: Partly cloudy, 45°F
   - Destination: Clear, 75°F
   - Weather Severity: 2/5 (low risk)
✅ Packing: 21.5% utilization, fragile items on top layer
✅ Risk Level: MEDIUM (due to fragile items)
⚠️  Recommendations:
   - Use extra padding for electronics
   - Avoid stacking heavy items on fragile boxes
   - Climate-controlled truck recommended
✅ Estimated transit time: 18-20 hours
```

---

## 🔍 Advanced Analysis Prompts

### Prompt 3: Historical Pattern Analysis

```
What can you tell me about shipments from Los Angeles to New York?
Show me historical patterns and recommend the best truck for a
250kg shipment.
```

**What Claude Will Do**:
1. ✅ Query Neo4j for LA→NYC historical shipments
2. ✅ Analyze average utilization rates
3. ✅ Check historical damage incidents
4. ✅ Find optimal trucks based on weight/volume
5. ✅ Provide data-driven recommendations

**Expected Response**:
```
📊 Historical Analysis: Los Angeles → New York

Found 15 previous shipments on this route:
✅ Average utilization: 78.5%
✅ Average transit time: 40 hours
✅ Damage incidents: 1 (6.7% rate)
✅ Most successful truck: TRK-003 (Box Truck, 90% avg utilization)

For your 250kg shipment, I recommend:
🚛 Truck: TRK-003 (Box Truck)
   - Capacity: 5,000kg, 1,000,000 cm³
   - Historical performance: 90% utilization on this route
   - Zero damage incidents

📈 Optimization Tips:
   - This route typically has low traffic on weekdays
   - Weather is optimal in fall/spring
   - Consider grouping with other LA→NYC shipments for better utilization
```

---

### Prompt 4: Real-Time Route Monitoring

```
I have shipment SH-ABC123 ready to go. Check current weather and
traffic conditions and tell me if it's safe to dispatch now or if
we should wait.
```

**What Claude Will Do**:
1. ✅ Get shipment details from database
2. ✅ Check REAL current weather (OpenWeatherMap)
3. ✅ Check REAL traffic conditions (TomTom)
4. ✅ Calculate road quality and weather severity
5. ✅ Predict damage risk with current conditions
6. ✅ Provide go/no-go recommendation

**Expected Response**:
```
🌤️  Route Conditions for SH-ABC123 (LA → NYC)

Current Weather:
✅ Los Angeles: Clear, 52°F, Wind 5mph
✅ New York: Partly cloudy, 45°F, Wind 10mph
✅ Weather Severity: 1/5 (excellent)

Traffic Conditions:
✅ Origin: Low congestion (0 min delay)
✅ Expected incidents: None reported
✅ Road Quality: Excellent (10/10)

Risk Assessment:
✅ Risk Level: LOW
✅ Risk Score: 15/100

🚀 RECOMMENDATION: DISPATCH NOW
   - Optimal weather conditions
   - No traffic issues
   - Low damage risk
   - All systems ready
```

---

## 🧠 AI-Powered Prompts

### Prompt 5: Complex Multi-Shipment Optimization

```
I have 3 shipments to optimize:
1. Los Angeles to New York: 10 boxes (50x40x30cm, 25kg each)
2. Chicago to Miami: 5 fragile boxes (100x80x60cm, 50kg each)
3. Seattle to Boston: 15 small boxes (30x30x30cm, 10kg each)

Analyze all three, find the best trucks, and tell me the optimal
dispatch schedule considering weather and traffic.
```

**What Claude Will Do**:
1. ✅ Create all 3 shipments
2. ✅ Analyze each route independently
3. ✅ Check weather/traffic for all routes
4. ✅ Optimize packing for each
5. ✅ Find optimal trucks from knowledge graph
6. ✅ Calculate damage risk for each
7. ✅ Create dispatch schedule based on conditions
8. ✅ Provide consolidated recommendation

**Expected Response**:
```
📦 Multi-Shipment Optimization Complete

Shipment 1: LA → NYC (SH-001)
✅ Truck: TRK-001 (85% utilization)
✅ Weather: Good (severity 2/5)
✅ Risk: LOW
🕐 Recommended Dispatch: Now

Shipment 2: Chicago → Miami (SH-002)
✅ Truck: TRK-004 (21% utilization)
⚠️  Weather: Thunderstorms expected (severity 4/5)
⚠️  Risk: MEDIUM
⏰ Recommended Dispatch: Wait 6 hours (storm passes)

Shipment 3: Seattle → Boston (SH-003)
✅ Truck: TRK-002 (45% utilization)
✅ Weather: Clear (severity 1/5)
✅ Risk: LOW
🕐 Recommended Dispatch: Now

📊 Summary:
   - Total utilization across 3 trucks: 50.3%
   - 2 shipments ready for immediate dispatch
   - 1 shipment should wait for better weather
   - Estimated total transit time: 48-60 hours
```

---

### Prompt 6: AI Learning & Recommendations

```
Analyze my last 20 shipments and tell me how I can improve
packing efficiency and reduce damage incidents.
```

**What Claude Will Do**:
1. ✅ Query Neo4j for last 20 shipments
2. ✅ Analyze utilization patterns
3. ✅ Identify damage incident correlations
4. ✅ Find inefficient routes
5. ✅ Use AI to generate recommendations
6. ✅ Provide actionable insights

**Expected Response**:
```
📈 Fleet Optimization Analysis (Last 20 Shipments)

Key Metrics:
✅ Average Utilization: 67.5%
⚠️  Damage Incidents: 3 (15% rate)
✅ Average Transit Time: 35 hours
✅ Total Volume Shipped: 450,000 cm³

🔍 Insights:

1. Low Utilization on Short Routes
   - LA → San Francisco: Avg 45% utilization
   - Recommendation: Group shipments on this route
   - Potential savings: 30% reduction in trips

2. Damage Correlation Found
   - All 3 incidents occurred in weather severity 4+
   - Fragile items + bad weather = high risk
   - Recommendation: Delay fragile shipments in severe weather

3. Truck Selection Issues
   - TRK-005 (Flatbed) used for fragile items 2x
   - Wrong truck type for cargo
   - Recommendation: Use box trucks for fragile cargo

4. Peak Traffic Delays
   - 5 shipments delayed 2+ hours due to peak traffic
   - All departed 7-9 AM
   - Recommendation: Schedule departures after 10 AM

🎯 Action Items:
   ✅ Implement route grouping for short-haul shipments
   ✅ Add weather delay logic for fragile items
   ✅ Update truck selection rules in knowledge graph
   ✅ Adjust departure schedules to avoid peak traffic

Estimated Impact:
   📈 Utilization: 67.5% → 85%+ (expected)
   📉 Damage Rate: 15% → 5% (expected)
   💰 Cost Savings: ~$15,000/month
```

---

## 🔧 API Integration Prompts

### Prompt 7: Using the REST API

```
Show me how to use the REST API to create and optimize a shipment
programmatically. Give me curl examples.
```

**What Claude Will Provide**:
```bash
# Step 1: Create a shipment
curl -X POST http://localhost:8000/api/shipments \
  -H "Content-Type: application/json" \
  -d '{
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
        "description": "General Cargo"
      }
    ],
    "priority": "high",
    "deadline": "2025-11-25T00:00:00"
  }'

# Response: {"shipment_id": "SH-ABC123", ...}

# Step 2: Full optimization with all features
curl -X POST http://localhost:8000/api/optimize \
  -H "Content-Type: application/json" \
  -d '{
    "shipment_id": "SH-ABC123",
    "truck_id": null,
    "include_ai_analysis": true,
    "store_in_graph": true
  }'

# Response includes:
# - 3D packing results (DeepPack3D)
# - Real weather conditions
# - Real traffic data
# - AI damage risk prediction
# - AI loading recommendations
# - Knowledge graph storage confirmation

# Step 3: Check route conditions
curl -X GET "http://localhost:8000/api/route-conditions?origin=Los%20Angeles&destination=New%20York"

# Step 4: Get analytics
curl -X GET http://localhost:8000/api/analytics/dashboard
curl -X GET http://localhost:8000/api/analytics/utilization
curl -X GET http://localhost:8000/api/analytics/performance

# Step 5: Query knowledge graph
curl -X POST http://localhost:8000/api/graph/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "MATCH (s:Shipment)-[:FROM]->(origin:Location {name: \"Los Angeles\"}) RETURN s LIMIT 10",
    "parameters": {}
  }'
```

---

## 🚀 Full Autonomous Workflow Prompt

### Prompt 8: Complete Autonomous Optimization

```
I need to ship electronics from Los Angeles to New York.
Create the shipment, optimize everything, and handle it
autonomously from start to finish. Use all available data
and AI to make the best decisions.
```

**What Claude Will Execute (11 Autonomous Steps)**:

```
🤖 Starting Autonomous Freight Optimization...

Step 1/11: Creating shipment...
✅ Created shipment SH-E70E42A5
   Origin: Los Angeles → Destination: New York
   Items: 10 boxes, 250 kg total

Step 2/11: Storing in knowledge graph...
✅ Stored in Neo4j with relationships
   Items in graph: 10
   Total volume: 600,000 cm³

Step 3/11: Checking historical patterns...
✅ Found 5 similar LA→NYC shipments
   Average utilization: 82%
   Best performing truck: TRK-003

Step 4/11: Analyzing route conditions...
✅ Weather at LA: Clear, 50°F (REAL DATA from OpenWeatherMap)
✅ Weather at NYC: Cloudy, 42°F
✅ Weather Severity: 2/5
✅ Traffic: Low congestion
✅ Road Quality: Excellent

Step 5/11: Finding optimal truck...
✅ Selected TRK-003 based on:
   - Historical 90% utilization on this route
   - Sufficient capacity for 250kg
   - Zero damage history

Step 6/11: Optimizing 3D packing...
✅ DeepPack3D algorithm complete
   Utilization: 85.2%
   All 10 items packed
   Computation time: 5ms

Step 7/11: Predicting damage risk...
✅ AI Risk Analysis (Claude API)
   Risk Level: LOW
   Risk Score: 15/100
   Factors: Good weather, low traffic, stable cargo

Step 8/11: Getting AI recommendations...
✅ AI Analysis (Claude API)
   Loading Strategy: Heavy items bottom, distribute weight evenly
   Special Handling: None required
   Truck Criteria: Standard box truck sufficient

Step 9/11: Publishing optimization event...
✅ Event published to Redpanda
   Topic: shipment.optimized
   Status: ready_for_dispatch

Step 10/11: Updating knowledge graph...
✅ Relationships created:
   - Shipment → Truck
   - Shipment → Route
   - Shipment → PackingPlan

Step 11/11: Generating final report...

═══════════════════════════════════════════════════════════════
 ✅ AUTONOMOUS OPTIMIZATION COMPLETE
═══════════════════════════════════════════════════════════════

Shipment Details:
   ID: SH-E70E42A5
   Route: Los Angeles → New York (2,800 miles)
   Items: 10 boxes, 250 kg
   Priority: high

Optimization Results:
   🚛 Truck: TRK-003 (Box Truck)
   📦 Utilization: 85.2% (excellent)
   🎯 Packing Method: DeepPack3D-BL
   ⚡ Computation Time: 5ms

Route Intelligence:
   🌤️  Weather: Good (severity 2/5)
   🚗 Traffic: Low congestion
   🛣️  Road Quality: 10/10
   ⏱️  Estimated Transit: 40 hours

Risk Assessment:
   ✅ Risk Level: LOW
   ✅ Risk Score: 15/100
   ✅ No special handling required

AI Recommendations:
   ✅ Standard packing procedures sufficient
   ✅ No weather delays expected
   ✅ Optimal dispatch window: Next 4 hours

Knowledge Graph:
   ✅ Stored for future learning
   ✅ Similar shipments: 5 found
   ✅ Historical success rate: 95%

Status:
   🚀 READY FOR IMMEDIATE DISPATCH
   ✅ All systems optimal
   ✅ No blocking issues

Next Steps:
   1. Assign driver to TRK-003
   2. Load cargo following AI recommendations
   3. Depart within 4-hour optimal window
   4. Monitor via WebSocket for real-time updates

═══════════════════════════════════════════════════════════════
 Claude executed 11 autonomous steps to optimize this shipment!
═══════════════════════════════════════════════════════════════
```

---

## 📱 Claude Desktop MCP Integration

### How to Use with Claude Desktop

1. **Configure Claude Desktop** (see `MCP_SERVER_SETUP.md`)
2. **Open Claude Desktop**
3. **Use any of the prompts above**
4. **Claude will automatically**:
   - Use the 14 MCP tools
   - Call real APIs (Weather, Neo4j, DeepPack3D)
   - Store data in knowledge graph
   - Learn from historical patterns
   - Make intelligent decisions

### Example Session:

```
You: Create a shipment from LA to NYC with 5 boxes and optimize it.

Claude: I'll help you optimize that shipment! Let me use the KITT
        system to create and optimize it.

        [Uses MCP tool: create_shipment]
        [Uses MCP tool: store_shipment_in_knowledge_graph]
        [Uses MCP tool: get_route_conditions]
        [Uses MCP tool: optimize_packing]
        [Uses MCP tool: predict_damage_risk]

        ✅ Done! I've created shipment SH-ABC123 and optimized it:
        - 85% truck utilization
        - Weather looks good (50°F, clear)
        - Low damage risk
        - Ready to dispatch!

        Would you like me to analyze historical patterns for this
        route or get more details about the packing layout?

You: Yes, show me historical patterns.

Claude: [Uses MCP tool: find_historical_shipment_patterns]

        I found 8 previous LA→NYC shipments. Here's what I learned:
        - Average utilization: 78%
        - Your 85% is above average! 📈
        - Best times to ship: Tuesday-Thursday
        - This route has a 96% on-time delivery rate
```

---

## 🎓 Pro Tips for Effective Prompts

### Best Practices:

1. **Be Specific About Requirements**
   - ✅ Good: "5 fragile boxes, 100x80x60cm, 50kg each, priority: critical"
   - ❌ Bad: "Some boxes that need to go somewhere"

2. **Request Analysis When Needed**
   - "...and analyze weather conditions"
   - "...check historical patterns"
   - "...predict damage risk"

3. **Ask for Comprehensive Reports**
   - "Give me a full optimization report"
   - "Include all available data"
   - "Show me AI recommendations"

4. **Let Claude Make Decisions**
   - "Optimize everything autonomously"
   - "Use all available intelligence"
   - "Make the best decisions based on data"

5. **Request Learning & Improvement**
   - "What can I learn from past shipments?"
   - "How can I improve efficiency?"
   - "Are there any patterns I should know about?"

---

## 📊 Expected Response Times

| Operation | Time | Notes |
|-----------|------|-------|
| Create shipment | < 100ms | Database write |
| 3D packing | ~5ms | DeepPack3D TensorFlow |
| Weather API | ~300ms | Real OpenWeatherMap call |
| Traffic API | ~500ms | Real TomTom call (or fallback) |
| AI Analysis | ~10s | Real Claude API call |
| Graph query | ~50ms | Neo4j query |
| Full optimization | ~15s | All steps combined |

---

## ✅ Verification

After optimization, Claude can verify results:

```
You: Did the optimization work correctly?

Claude: Let me verify the optimization for SH-ABC123:

        [Uses MCP tool: get_shipment_data]

        ✅ Shipment verified:
        - Status: packed
        - Packing plan: PLAN-XYZ789
        - Utilization: 85.2%
        - Risk assessment: LOW
        - Knowledge graph: Stored

        Everything looks perfect! The shipment is ready for dispatch.
```

---

## 🚀 Start Using

To start using these prompts:

1. **With Claude Desktop**: Just paste any prompt above
2. **With REST API**: Use the curl examples in Prompt 7
3. **With MCP Server**: Configure and use via Claude Desktop

All prompts work with **100% real APIs** and **autonomous decision-making**! 🎯
