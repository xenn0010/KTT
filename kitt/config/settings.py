from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """KITT application settings"""

    # FastAPI
    FASTAPI_HOST: str = "0.0.0.0"
    FASTAPI_PORT: int = 8000
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "sqlite:///./kitt.db"

    # Redpanda
    REDPANDA_BOOTSTRAP_SERVERS: str = "localhost:9092"

    # Anthropic
    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_MODEL: str = "claude-3-5-haiku-20250219"

    # Weather API (OpenWeatherMap)
    WEATHER_API_KEY: str = ""
    WEATHER_API_URL: str = "https://api.openweathermap.org/data/2.5"

    # Traffic API (TomTom)
    TRAFFIC_API_KEY: str = ""
    TRAFFIC_API_URL: str = "https://api.tomtom.com/traffic/services/4"

    # Route API (OpenRouteService)
    ROUTE_API_KEY: str = ""
    ROUTE_API_URL: str = "https://api.openrouteservice.org/v2"

    # Redis Cache
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_TTL_WEATHER: int = 1800
    CACHE_TTL_TRAFFIC: int = 300
    CACHE_TTL_ROUTE: int = 86400

    # DeepPack3D
    DEEPPACK3D_METHOD: str = "bl"
    DEEPPACK3D_LOOKAHEAD: int = 5

    # Neo4j Graph Database
    NEO4J_URI: str = ""
    NEO4J_USERNAME: str = "neo4j"
    NEO4J_PASSWORD: str = ""
    NEO4J_DATABASE: str = "neo4j"
    AURA_INSTANCEID: Optional[str] = None
    AURA_INSTANCENAME: Optional[str] = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Ignore extra fields from .env


settings = Settings()
