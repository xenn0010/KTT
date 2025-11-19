"""
Geocoding Service - Convert city names to coordinates
Uses OpenWeatherMap Geocoding API (free with weather API key)
"""

import httpx
import logging
from typing import Dict, Optional, Tuple
from config.settings import settings

logger = logging.getLogger(__name__)


class GeocodingService:
    """Geocoding service to convert city names to coordinates"""

    def __init__(self):
        self.api_key = settings.WEATHER_API_KEY
        self.client = httpx.AsyncClient(timeout=10.0)
        self._cache = {}  # Simple in-memory cache

    async def get_coordinates(self, city: str) -> Optional[Tuple[float, float]]:
        """
        Get coordinates for a city

        Args:
            city: City name (e.g., "Los Angeles", "New York, NY")

        Returns:
            (lat, lon) tuple or None if not found
        """
        # Check cache
        if city in self._cache:
            return self._cache[city]

        try:
            url = "http://api.openweathermap.org/geo/1.0/direct"
            params = {
                "q": city,
                "limit": 1,
                "appid": self.api_key
            }

            response = await self.client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            if data and len(data) > 0:
                lat = data[0]["lat"]
                lon = data[0]["lon"]
                coords = (lat, lon)
                self._cache[city] = coords
                return coords

            logger.warning(f"No coordinates found for city: {city}")
            return None

        except Exception as e:
            logger.error(f"Error geocoding city {city}: {e}")
            # Return approximate coordinates for major cities as fallback
            return self._get_fallback_coordinates(city)

    def _get_fallback_coordinates(self, city: str) -> Optional[Tuple[float, float]]:
        """Fallback coordinates for major US cities"""
        fallback_coords = {
            "los angeles": (34.0522, -118.2437),
            "new york": (40.7128, -74.0060),
            "chicago": (41.8781, -87.6298),
            "houston": (29.7604, -95.3698),
            "phoenix": (33.4484, -112.0740),
            "philadelphia": (39.9526, -75.1652),
            "san antonio": (29.4241, -98.4936),
            "san diego": (32.7157, -117.1611),
            "dallas": (32.7767, -96.7970),
            "san jose": (37.3382, -121.8863),
            "austin": (30.2672, -97.7431),
            "jacksonville": (30.3322, -81.6557),
            "fort worth": (32.7555, -97.3308),
            "columbus": (39.9612, -82.9988),
            "charlotte": (35.2271, -80.8431),
            "san francisco": (37.7749, -122.4194),
            "indianapolis": (39.7684, -86.1581),
            "seattle": (47.6062, -122.3321),
            "denver": (39.7392, -104.9903),
            "boston": (42.3601, -71.0589),
            "atlanta": (33.7490, -84.3880),
            "miami": (25.7617, -80.1918),
            "detroit": (42.3314, -83.0458),
            "nashville": (36.1627, -86.7816),
            "portland": (45.5152, -122.6784),
            "las vegas": (36.1699, -115.1398),
            "baltimore": (39.2904, -76.6122),
            "milwaukee": (43.0389, -87.9065),
            "albuquerque": (35.0844, -106.6504),
            "tucson": (32.2226, -110.9747),
            "fresno": (36.7378, -119.7871),
            "sacramento": (38.5816, -121.4944),
            "kansas city": (39.0997, -94.5786),
            "mesa": (33.4152, -111.8315),
            "omaha": (41.2565, -95.9345),
            "cleveland": (41.4993, -81.6944),
            "virginia beach": (36.8529, -75.9780),
            "oakland": (37.8044, -122.2712),
            "raleigh": (35.7796, -78.6382),
            "minneapolis": (44.9778, -93.2650),
            "tampa": (27.9506, -82.4572)
        }

        city_lower = city.lower().strip()
        coords = fallback_coords.get(city_lower)

        if coords:
            self._cache[city] = coords
            logger.info(f"Using fallback coordinates for {city}")

        return coords

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


# Singleton instance
_geocoding_service = None


async def get_geocoding_service() -> GeocodingService:
    """Get or create geocoding service instance"""
    global _geocoding_service
    if _geocoding_service is None:
        _geocoding_service = GeocodingService()
    return _geocoding_service
