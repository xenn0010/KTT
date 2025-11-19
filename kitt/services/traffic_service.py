"""
Traffic Service - TomTom Traffic API Integration
Provides real-time traffic data for route conditions
"""

import httpx
import logging
from typing import Dict, List, Optional
from config.settings import settings

logger = logging.getLogger(__name__)


class TrafficService:
    """TomTom Traffic API service"""

    def __init__(self):
        self.api_key = settings.TRAFFIC_API_KEY
        self.api_url = settings.TRAFFIC_API_URL
        self.client = httpx.AsyncClient(timeout=10.0)

    async def get_traffic_flow(
        self,
        lat: float,
        lon: float,
        zoom: int = 10
    ) -> Dict:
        """
        Get traffic flow data for a location

        Args:
            lat: Latitude
            lon: Longitude
            zoom: Zoom level (higher = more detail)

        Returns:
            Traffic flow information
        """
        try:
            url = f"{self.api_url}/incident/s4/incidentDetails"
            params = {
                "key": self.api_key,
                "point": f"{lat},{lon}",
                "unit": "MPH",
                "zoom": zoom
            }

            response = await self.client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            flow_data = data.get("flowSegmentData", {})

            return {
                "current_speed": flow_data.get("currentSpeed", 0),
                "free_flow_speed": flow_data.get("freeFlowSpeed", 0),
                "current_travel_time": flow_data.get("currentTravelTime", 0),
                "free_flow_travel_time": flow_data.get("freeFlowTravelTime", 0),
                "confidence": flow_data.get("confidence", 0.5),
                "road_closure": flow_data.get("roadClosure", False)
            }

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 403:
                logger.error("Invalid TomTom API key")
                return self._mock_traffic_flow()
            logger.error(f"Traffic API error: {e}")
            return self._mock_traffic_flow()
        except Exception as e:
            logger.error(f"Error fetching traffic flow: {e}")
            return self._mock_traffic_flow()

    async def get_traffic_incidents(
        self,
        min_lat: float,
        min_lon: float,
        max_lat: float,
        max_lon: float
    ) -> List[Dict]:
        """
        Get traffic incidents in a bounding box

        Args:
            min_lat: Minimum latitude
            min_lon: Minimum longitude
            max_lat: Maximum latitude
            max_lon: Maximum longitude

        Returns:
            List of traffic incidents
        """
        try:
            url = f"{self.api_url}/incidentDetails"
            params = {
                "key": self.api_key,
                "bbox": f"{min_lon},{min_lat},{max_lon},{max_lat}",
                "fields": "{incidents{type,geometry{type,coordinates},properties{id,iconCategory,magnitudeOfDelay,events{description,code,iconCategory},startTime,endTime,from,to,length,delay,roadNumbers,timeValidity}}}",
                "language": "en-US"
            }

            response = await self.client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            incidents = []
            for incident in data.get("incidents", []):
                props = incident.get("properties", {})
                incidents.append({
                    "id": props.get("id"),
                    "type": props.get("iconCategory"),
                    "description": props.get("events", [{}])[0].get("description", ""),
                    "delay": props.get("delay", 0),
                    "magnitude": props.get("magnitudeOfDelay", 0),
                    "from": props.get("from"),
                    "to": props.get("to"),
                    "length": props.get("length", 0)
                })

            return incidents

        except Exception as e:
            logger.error(f"Error fetching traffic incidents: {e}")
            return []

    async def get_route_traffic(
        self,
        origin_lat: float,
        origin_lon: float,
        dest_lat: float,
        dest_lon: float
    ) -> Dict:
        """
        Get traffic conditions for a route

        Args:
            origin_lat: Origin latitude
            origin_lon: Origin longitude
            dest_lat: Destination latitude
            dest_lon: Destination longitude

        Returns:
            Traffic conditions and incidents
        """
        try:
            # Get traffic flow at origin and destination
            origin_flow = await self.get_traffic_flow(origin_lat, origin_lon)
            dest_flow = await self.get_traffic_flow(dest_lat, dest_lon)

            # Get incidents in bounding box
            min_lat = min(origin_lat, dest_lat) - 0.5
            max_lat = max(origin_lat, dest_lat) + 0.5
            min_lon = min(origin_lon, dest_lon) - 0.5
            max_lon = max(origin_lon, dest_lon) + 0.5

            incidents = await self.get_traffic_incidents(min_lat, min_lon, max_lat, max_lon)

            # Calculate traffic level
            level, delay = self._calculate_traffic_level(origin_flow, dest_flow, incidents)

            return {
                "level": level,
                "delay_minutes": delay,
                "origin_flow": origin_flow,
                "destination_flow": dest_flow,
                "incidents": incidents,
                "incident_count": len(incidents),
                "warnings": self._generate_traffic_warnings(incidents)
            }

        except Exception as e:
            logger.error(f"Error getting route traffic: {e}")
            return self._mock_route_traffic()

    def _calculate_traffic_level(
        self,
        origin_flow: Dict,
        dest_flow: Dict,
        incidents: List[Dict]
    ) -> tuple:
        """
        Calculate traffic level and estimated delay

        Returns:
            (level: str, delay_minutes: int)
        """
        # Calculate speed ratio (current vs free flow)
        origin_ratio = (
            origin_flow.get("current_speed", 60) /
            max(origin_flow.get("free_flow_speed", 60), 1)
        )
        dest_ratio = (
            dest_flow.get("current_speed", 60) /
            max(dest_flow.get("free_flow_speed", 60), 1)
        )

        avg_ratio = (origin_ratio + dest_ratio) / 2

        # Calculate delay from incidents
        incident_delay = sum(i.get("delay", 0) for i in incidents) / 60  # Convert to minutes

        # Determine level (must match DB constraint: low/medium/high/severe)
        if avg_ratio > 0.8 and len(incidents) == 0:
            level = "low"
            delay = 0
        elif avg_ratio > 0.6 and len(incidents) < 3:
            level = "medium"
            delay = int(5 + incident_delay)
        elif avg_ratio > 0.4:
            level = "high"
            delay = int(15 + incident_delay)
        else:
            level = "severe"
            delay = int(30 + incident_delay)

        return level, delay

    def _generate_traffic_warnings(self, incidents: List[Dict]) -> List[str]:
        """Generate traffic warnings"""
        warnings = []

        for incident in incidents:
            incident_type = incident.get("type", "")
            delay = incident.get("delay", 0) / 60  # Convert to minutes

            if incident_type in ["ACCIDENT", "ROAD_CLOSED"]:
                warnings.append(f"CRITICAL: {incident.get('description', 'Road incident')}")
            elif delay > 10:
                warnings.append(f"WARNING: {incident.get('description', 'Traffic delay')} (+{int(delay)} min)")

        return warnings

    def _mock_traffic_flow(self) -> Dict:
        """Fallback mock traffic flow"""
        return {
            "current_speed": 55,
            "free_flow_speed": 60,
            "current_travel_time": 100,
            "free_flow_travel_time": 90,
            "confidence": 0.8,
            "road_closure": False
        }

    def _mock_route_traffic(self) -> Dict:
        """Fallback mock route traffic"""
        return {
            "level": "medium",
            "delay_minutes": 15,
            "origin_flow": self._mock_traffic_flow(),
            "destination_flow": self._mock_traffic_flow(),
            "incidents": [],
            "incident_count": 0,
            "warnings": []
        }

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


# Singleton instance
_traffic_service = None


async def get_traffic_service() -> TrafficService:
    """Get or create traffic service instance"""
    global _traffic_service
    if _traffic_service is None:
        _traffic_service = TrafficService()
    return _traffic_service
