import asyncio
import websockets
import json
from datetime import datetime
from uuid import uuid4


async def test_freight_websocket():
    """Test freight WebSocket endpoint"""
    uri = "ws://localhost:8000/ws/freight?client_id=test-client-1"

    print(f"🔌 Connecting to {uri}...")

    async with websockets.connect(uri) as websocket:
        print("✅ Connected to freight endpoint")

        # Send heartbeat
        heartbeat_message = {
            "type": "heartbeat",
            "timestamp": datetime.utcnow().isoformat(),
            "payload": {},
            "correlation_id": str(uuid4())
        }
        await websocket.send(json.dumps(heartbeat_message))
        print("📤 Sent heartbeat")

        response = await websocket.recv()
        print(f"📥 Received: {response}")

        # Send shipment request
        shipment_request = {
            "type": "shipment_request",
            "timestamp": datetime.utcnow().isoformat(),
            "payload": {
                "shipment_id": "SH-001",
                "origin": "Chicago",
                "destination": "Dallas",
                "items": [
                    {"width": 50, "height": 40, "depth": 30, "weight": 25},
                    {"width": 60, "height": 50, "depth": 40, "weight": 35},
                    {"width": 45, "height": 35, "depth": 25, "weight": 20}
                ],
                "priority": "high"
            },
            "correlation_id": str(uuid4())
        }
        await websocket.send(json.dumps(shipment_request))
        print("📤 Sent shipment request")

        response = await websocket.recv()
        print(f"📥 Received: {response}")

        print("✅ Freight WebSocket test completed")


async def test_packing_websocket():
    """Test packing WebSocket endpoint"""
    uri = "ws://localhost:8000/ws/packing?client_id=test-client-2"

    print(f"\n🔌 Connecting to {uri}...")

    async with websockets.connect(uri) as websocket:
        print("✅ Connected to packing endpoint")

        # Send heartbeat
        heartbeat_message = {
            "type": "heartbeat",
            "timestamp": datetime.utcnow().isoformat(),
            "payload": {},
            "correlation_id": str(uuid4())
        }
        await websocket.send(json.dumps(heartbeat_message))
        print("📤 Sent heartbeat")

        response = await websocket.recv()
        print(f"📥 Received: {response}")

        # Send packing result
        packing_result = {
            "type": "packing_result",
            "timestamp": datetime.utcnow().isoformat(),
            "payload": {
                "shipment_id": "SH-001",
                "truck_id": "TRK-12",
                "placements": [
                    {
                        "item_id": 0,
                        "position": {"x": 0, "y": 0, "z": 0},
                        "dimensions": {"width": 50, "height": 40, "depth": 30},
                        "rotation": 0
                    }
                ],
                "utilization": 87.5,
                "risk_score": 15.3,
                "bins_used": 1
            },
            "correlation_id": str(uuid4())
        }
        await websocket.send(json.dumps(packing_result))
        print("📤 Sent packing result")

        response = await websocket.recv()
        print(f"📥 Received: {response}")

        print("✅ Packing WebSocket test completed")


async def test_notifications_websocket():
    """Test notifications WebSocket endpoint"""
    uri = "ws://localhost:8000/ws/notifications?client_id=test-client-3"

    print(f"\n🔌 Connecting to {uri}...")

    async with websockets.connect(uri) as websocket:
        print("✅ Connected to notifications endpoint")

        # Send weather alert
        weather_alert = {
            "type": "weather_alert",
            "timestamp": datetime.utcnow().isoformat(),
            "payload": {
                "route_id": "ROUTE-CHI-DAL",
                "alert_type": "rain",
                "severity": 3,
                "description": "Heavy rain expected along route",
                "valid_until": "2025-01-20T18:00:00Z"
            },
            "correlation_id": str(uuid4())
        }
        await websocket.send(json.dumps(weather_alert))
        print("📤 Sent weather alert")

        response = await websocket.recv()
        print(f"📥 Received: {response}")

        print("✅ Notifications WebSocket test completed")


async def test_concurrent_connections():
    """Test multiple concurrent connections"""
    print("\n🔌 Testing concurrent connections...")

    async def client(client_id: int, endpoint: str):
        uri = f"ws://localhost:8000/ws/{endpoint}?client_id=concurrent-{client_id}"
        async with websockets.connect(uri) as websocket:
            message = {
                "type": "heartbeat",
                "timestamp": datetime.utcnow().isoformat(),
                "payload": {"client_id": client_id},
                "correlation_id": str(uuid4())
            }
            await websocket.send(json.dumps(message))
            response = await websocket.recv()
            print(f"✅ Client {client_id} on {endpoint} received: {json.loads(response)['type']}")
            await asyncio.sleep(1)

    # Create 10 concurrent connections across different endpoints
    tasks = []
    for i in range(10):
        endpoint = ["freight", "packing", "notifications"][i % 3]
        tasks.append(client(i, endpoint))

    await asyncio.gather(*tasks)
    print("✅ Concurrent connections test completed")


async def main():
    """Run all WebSocket tests"""
    print("🧪 Starting KITT WebSocket Tests\n")
    print("=" * 60)

    try:
        await test_freight_websocket()
        await test_packing_websocket()
        await test_notifications_websocket()
        await test_concurrent_connections()

        print("\n" + "=" * 60)
        print("✅ All WebSocket tests passed!")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
