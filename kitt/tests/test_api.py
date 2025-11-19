"""
Test REST API Endpoints
"""

import asyncio
import httpx
from datetime import datetime


async def test_api():
    """Test all API endpoints"""

    print("=" * 80)
    print(" KITT REST API TEST")
    print("=" * 80)

    # Note: This requires the API to be running
    # Start with: uvicorn api.main:app --reload
    base_url = "http://localhost:8000"

    async with httpx.AsyncClient(timeout=30.0) as client:

        # Test 1: Health Check
        print("\n[Test 1] Health Check")
        try:
            response = await client.get(f"{base_url}/health")
            print(f"✅ Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Services: {data.get('services', {})}")
        except Exception as e:
            print(f"❌ Health check failed: {e}")

        # Test 2: Create Shipment
        print("\n[Test 2] Create Shipment")
        try:
            shipment_data = {
                "origin": "Los Angeles",
                "destination": "New York",
                "items": [
                    {
                        "width": 50,
                        "height": 40,
                        "depth": 30,
                        "weight": 25,
                        "fragile": False,
                        "stackable": True,
                        "description": "Test Box 1"
                    },
                    {
                        "width": 60,
                        "height": 50,
                        "depth": 40,
                        "weight": 30,
                        "fragile": True,
                        "stackable": False,
                        "description": "Test Box 2"
                    }
                ],
                "priority": "high",
                "deadline": datetime.now().isoformat()
            }

            response = await client.post(f"{base_url}/api/shipments", json=shipment_data)
            print(f"✅ Status: {response.status_code}")

            if response.status_code == 201:
                data = response.json()
                shipment_id = data.get("shipment_id")
                print(f"   Shipment ID: {shipment_id}")
                print(f"   Origin: {data.get('origin')}")
                print(f"   Destination: {data.get('destination')}")

                # Test 3: Get Shipment
                print("\n[Test 3] Get Shipment")
                response = await client.get(f"{base_url}/api/shipments/{shipment_id}")
                print(f"✅ Status: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    print(f"   Items: {len(data.get('items', []))}")

                # Test 4: Optimize Shipment
                print("\n[Test 4] Full Optimization")
                optimize_data = {
                    "shipment_id": shipment_id,
                    "include_ai_analysis": True,
                    "store_in_graph": True
                }

                response = await client.post(f"{base_url}/api/optimize", json=optimize_data)
                print(f"✅ Status: {response.status_code}")

                if response.status_code == 200:
                    data = response.json()
                    print(f"   Utilization: {data.get('packing', {}).get('utilization_percentage', 0)}%")
                    print(f"   Risk Level: {data.get('risk_assessment', {}).get('risk_level', 'N/A')}")
                    print(f"   Weather Severity: {data.get('route_conditions', {}).get('weather_severity', 0)}/5")

                # Test 5: Knowledge Graph
                print("\n[Test 5] Knowledge Graph Query")
                response = await client.get(f"{base_url}/api/graph/shipment/{shipment_id}")
                print(f"✅ Status: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    print(f"   Graph Items: {len(data.get('items', []))}")

                # Test 6: Analytics Dashboard
                print("\n[Test 6] Analytics Dashboard")
                response = await client.get(f"{base_url}/api/analytics/dashboard")
                print(f"✅ Status: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    print(f"   Total Shipments: {data.get('total_shipments', 0)}")

        except Exception as e:
            print(f"❌ API test failed: {e}")

    print("\n" + "=" * 80)
    print(" API TEST COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    print("\n⚠️  Make sure API is running: uvicorn api.main:app --reload\n")
    asyncio.run(test_api())
