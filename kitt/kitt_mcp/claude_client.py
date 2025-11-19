from anthropic import Anthropic, AsyncAnthropic
from typing import Optional, Dict, Any, List
import logging
import json

from config.settings import settings

logger = logging.getLogger(__name__)


class ClaudeClient:
    """Claude Haiku 4.5 client for AI-powered freight analysis"""

    def __init__(self):
        self.api_key = settings.ANTHROPIC_API_KEY
        self.model = settings.ANTHROPIC_MODEL
        self.client = Anthropic(api_key=self.api_key) if self.api_key else None
        self.async_client = AsyncAnthropic(api_key=self.api_key) if self.api_key else None

        if not self.client:
            logger.warning("Anthropic API key not configured")

    def _create_system_prompt(self) -> str:
        """Create system prompt for Claude"""
        return """You are KITT, an AI freight optimization assistant specializing in:

1. **Shipment Analysis**: Analyzing freight shipments for optimal loading strategies
2. **Route Optimization**: Recommending best routes based on weather, traffic, and road conditions
3. **Damage Prediction**: Assessing risk factors that could lead to shipment damage
4. **Delay Prediction**: Predicting potential delays based on route conditions

Provide concise, actionable recommendations. Use structured output when possible.
Always consider: safety, efficiency, cost optimization, and damage prevention.
"""

    async def analyze_shipment(
        self,
        shipment_data: dict,
        items: List[dict]
    ) -> Dict[str, Any]:
        """
        Analyze shipment and provide loading strategy

        Args:
            shipment_data: Shipment details (origin, destination, priority, etc.)
            items: List of items to be shipped

        Returns:
            dict: Analysis with recommendations
        """
        if not self.async_client:
            return {
                "error": "Claude API not configured",
                "recommendations": []
            }

        try:
            prompt = f"""Analyze this freight shipment and provide loading recommendations:

**Shipment Details:**
- Origin: {shipment_data.get('origin')}
- Destination: {shipment_data.get('destination')}
- Priority: {shipment_data.get('priority')}
- Number of items: {len(items)}

**Items:**
{json.dumps(items, indent=2)}

Provide:
1. Recommended loading strategy
2. Items that require special handling
3. Potential risks to consider
4. Optimal truck selection criteria

Format response as JSON with keys: strategy, special_handling, risks, truck_criteria
"""

            message = await self.async_client.messages.create(
                model=self.model,
                max_tokens=1024,
                temperature=0.3,
                system=self._create_system_prompt(),
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            response_text = message.content[0].text

            # Try to parse as JSON, fallback to text
            try:
                result = json.loads(response_text)
            except json.JSONDecodeError:
                result = {
                    "analysis": response_text,
                    "raw_response": True
                }

            logger.info(f"Analyzed shipment {shipment_data.get('id')}")
            return result

        except Exception as e:
            logger.error(f"Error analyzing shipment: {e}")
            return {
                "error": str(e),
                "recommendations": []
            }

    async def predict_delays(
        self,
        route_data: dict,
        weather_data: dict = None,
        traffic_data: dict = None
    ) -> Dict[str, Any]:
        """
        Predict potential delays based on route conditions

        Args:
            route_data: Route information
            weather_data: Weather conditions
            traffic_data: Traffic information

        Returns:
            dict: Delay prediction with recommendations
        """
        if not self.async_client:
            return {
                "error": "Claude API not configured",
                "delay_prediction": "unknown"
            }

        try:
            prompt = f"""Analyze this route and predict potential delays:

**Route:**
- From: {route_data.get('origin')}
- To: {route_data.get('destination')}
- Distance: {route_data.get('distance_km')} km
- Estimated Duration: {route_data.get('duration_minutes')} minutes

**Weather Conditions:**
{json.dumps(weather_data, indent=2) if weather_data else 'Not available'}

**Traffic Conditions:**
{json.dumps(traffic_data, indent=2) if traffic_data else 'Not available'}

Provide:
1. Delay probability (low/medium/high)
2. Estimated delay in minutes (if any)
3. Contributing factors
4. Mitigation recommendations

Format response as JSON with keys: delay_probability, estimated_delay_minutes, factors, recommendations
"""

            message = await self.async_client.messages.create(
                model=self.model,
                max_tokens=1024,
                temperature=0.3,
                system=self._create_system_prompt(),
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            response_text = message.content[0].text

            try:
                result = json.loads(response_text)
            except json.JSONDecodeError:
                result = {
                    "prediction": response_text,
                    "raw_response": True
                }

            logger.info(f"Predicted delays for route {route_data.get('route_id')}")
            return result

        except Exception as e:
            logger.error(f"Error predicting delays: {e}")
            return {
                "error": str(e),
                "delay_prediction": "error"
            }

    async def analyze_damage_risk(
        self,
        shipment_data: dict,
        route_data: dict,
        weather_data: dict = None,
        packing_data: dict = None
    ) -> Dict[str, Any]:
        """
        Analyze damage risk for shipment

        Args:
            shipment_data: Shipment details
            route_data: Route information
            weather_data: Weather conditions
            packing_data: Packing plan details

        Returns:
            dict: Risk analysis with recommendations
        """
        if not self.async_client:
            return {
                "error": "Claude API not configured",
                "risk_level": "unknown"
            }

        try:
            prompt = f"""Analyze damage risk for this freight shipment:

**Shipment:**
{json.dumps(shipment_data, indent=2)}

**Route:**
{json.dumps(route_data, indent=2)}

**Weather:**
{json.dumps(weather_data, indent=2) if weather_data else 'Not available'}

**Packing:**
{json.dumps(packing_data, indent=2) if packing_data else 'Not available'}

Provide:
1. Overall risk level (LOW/MEDIUM/HIGH/CRITICAL)
2. Risk score (0-100)
3. Top 3 contributing factors with weights
4. Specific recommendations to reduce risk

Format response as JSON with keys: risk_level, risk_score, contributing_factors, recommendations
"""

            message = await self.async_client.messages.create(
                model=self.model,
                max_tokens=1536,
                temperature=0.2,
                system=self._create_system_prompt(),
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            response_text = message.content[0].text

            try:
                result = json.loads(response_text)
            except json.JSONDecodeError:
                result = {
                    "analysis": response_text,
                    "raw_response": True
                }

            logger.info(f"Analyzed damage risk for shipment {shipment_data.get('id')}")
            return result

        except Exception as e:
            logger.error(f"Error analyzing damage risk: {e}")
            return {
                "error": str(e),
                "risk_level": "error"
            }

    async def optimize_route(
        self,
        origin: str,
        destination: str,
        route_options: List[dict],
        constraints: dict = None
    ) -> Dict[str, Any]:
        """
        Recommend optimal route from multiple options

        Args:
            origin: Starting point
            destination: End point
            route_options: List of possible routes with metrics
            constraints: Additional constraints (deadline, priorities, etc.)

        Returns:
            dict: Route recommendation
        """
        if not self.async_client:
            return {
                "error": "Claude API not configured",
                "recommended_route": None
            }

        try:
            prompt = f"""Recommend the optimal route for this freight shipment:

**Journey:**
- From: {origin}
- To: {destination}

**Route Options:**
{json.dumps(route_options, indent=2)}

**Constraints:**
{json.dumps(constraints, indent=2) if constraints else 'None specified'}

Analyze each route considering:
- Total travel time
- Distance
- Weather conditions
- Traffic levels
- Road quality
- Safety
- Cost efficiency

Provide:
1. Recommended route ID
2. Reasoning for recommendation
3. Alternative routes ranked
4. Estimated arrival time

Format response as JSON with keys: recommended_route_id, reasoning, alternatives, estimated_arrival
"""

            message = await self.async_client.messages.create(
                model=self.model,
                max_tokens=1536,
                temperature=0.3,
                system=self._create_system_prompt(),
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            response_text = message.content[0].text

            try:
                result = json.loads(response_text)
            except json.JSONDecodeError:
                result = {
                    "recommendation": response_text,
                    "raw_response": True
                }

            logger.info(f"Optimized route from {origin} to {destination}")
            return result

        except Exception as e:
            logger.error(f"Error optimizing route: {e}")
            return {
                "error": str(e),
                "recommended_route": None
            }

    def count_tokens(self, text: str) -> int:
        """
        Estimate token count for text

        Args:
            text: Text to count tokens for

        Returns:
            int: Estimated token count
        """
        if not self.client:
            return 0

        try:
            result = self.client.count_tokens(text)
            return result
        except Exception as e:
            logger.error(f"Error counting tokens: {e}")
            # Rough estimation: ~4 characters per token
            return len(text) // 4


# Global Claude client instance
claude = ClaudeClient()
