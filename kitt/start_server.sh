#!/bin/bash

echo "🚀 Starting KITT Freight Optimizer Server"
echo "=========================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found, copying from .env.example"
    cp .env.example .env
    echo "✅ Created .env file"
fi

# Start the server
echo "🔌 Starting FastAPI server on http://localhost:8000"
echo ""
echo "WebSocket endpoints:"
echo "  - ws://localhost:8000/ws/freight"
echo "  - ws://localhost:8000/ws/packing"
echo "  - ws://localhost:8000/ws/notifications"
echo ""
echo "REST endpoints:"
echo "  - http://localhost:8000 (API info)"
echo "  - http://localhost:8000/health (Health check)"
echo "  - http://localhost:8000/stats (Connection stats)"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=========================================="
echo ""

python3 api/main.py
