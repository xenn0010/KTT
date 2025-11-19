"""
Weather Service - OpenWeatherMap API Integration
Provides real weather data for route conditions
"""

import httpx
import logging
from typing import Dict, Optional, Tuple
from config.settings import settings

logger = logging.getLogger(__name__)


class WeatherService:
    """OpenWeatherMap API service for weather data"""

    def __init__(self):
        self.api_key = settings.WEATHER_API_KEY
        self.api_url = settings.WEATHER_API_URL
        self.client = httpx.AsyncClient(timeout=10.0)

    async def get_weather_by_city(self, city: str) -> Dict:
        """
        Get current weather for a city

        Args:
            city: City name (e.g., "Los Angeles", "New York")

        Returns:
            Weather data including temperature, conditions, precipitation
        """
        try:
            url = f"{self.api_url}/weather"
            params = {
                "q": city,
                "appid": self.api_key,
                "units": "imperial"  # Fahrenheit
            }

            response = await self.client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            return {
                "condition": data["weather"][0]["main"].lower(),
                "description": data["weather"][0]["description"],
                "temperature": data["main"]["temp"],
                "feels_like": data["main"]["feels_like"],
                "humidity": data["main"]["humidity"],
                "precipitation_probability": data.get("pop", 0) * 100,  # If available
                "wind_speed": data["wind"]["speed"],
                "visibility": data.get("visibility", 10000) / 1000,  # Convert to km
                "clouds": data["clouds"]["all"]
            }

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                logger.error("Invalid OpenWeatherMap API key")
                return self._mock_weather()
            logger.error(f"Weather API error: {e}")
            return self._mock_weather()
        except Exception as e:
            logger.error(f"Error fetching weather: {e}")
            return self._mock_weather()

    async def get_weather_by_coordinates(self, lat: float, lon: float) -> Dict:
        """
        Get current weather by coordinates

        Args:
            lat: Latitude
            lon: Longitude

        Returns:
            Weather data
        """
        try:
            url = f"{self.api_url}/weather"
            params = {
                "lat": lat,
                "lon": lon,
                "appid": self.api_key,
                "units": "imperial"
            }

            response = await self.client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            return {
                "condition": data["weather"][0]["main"].lower(),
                "description": data["weather"][0]["description"],
                "temperature": data["main"]["temp"],
                "feels_like": data["main"]["feels_like"],
                "humidity": data["main"]["humidity"],
                "wind_speed": data["wind"]["speed"],
                "visibility": data.get("visibility", 10000) / 1000,
                "clouds": data["clouds"]["all"]
            }

        except Exception as e:
            logger.error(f"Error fetching weather by coordinates: {e}")
            return self._mock_weather()

    async def get_route_weather(self, origin: str, destination: str) -> Dict:
        """
        Get weather conditions along a route

        Args:
            origin: Starting city
            destination: Ending city

        Returns:
            Weather for origin, destination, and severity assessment
        """
        try:
            origin_weather = await self.get_weather_by_city(origin)
            dest_weather = await self.get_weather_by_city(destination)

            # Calculate severity based on conditions
            severity = self._calculate_weather_severity(origin_weather, dest_weather)

            return {
                "origin": {
                    "city": origin,
                    "weather": origin_weather
                },
                "destination": {
                    "city": destination,
                    "weather": dest_weather
                },
                "severity": severity,
                "warnings": self._generate_weather_warnings(origin_weather, dest_weather)
            }

        except Exception as e:
            logger.error(f"Error fetching route weather: {e}")
            return {
                "origin": {"city": origin, "weather": self._mock_weather()},
                "destination": {"city": destination, "weather": self._mock_weather()},
                "severity": 1,
                "warnings": []
            }

    def _calculate_weather_severity(self, origin: Dict, dest: Dict) -> int:
        """
        Calculate weather severity (1-5)

        1 = Clear
        2 = Cloudy
        3 = Rain/Snow
        4 = Heavy Rain/Snow
        5 = Severe Weather
        """
        conditions = [origin.get("condition", "clear"), dest.get("condition", "clear")]

        if any(c in ["thunderstorm", "tornado", "hurricane"] for c in conditions):
            return 5
        elif any(c in ["snow", "heavy rain"] for c in conditions):
            return 4
        elif any(c in ["rain", "drizzle"] for c in conditions):
            return 3
        elif any(c in ["clouds", "mist", "fog"] for c in conditions):
            return 2
        else:
            return 1

    def _generate_weather_warnings(self, origin: Dict, dest: Dict) -> list:
        """Generate weather warnings for route"""
        warnings = []

        for location, weather in [("origin", origin), ("destination", dest)]:
            condition = weather.get("condition", "clear")

            if condition in ["thunderstorm", "tornado", "hurricane"]:
                warnings.append(f"SEVERE: Dangerous weather at {location}")
            elif condition in ["snow", "heavy rain"]:
                warnings.append(f"WARNING: Heavy precipitation at {location}")
            elif weather.get("wind_speed", 0) > 25:
                warnings.append(f"WARNING: High winds at {location} ({weather['wind_speed']} mph)")
            elif weather.get("visibility", 10) < 1:
                warnings.append(f"WARNING: Low visibility at {location}")

        return warnings

    def _mock_weather(self) -> Dict:
        """Fallback mock weather data"""
        return {
            "condition": "clear",
            "description": "clear sky",
            "temperature": 72,
            "feels_like": 70,
            "humidity": 50,
            "precipitation_probability": 10,
            "wind_speed": 5,
            "visibility": 10,
            "clouds": 10
        }

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


# Singleton instance
_weather_service = None


async def get_weather_service() -> WeatherService:
    """Get or create weather service instance"""
    global _weather_service
    if _weather_service is None:
        _weather_service = WeatherService()
    return _weather_service
