import asyncio
import logging
from typing import Optional
from contextlib import asynccontextmanager

try:
    from fastmcp import FastMCP
except ImportError:
    FastMCP = None
    logging.warning("fastmcp not installed, MCP server will not be available")

from kitt_mcp.database import db
from kitt_mcp.tools import tools
from kitt_mcp.graph_tools import graph_tools
from services.neo4j_service import get_neo4j_service
from config.settings import settings

logger = logging.getLogger(__name__)


# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(mcp_app):
    """Handle startup and shutdown events"""
    logger.info("🚀 Starting KITT MCP Server")

    # Initialize SQL database
    try:
        await db.initialize_schema()
        logger.info("✅ SQL Database initialized")
    except Exception as e:
        logger.error(f"❌ SQL Database initialization failed: {e}")

    # Initialize Neo4j graph database
    try:
        neo4j = await get_neo4j_service()
        logger.info("✅ Neo4j Graph Database connected")
    except Exception as e:
        logger.error(f"❌ Neo4j connection failed: {e}")

    yield

    # Cleanup on shutdown
    logger.info("🛑 Shutting down KITT MCP Server")
    await db.disconnect()

    # Close Neo4j connection
    try:
        neo4j = await get_neo4j_service()
        await neo4j.close()
    except:
        pass


# Initialize FastMCP server
if FastMCP:
    mcp = FastMCP("KITT Freight Optimizer", lifespan=lifespan)
else:
    mcp = None
    logger.error("FastMCP not available - install with: pip install fastmcp")


# Register MCP Tools
if mcp:

    @mcp.tool()
    async def get_shipment_data(shipment_id: str) -> dict:
        """
        Get complete shipment data including items, packing plans, and predictions

        Args:
            shipment_id: The unique shipment identifier

        Returns:
            Complete shipment data with all related information
        """
        return await tools.get_shipment_data(shipment_id)

    @mcp.tool()
    async def create_shipment(
        origin: str,
        destination: str,
        items: list,
        priority: str = "medium",
        deadline: Optional[str] = None
    ) -> dict:
        """
        Create a new shipment with items

        Args:
            origin: Starting location
            destination: Destination location
            items: List of items with dimensions (width, height, depth, weight)
            priority: Shipment priority (low/medium/high/critical)
            deadline: Optional deadline in ISO format

        Returns:
            Created shipment information

        Example items format:
        [
            {
                "width": 50,
                "height": 40,
                "depth": 30,
                "weight": 25,
                "fragile": false,
                "stackable": true,
                "description": "Electronics"
            }
        ]
        """
        return await tools.create_shipment(
            origin=origin,
            destination=destination,
            items=items,
            priority=priority,
            deadline=deadline
        )

    @mcp.tool()
    async def optimize_packing(
        shipment_id: str,
        truck_id: Optional[str] = None
    ) -> dict:
        """
        Optimize 3D packing for a shipment

        Args:
            shipment_id: Shipment to optimize
            truck_id: Optional specific truck (will auto-select if not provided)

        Returns:
            Packing plan with utilization metrics and placement coordinates
        """
        return await tools.optimize_packing(shipment_id, truck_id)

    @mcp.tool()
    async def get_route_conditions(
        route_id: str,
        origin: Optional[str] = None,
        destination: Optional[str] = None
    ) -> dict:
        """
        Get current route conditions including weather, traffic, and road quality

        Args:
            route_id: Route identifier
            origin: Origin location (if route_id not in database)
            destination: Destination location (if route_id not in database)

        Returns:
            Current and historical route conditions
        """
        return await tools.get_route_conditions(route_id, origin, destination)

    @mcp.tool()
    async def predict_damage_risk(
        shipment_id: str,
        route_id: Optional[str] = None
    ) -> dict:
        """
        Predict damage risk for shipment using AI analysis

        Uses Claude Haiku 4.5 to analyze:
        - Shipment characteristics
        - Route conditions
        - Weather forecasts
        - Packing quality
        - Historical damage patterns

        Args:
            shipment_id: Shipment to analyze
            route_id: Optional route for condition analysis

        Returns:
            Risk assessment with level (LOW/MEDIUM/HIGH/CRITICAL),
            score (0-100), contributing factors, and recommendations
        """
        return await tools.predict_damage_risk(shipment_id, route_id)

    @mcp.tool()
    async def publish_event(event_type: str, event_data: dict) -> dict:
        """
        Publish event to Redpanda event stream

        Args:
            event_type: Type of event (shipment_request, packing_result, route_update, etc.)
            event_data: Event payload data

        Returns:
            Success status and topic information

        Supported event types:
        - shipment_request
        - packing_result
        - route_update
        - weather_alert
        - traffic_update
        - damage_prediction
        - notification
        """
        return await tools.publish_event(event_type, event_data)

    @mcp.tool()
    async def analyze_shipment_with_ai(shipment_id: str) -> dict:
        """
        Get AI-powered analysis and recommendations for shipment

        Uses Claude Haiku 4.5 to provide:
        - Recommended loading strategy
        - Items requiring special handling
        - Potential risks
        - Optimal truck selection criteria

        Args:
            shipment_id: Shipment to analyze

        Returns:
            AI analysis with structured recommendations
        """
        return await tools.analyze_shipment_with_ai(shipment_id)

    # ==================== NEO4J GRAPH DATABASE TOOLS ====================

    @mcp.tool()
    async def store_shipment_in_knowledge_graph(
        shipment_id: str,
        origin: str,
        destination: str,
        items: list,
        status: str = "pending",
        priority: str = "medium",
        deadline: str = None
    ) -> dict:
        """
        Store shipment in Neo4j knowledge graph with all relationships

        Creates graph structure:
        - Shipment node with properties
        - Item nodes linked to shipment
        - Location nodes for origin/destination
        - Relationships: (Shipment)-[:CONTAINS]->(Item)
        - Relationships: (Shipment)-[:FROM]->(Origin)
        - Relationships: (Shipment)-[:TO]->(Destination)

        This enables graph-based queries like:
        - Find all shipments between two cities
        - Discover patterns in successful deliveries
        - Identify optimal truck routes
        - Learn from historical data

        Args:
            shipment_id: Unique identifier
            origin: Origin city/location
            destination: Destination city/location
            items: List of dicts with width, height, depth, weight
            status: pending/in_transit/delivered
            priority: low/medium/high/critical
            deadline: ISO datetime string

        Returns:
            Graph structure with node counts and relationships
        """
        return await graph_tools.store_shipment_in_graph(
            shipment_id=shipment_id,
            origin=origin,
            destination=destination,
            items=items,
            status=status,
            priority=priority,
            deadline=deadline
        )

    @mcp.tool()
    async def get_shipment_knowledge_graph(shipment_id: str) -> dict:
        """
        Get complete knowledge graph view of shipment

        Returns shipment with ALL related nodes and relationships:
        - Shipment properties
        - All items (dimensions, weight, properties)
        - Origin and destination locations
        - Assigned truck (if any)
        - Route being used (if any)
        - Similar historical shipments for comparison

        This gives Claude a complete context about the shipment
        and its relationships in the freight network.

        Args:
            shipment_id: Shipment to query

        Returns:
            Complete graph structure with all relationships
        """
        return await graph_tools.get_shipment_knowledge_graph(shipment_id)

    @mcp.tool()
    async def find_optimal_trucks_from_graph(
        total_weight: float,
        total_volume: float,
        origin: str
    ) -> list:
        """
        Find best available trucks using graph database

        Uses graph queries to find trucks that:
        - Meet weight capacity requirements
        - Meet volume capacity requirements
        - Are currently available (not assigned)
        - Are near origin location (if data exists)

        Returns trucks ranked by:
        - Capacity match (smallest that fits = best)
        - Current location proximity
        - Historical performance on similar routes

        Args:
            total_weight: Required weight capacity (kg)
            total_volume: Required volume capacity (cubic cm)
            origin: Origin location name

        Returns:
            List of suitable trucks with capacity details
        """
        return await graph_tools.find_optimal_trucks(
            total_weight=total_weight,
            total_volume=total_volume,
            origin=origin
        )

    @mcp.tool()
    async def get_location_analytics_from_graph(location_name: str) -> dict:
        """
        Get comprehensive analytics for a location from graph

        Analyzes freight activity at location:
        - Shipments originated here
        - Shipments received here
        - Routes starting here
        - Routes ending here
        - Total freight throughput
        - Busiest times/patterns

        Useful for:
        - Capacity planning
        - Warehouse optimization
        - Understanding freight flows
        - Predicting demand

        Args:
            location_name: City or location to analyze

        Returns:
            Analytics with counts, trends, and insights
        """
        return await graph_tools.get_location_analytics(location_name)

    @mcp.tool()
    async def find_historical_shipment_patterns(
        origin: str,
        destination: str
    ) -> list:
        """
        Find historical shipment patterns between two locations

        Discovers patterns like:
        - What trucks work best for this route?
        - Average delivery times
        - Common packing strategies
        - Seasonal variations
        - Success/failure rates

        Claude can use this to:
        - Make better recommendations
        - Predict realistic timelines
        - Avoid past mistakes
        - Learn from successful deliveries

        Args:
            origin: Starting location
            destination: Ending location

        Returns:
            Historical shipments with outcomes and learnings
        """
        return await graph_tools.find_historical_patterns(
            origin=origin,
            destination=destination
        )

    @mcp.tool()
    async def get_freight_network_overview() -> dict:
        """
        Get high-level overview of entire freight network

        Network-wide statistics:
        - Total shipments in system
        - Total trucks and utilization
        - Total locations served
        - Total routes established
        - Network health metrics

        Useful for:
        - Executive dashboards
        - Capacity planning
        - Network optimization
        - Performance monitoring

        Returns:
            Network statistics and health metrics
        """
        return await graph_tools.get_network_overview()

    @mcp.tool()
    async def query_knowledge_graph_with_cypher(
        cypher_query: str,
        parameters: dict = None
    ) -> list:
        """
        **POWERFUL**: Execute custom Cypher queries on knowledge graph

        This is Claude's most powerful graph tool - allows writing
        custom graph queries to answer complex questions.

        Use cases:
        - "Find all shipments from LA to NYC in last 30 days"
        - "What trucks have >80% average utilization?"
        - "Show busiest freight corridors by volume"
        - "Find items frequently damaged on rough roads"
        - "Discover seasonal shipping patterns"
        - "Identify underutilized trucks"

        Cypher is Neo4j's graph query language. Examples:

        Find high-priority shipments:
        ```
        MATCH (s:Shipment {priority: 'high'})
        WHERE s.status = 'pending'
        RETURN s
        ```

        Find best truck-route combinations:
        ```
        MATCH (t:Truck)-[:ASSIGNED_TO]->(s:Shipment)-[:USES_ROUTE]->(r:Route)
        WITH t.type as truck_type, r.id as route, avg(s.utilization) as avg_util
        WHERE avg_util > 75
        RETURN truck_type, route, avg_util
        ORDER BY avg_util DESC
        ```

        Find freight hubs (busy locations):
        ```
        MATCH (l:Location)
        OPTIONAL MATCH (l)<-[:FROM]-(out:Shipment)
        OPTIONAL MATCH (l)<-[:TO]-(in:Shipment)
        WITH l, count(out) + count(in) as total
        WHERE total > 10
        RETURN l.name, total
        ORDER BY total DESC
        ```

        Args:
            cypher_query: Cypher query string
            parameters: Query parameters (use for safety)

        Returns:
            Query results as list of dictionaries
        """
        return await graph_tools.query_graph_with_cypher(
            cypher_query=cypher_query,
            parameters=parameters or {}
        )

    logger.info("✅ Registered 15 MCP tools (7 core + 8 graph)")


# Run MCP server (if called directly)
if __name__ == "__main__":
    if mcp:
        import uvicorn
        logger.info("Starting MCP server on http://localhost:8001")
        uvicorn.run(
            mcp.app,
            host="0.0.0.0",
            port=8001,
            log_level="info"
        )
    else:
        logger.error("Cannot start MCP server: fastmcp not installed")
