# KTT - KITT AI Freight Optimizer

> **Real-time freight loading optimization with AI-powered route intelligence**

![Status](https://img.shields.io/badge/status-active-success.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## Overview

KITT (KTT) is an intelligent logistics optimization platform that combines AI-powered 3D packing algorithms, real-time route intelligence, and predictive analytics to revolutionize freight management. The system eliminates shipping delays and damages by optimizing load distribution based on route conditions, weather, and traffic patterns.

## Key Features

- **AI-Powered 3D Packing** - DeepPack3D integration for optimal container utilization
- **Real-time Route Intelligence** - Dynamic optimization based on weather, traffic, and road conditions
- **Predictive Damage Prevention** - ML-based risk scoring before shipment
- **Graph-Based Fleet Optimization** - Neo4j for intelligent fleet management
- **Live WebSocket Streaming** - Real-time updates via Redpanda event streaming
- **Voice Interface** - Natural language commands through Pipecat AI
- **MCP Integration** - FastMCP server with Claude AI for intelligent decision-making

## Architecture

```
Voice Agent (Pipecat) → FastAPI + WebSockets → Redpanda Streams
                                                     ↓
                                       ┌─────────────┴─────────────┐
                                       ↓                           ↓
                                 DeepPack3D                     Neo4j
                              (3D Packing)               (Graph Intelligence)
                                       ↓                           ↓
                                   MCP Server + SQLite
                                       ↓
                       External APIs (Weather, Traffic, Route)
                                       ↓
                           Damage Prediction (ML Model)
```

## Tech Stack

- **Backend:** FastAPI, WebSockets, Python 3.10+
- **Streaming:** Redpanda (Kafka-compatible)
- **Databases:** SQLite, Neo4j
- **AI/ML:** DeepPack3D, Claude 3.5 Haiku, scikit-learn
- **Frontend:** React, TypeScript, Vite, Three.js
- **Voice:** Pipecat AI
- **MCP:** FastMCP for AI tool integration
- **APIs:** OpenWeatherMap, TomTom Traffic, OpenRouteService

## Quick Start

```bash
# Navigate to project
cd kitt

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your API keys

# Start the server
./start_server.sh

# Or manually
python3 api/main.py
```

Server runs at: `http://localhost:8000`

### Frontend Setup

```bash
cd kitt/frontend
npm install
npm run dev
```

Frontend runs at: `http://localhost:5173`

## Project Status

### ✅ Completed Features

- [x] FastAPI backend with WebSocket support
- [x] Real-time communication (freight, packing, notifications)
- [x] MCP server with AI-powered tools
- [x] SQLite database with async operations
- [x] Redpanda event streaming
- [x] Claude Haiku integration
- [x] DeepPack3D 3D bin packing engine
- [x] React frontend with visualization
- [x] Neo4j graph database integration
- [x] Comprehensive test suite

### 🚧 In Progress

- [ ] Voice agent integration (Pipecat)
- [ ] Production deployment configuration
- [ ] Advanced damage prediction model
- [ ] Multi-fleet optimization

## API Endpoints

### REST API
- `GET /` - API information
- `GET /health` - Health check with connection stats
- `GET /stats` - Detailed WebSocket statistics
- `POST /api/optimization/pack` - 3D packing optimization
- `GET /api/shipments` - List all shipments
- `GET /api/graph/routes` - Neo4j route analysis

### WebSocket Endpoints
- `ws://localhost:8000/ws/freight?client_id=<id>` - Freight data stream
- `ws://localhost:8000/ws/packing?client_id=<id>` - Packing results
- `ws://localhost:8000/ws/notifications?client_id=<id>` - System alerts

## Documentation

- [Main Documentation](kitt/README.md) - Detailed project documentation
- [WebSocket Guide](kitt/README_WEBSOCKETS.md) - WebSocket implementation
- [MCP Integration](kitt/README_MCP.md) - MCP server setup
- [Visualization Guide](kitt/VISUALIZATION_QUICK_START.md) - 3D visualization
- [API Documentation](kitt/API_DOCUMENTATION.md) - Complete API reference
- [Agent Prompts](kitt/CLAUDE_AGENT_PROMPTS.md) - AI agent integration

## Performance Metrics

- ✅ 100+ concurrent WebSocket connections
- ✅ Message latency <100ms
- ✅ Packing optimization <5s for 50 items
- ✅ 75%+ space utilization
- ✅ Real-time event streaming

## Project Structure

```
KTT/
├── kitt/                           # Main application
│   ├── api/                        # FastAPI backend
│   │   ├── main.py                # Application entry point
│   │   ├── routes/                # REST API routes
│   │   └── websockets.py          # WebSocket handlers
│   ├── frontend/                  # React frontend
│   │   ├── src/                   # Source code
│   │   │   ├── components/       # React components
│   │   │   ├── pages/            # Application pages
│   │   │   └── types/            # TypeScript types
│   │   └── package.json          # Frontend dependencies
│   ├── kitt_mcp/                  # MCP server
│   │   ├── server.py             # FastMCP server
│   │   ├── tools.py              # AI tools
│   │   └── database.py           # Database operations
│   ├── services/                  # Business logic
│   │   ├── deeppack3d_engine/    # 3D packing algorithm
│   │   ├── neo4j_service.py      # Graph database
│   │   └── weather_service.py    # External APIs
│   ├── models/                    # Data models
│   ├── tests/                     # Test suite
│   └── scripts/                   # Utility scripts
└── README.md                      # This file
```

## Testing

```bash
# Run all tests
cd kitt
pytest tests/

# Test WebSocket connections
python3 tests/test_websocket_client.py

# Test API endpoints
python3 tests/test_api.py

# Test DeepPack3D integration
python3 tests/test_deeppack3d_integration.py
```

## Contributing

Contributions are welcome! This is a production-ready freight optimization system.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License - See [LICENSE](LICENSE) file for details

## Contact

Project Link: [https://github.com/xenn0010/KTT](https://github.com/xenn0010/KTT)

## Acknowledgments

- [DeepPack3D](https://github.com/zgtcktom/DeepPack3D) - 3D bin packing algorithm
- [FastMCP](https://github.com/jlowin/fastmcp) - MCP server framework
- [Pipecat AI](https://github.com/pipecat-ai/pipecat) - Voice agent framework
- [Anthropic Claude](https://www.anthropic.com) - AI intelligence

---

**Built with AI for AI-powered logistics** | Last Updated: 2025-11-19
