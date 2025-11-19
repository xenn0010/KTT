# 🤖 Agent Prompt API - Natural Language Control

**Let users command Claude with natural language prompts from your frontend**

---

## 🎯 Endpoints

### 1. `POST /api/agent/prompt` - Execute Agent Commands

Send natural language prompts and Claude autonomously executes them.

### 2. `POST /api/agent/chat` - Chat with Agent

Conversational interface for questions and analysis.

---

## 📝 Request Format

```json
{
  "prompt": "Create a shipment from LA to NYC with 5 boxes and optimize it",
  "context": {
    "user_id": "user123",
    "session_id": "sess456"
  },
  "max_tokens": 4096
}
```

### Parameters

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `prompt` | string | Yes | Natural language command/question |
| `context` | object | No | Additional context for the agent |
| `max_tokens` | integer | No | Max response length (default: 4096) |

---

## 🚀 Example Requests

### Example 1: Create and Optimize Shipment

```bash
curl -X POST http://localhost:8000/api/agent/prompt \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create a shipment from Los Angeles to New York with 5 boxes (50x40x30cm, 25kg each, priority high) and optimize everything including weather and AI analysis"
  }'
```

**Response**:
```json
{
  "success": true,
  "prompt": "Create a shipment from Los Angeles to New York...",
  "response": "## Action Taken\nCreated shipment SH-ABC123 from Los Angeles to New York with 5 standard cargo boxes.\n\n## Results\n- **Shipment ID**: SH-ABC123\n- **Packing Utilization**: 85.2%\n- **Weather Conditions**: Clear, 50°F at origin, 42°F at destination\n- **Weather Severity**: 2/5 (Good)\n- **Traffic**: Low congestion\n- **Damage Risk**: LOW (15/100)\n\n## Recommendations\n- Standard packing procedures are sufficient\n- Optimal dispatch window: Next 4 hours\n- No weather delays expected\n- Heavy items should be placed at bottom, distribute weight evenly\n\n## Next Steps\n1. Assign driver to truck TRK-001\n2. Load cargo following AI recommendations\n3. Depart within optimal window for best conditions\n4. Monitor via WebSocket for real-time updates",
  "actions_taken": ["Agent processed prompt and executed necessary operations"],
  "data": {...}
}
```

---

### Example 2: Check Route Conditions

```bash
curl -X POST http://localhost:8000/api/agent/prompt \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "What are the current weather and traffic conditions for a route from Chicago to Miami?"
  }'
```

**Response**:
```json
{
  "success": true,
  "prompt": "What are the current weather...",
  "response": "## Action Taken\nChecked real-time weather and traffic conditions for Chicago → Miami route.\n\n## Results\n**Weather at Origin (Chicago)**:\n- Condition: Cloudy\n- Temperature: 45°F\n- Wind: 10 mph\n\n**Weather at Destination (Miami)**:\n- Condition: Clear\n- Temperature: 75°F\n- Humidity: 65%\n\n**Weather Severity**: 2/5 (Good conditions)\n\n**Traffic Conditions**:\n- Congestion Level: Low\n- Expected Delays: 0 minutes\n- Road Quality: Excellent (10/10)\n\n## Recommendations\n- Excellent conditions for dispatch\n- No weather-related delays expected\n- Low traffic means optimal transit time\n\n## Next Steps\nGreen light for immediate dispatch if shipment is ready.",
  "actions_taken": ["Agent processed prompt and executed necessary operations"]
}
```

---

### Example 3: Analyze Historical Data

```bash
curl -X POST http://localhost:8000/api/agent/prompt \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Show me utilization statistics for my last 20 shipments and tell me how I can improve"
  }'
```

**Response**:
```json
{
  "success": true,
  "prompt": "Show me utilization statistics...",
  "response": "## Action Taken\nAnalyzed last 20 shipments from database and knowledge graph.\n\n## Results\n**Overall Statistics**:\n- Average Utilization: 67.5%\n- Min Utilization: 34%\n- Max Utilization: 92%\n- Total Volume Shipped: 450,000 cm³\n\n**Routes Breakdown**:\n1. LA → NYC: 5 shipments, 82% avg utilization ✅\n2. Chicago → Miami: 8 shipments, 71% avg utilization ⚠️\n3. Seattle → Boston: 7 shipments, 52% avg utilization ❌\n\n**Problem Areas Identified**:\n- Seattle → Boston route has consistently low utilization\n- 5 shipments departed during peak traffic (7-9 AM)\n- 3 damage incidents, all in weather severity 4+\n\n## Recommendations\n1. **Route Optimization**: Consider grouping Seattle → Boston shipments to improve utilization from 52% to 75%+\n2. **Timing**: Adjust departure schedules to avoid 7-9 AM peak traffic\n3. **Weather Delays**: Implement weather delay logic for fragile items when severity > 3\n4. **Truck Selection**: Use appropriate truck types (found 2 cases of flatbed used for fragile cargo)\n\n**Potential Impact**:\n- Utilization improvement: 67.5% → 85%+ (expected)\n- Cost savings: ~$12,000/month\n- Damage reduction: 15% → 5% rate\n\n## Next Steps\n1. Review Seattle → Boston shipment grouping opportunities\n2. Update departure schedule policies\n3. Add weather-based dispatch rules for fragile items",
  "actions_taken": ["Agent processed prompt and executed necessary operations"]
}
```

---

### Example 4: Damage Risk Assessment

```bash
curl -X POST http://localhost:8000/api/agent/prompt \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Check if shipment SH-ABC123 is safe to dispatch right now"
  }'
```

**Response**:
```json
{
  "success": true,
  "prompt": "Check if shipment SH-ABC123 is safe...",
  "response": "## Action Taken\nAssessed shipment SH-ABC123 for current dispatch safety.\n\n## Results\n**Shipment Details**:\n- Route: Los Angeles → New York\n- Items: 5 boxes, 125 kg total\n- Priority: High\n\n**Current Conditions**:\n- Weather Severity: 2/5 (Good)\n- Traffic Level: Low\n- Road Quality: 10/10 (Excellent)\n\n**Risk Assessment**:\n- Risk Level: **LOW** ✅\n- Risk Score: 15/100\n- Packing Utilization: 85.2%\n\n**Risk Factors**:\n- No severe weather conditions\n- Low traffic congestion\n- Standard cargo handling\n\n## Recommendations\n✅ **SAFE TO DISPATCH NOW**\n\nOptimal conditions for dispatch:\n- Weather is clear at both origin and destination\n- No traffic delays expected\n- Low damage risk\n- All packing optimization complete\n\n## Next Steps\n1. Assign driver immediately\n2. Depart within next 4 hours for optimal conditions\n3. Monitor real-time via WebSocket",
  "actions_taken": ["Agent processed prompt and executed necessary operations"]
}
```

---

### Example 5: Chat Interface

```bash
curl -X POST http://localhost:8000/api/agent/chat \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "How many shipments do I have pending?"
  }'
```

**Response**:
```json
{
  "success": true,
  "prompt": "How many shipments do I have pending?",
  "response": "You currently have **8 pending shipments** waiting for optimization.\n\nHere's the breakdown by priority:\n- Critical: 2 shipments\n- High: 4 shipments\n- Medium: 2 shipments\n\nWould you like me to optimize all of them now, or would you prefer to focus on the critical priority shipments first?",
  "actions_taken": null
}
```

---

## 💬 Natural Language Examples

### Users can write prompts like:

**Shipment Management**:
- "Create a shipment from LA to NYC with 10 boxes and optimize it"
- "Show me details for shipment SH-ABC123"
- "Delete shipment SH-XYZ789"
- "List all critical priority shipments"

**Optimization**:
- "Optimize packing for shipment SH-ABC123"
- "Run full optimization with AI analysis for SH-ABC123"
- "Check if I should dispatch SH-ABC123 now or wait"

**Analysis & Insights**:
- "What's my average truck utilization this month?"
- "Show me damage risk for the Chicago to Miami route"
- "Which routes have the best on-time delivery rates?"
- "Analyze my last 20 shipments and suggest improvements"

**Weather & Traffic**:
- "What's the weather like from Seattle to Boston right now?"
- "Is there any traffic on the LA to San Francisco route?"
- "Should I delay dispatch due to weather?"

**Historical Patterns**:
- "Show me historical patterns for NYC to Boston"
- "What trucks performed best on the Chicago to Miami route?"
- "Which routes have the highest damage rates?"

---

## 🔧 Frontend Integration

### React Example

```javascript
import { useState } from 'react';

function AgentChat() {
  const [prompt, setPrompt] = useState('');
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);

  const sendPrompt = async () => {
    setLoading(true);
    try {
      const res = await fetch('http://localhost:8000/api/agent/prompt', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt })
      });
      const data = await res.json();
      setResponse(data.response);
    } catch (error) {
      console.error('Agent error:', error);
    }
    setLoading(false);
  };

  return (
    <div className="agent-chat">
      <h2>🤖 Ask KITT Agent</h2>

      <textarea
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        placeholder="What would you like me to do? (e.g., Create a shipment from LA to NYC...)"
        rows={4}
        style={{ width: '100%', padding: '10px' }}
      />

      <button onClick={sendPrompt} disabled={loading}>
        {loading ? '🔄 Processing...' : '✨ Execute'}
      </button>

      {response && (
        <div className="agent-response" style={{ marginTop: '20px', whiteSpace: 'pre-wrap' }}>
          {response}
        </div>
      )}
    </div>
  );
}

export default AgentChat;
```

### Vue Example

```vue
<template>
  <div class="agent-chat">
    <h2>🤖 Ask KITT Agent</h2>

    <textarea
      v-model="prompt"
      placeholder="What would you like me to do?"
      rows="4"
    ></textarea>

    <button @click="sendPrompt" :disabled="loading">
      {{ loading ? '🔄 Processing...' : '✨ Execute' }}
    </button>

    <div v-if="response" class="agent-response">
      {{ response }}
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const prompt = ref('');
const response = ref(null);
const loading = ref(false);

const sendPrompt = async () => {
  loading.value = true;
  try {
    const res = await fetch('http://localhost:8000/api/agent/prompt', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt: prompt.value })
    });
    const data = await res.json();
    response.value = data.response;
  } catch (error) {
    console.error('Agent error:', error);
  }
  loading.value = false;
};
</script>
```

---

## 🎨 UI Component Examples

### Simple Chat Input

```html
<div class="agent-prompt-box">
  <input
    type="text"
    placeholder="Ask Claude to optimize your shipments..."
    id="agent-prompt"
  />
  <button onclick="executePrompt()">Ask Agent</button>
</div>
```

### With Suggestions

```html
<div class="agent-interface">
  <h3>Quick Commands</h3>
  <div class="suggestions">
    <button onclick="fillPrompt('Create a shipment from LA to NYC')">
      📦 Create Shipment
    </button>
    <button onclick="fillPrompt('What is my average utilization?')">
      📊 Check Stats
    </button>
    <button onclick="fillPrompt('Show weather for Chicago to Miami')">
      🌤️ Weather Check
    </button>
  </div>

  <textarea id="agent-prompt"></textarea>
  <button onclick="executePrompt()">✨ Execute</button>

  <div id="agent-response"></div>
</div>
```

---

## ⚡ Response Time

| Operation | Avg Time | Notes |
|-----------|----------|-------|
| Simple query | ~2s | Database lookups |
| Shipment creation | ~3s | Create + initial analysis |
| Full optimization | ~15s | Includes AI calls |
| Weather check | ~1s | Real API call |
| Historical analysis | ~5s | Graph queries + AI |

---

## 🔒 Best Practices

### 1. Input Validation
```javascript
const validatePrompt = (prompt) => {
  if (!prompt || prompt.trim().length < 3) {
    return 'Prompt too short';
  }
  if (prompt.length > 1000) {
    return 'Prompt too long (max 1000 chars)';
  }
  return null;
};
```

### 2. Error Handling
```javascript
try {
  const response = await fetch('/api/agent/prompt', {
    method: 'POST',
    body: JSON.stringify({ prompt })
  });

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }

  const data = await response.json();

  if (!data.success) {
    showError('Agent could not process your request');
  }

} catch (error) {
  showError('Network error. Please try again.');
}
```

### 3. Loading States
```javascript
// Show loading indicator
setLoading(true);
setResponse(null);

// Execute prompt
await sendToAgent(prompt);

// Hide loading
setLoading(false);
```

---

## 🎯 Example Prompts for Users

### Getting Started
```
"Create a shipment from Los Angeles to New York with 5 boxes"
"Show me the weather for my Chicago to Miami route"
"What's my average utilization rate?"
```

### Intermediate
```
"Optimize shipment SH-ABC123 with full AI analysis"
"Check if I should dispatch SH-XYZ now or wait for better weather"
"Show me historical patterns for the LA to NYC route"
```

### Advanced
```
"Analyze my last 20 shipments, identify inefficiencies, and suggest specific improvements with cost impact"
"Create a shipment from Chicago to Miami with 10 fragile electronics boxes, optimize with AI, check damage risk, and tell me the best time to dispatch"
"Compare utilization rates across all routes and recommend which routes to consolidate for better efficiency"
```

---

## ✅ Summary

**New Endpoints**:
- `POST /api/agent/prompt` - Execute commands
- `POST /api/agent/chat` - Conversational interface

**What Users Can Do**:
- ✅ Write natural language prompts in the frontend
- ✅ Claude autonomously executes operations
- ✅ Get comprehensive, formatted responses
- ✅ No need to know specific API endpoints
- ✅ Conversational interface for questions

**Example**:
```
User types: "Create a shipment from LA to NYC and optimize it"

Claude autonomously:
1. Creates the shipment
2. Runs 3D packing optimization
3. Checks real weather/traffic
4. Predicts damage risk
5. Generates AI recommendations
6. Returns comprehensive report

All from one natural language prompt! 🚀
```
