"""
Graph Database MCP Tools
Provides Claude with agentic access to the Neo4j knowledge graph
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from services.neo4j_service import get_neo4j_service

logger = logging.getLogger(__name__)


class GraphTools:
    """MCP tools for Neo4j graph database operations"""

    def __init__(self):
        self.neo4j = None

    async def _ensure_connection(self):
        """Ensure Neo4j connection is established"""
        if not self.neo4j:
            self.neo4j = await get_neo4j_service()
        return self.neo4j

    # ==================== GRAPH CREATION TOOLS ====================

    async def store_shipment_in_graph(
        self,
        shipment_id: str,
        origin: str,
        destination: str,
        items: List[Dict],
        status: str = "pending",
        priority: str = "medium",
        deadline: Optional[str] = None
    ) -> Dict:
        """
        Store shipment and its relationships in the knowledge graph

        Creates:
        - Shipment node
        - Item nodes
        - Location nodes (origin, destination)
        - Relationships: CONTAINS, FROM, TO

        Args:
            shipment_id: Unique shipment identifier
            origin: Origin location name
            destination: Destination location name
            items: List of items with dimensions and properties
            status: Shipment status (pending/in_transit/delivered)
            priority: Priority level (low/medium/high/critical)
            deadline: Optional ISO datetime string

        Returns:
            Created graph structure with node IDs
        """
        service = await self._ensure_connection()

        # Calculate totals
        total_weight = sum(item.get('weight', 0) for item in items)
        total_volume = sum(
            item.get('width', 0) * item.get('height', 0) * item.get('depth', 0)
            for item in items
        )

        # Create shipment node
        shipment_data = {
            "id": shipment_id,
            "status": status,
            "priority": priority,
            "created_at": deadline or datetime.now().isoformat(),
            "deadline": deadline or datetime.now().isoformat(),
            "total_weight": total_weight,
            "total_volume": total_volume,
            "item_count": len(items)
        }

        shipment_node = await service.create_shipment_node(shipment_data)

        # Link to locations
        await service.link_shipment_to_locations(shipment_id, origin, destination)

        # Add items
        items_added = await service.add_items_to_shipment(shipment_id, items)

        return {
            "success": True,
            "shipment_node": shipment_node,
            "items_added": items_added,
            "origin": origin,
            "destination": destination,
            "total_weight": total_weight,
            "total_volume": total_volume
        }

    async def store_route_in_graph(
        self,
        route_id: str,
        origin: str,
        destination: str,
        distance_km: float,
        duration_hours: float,
        road_quality: str = "good"
    ) -> Dict:
        """
        Store route information in the knowledge graph

        Creates:
        - Route node with distance, duration, quality
        - Links to origin and destination locations

        Args:
            route_id: Unique route identifier
            origin: Starting location
            destination: Ending location
            distance_km: Distance in kilometers
            duration_hours: Estimated duration in hours
            road_quality: Road condition (excellent/good/fair/poor)

        Returns:
            Created route node
        """
        service = await self._ensure_connection()

        route_node = await service.create_route(
            route_id=route_id,
            origin=origin,
            destination=destination,
            distance_km=distance_km,
            duration_hours=duration_hours,
            road_quality=road_quality
        )

        return {
            "success": True,
            "route": route_node,
            "origin": origin,
            "destination": destination,
            "distance_km": distance_km
        }

    async def store_truck_in_graph(
        self,
        truck_id: str,
        license_plate: str,
        truck_type: str,
        max_weight: float,
        container_width: float,
        container_height: float,
        container_depth: float,
        status: str = "available"
    ) -> Dict:
        """
        Store truck information in the knowledge graph

        Args:
            truck_id: Unique truck identifier
            license_plate: Truck license plate
            truck_type: Type (flatbed/box_truck/semi_trailer/etc)
            max_weight: Maximum weight capacity in kg
            container_width: Container width in cm
            container_height: Container height in cm
            container_depth: Container depth in cm
            status: Truck status (available/in_use/maintenance)

        Returns:
            Created truck node
        """
        service = await self._ensure_connection()

        truck_data = {
            "id": truck_id,
            "license_plate": license_plate,
            "type": truck_type,
            "max_weight": max_weight,
            "container_width": container_width,
            "container_height": container_height,
            "container_depth": container_depth,
            "status": status
        }

        truck_node = await service.create_truck_node(truck_data)

        return {
            "success": True,
            "truck": truck_node,
            "capacity_volume": container_width * container_height * container_depth
        }

    async def assign_truck_to_shipment_in_graph(
        self,
        shipment_id: str,
        truck_id: str,
        utilization: float
    ) -> Dict:
        """
        Create relationship between truck and shipment

        Args:
            shipment_id: Shipment identifier
            truck_id: Truck identifier
            utilization: Space utilization percentage (0-100)

        Returns:
            Assignment confirmation
        """
        service = await self._ensure_connection()

        success = await service.assign_truck_to_shipment(
            shipment_id=shipment_id,
            truck_id=truck_id,
            utilization=utilization
        )

        return {
            "success": success,
            "shipment_id": shipment_id,
            "truck_id": truck_id,
            "utilization": utilization
        }

    # ==================== GRAPH QUERY TOOLS ====================

    async def get_shipment_knowledge_graph(self, shipment_id: str) -> Dict:
        """
        Get complete knowledge graph for a shipment

        Returns shipment with ALL relationships:
        - Origin and destination locations
        - All items contained
        - Assigned truck (if any)
        - Route being used (if any)
        - Similar historical shipments

        Args:
            shipment_id: Shipment to query

        Returns:
            Complete graph view of shipment and relationships
        """
        service = await self._ensure_connection()

        graph = await service.get_shipment_graph(shipment_id)

        # Also get similar shipments for context
        if graph.get('origin') and graph.get('destination'):
            similar = await service.find_similar_shipments(
                origin=graph['origin'].get('name'),
                destination=graph['destination'].get('name')
            )
            graph['similar_shipments'] = similar

        return graph

    async def find_optimal_trucks(
        self,
        total_weight: float,
        total_volume: float,
        origin: str
    ) -> List[Dict]:
        """
        Find best available trucks for given shipment requirements

        Uses graph queries to find trucks that:
        - Have sufficient weight capacity
        - Have sufficient volume capacity
        - Are currently available
        - Are near the origin location (if location data exists)

        Args:
            total_weight: Required weight capacity in kg
            total_volume: Required volume capacity in cubic cm
            origin: Origin location for proximity search

        Returns:
            List of suitable trucks ranked by availability
        """
        service = await self._ensure_connection()

        trucks = await service.find_optimal_truck_for_shipment(
            total_weight=total_weight,
            total_volume=total_volume,
            origin=origin
        )

        return trucks

    async def get_location_analytics(self, location_name: str) -> Dict:
        """
        Get comprehensive analytics for a location

        Analyzes:
        - Number of shipments originated
        - Number of shipments received
        - Routes starting/ending here
        - Total freight activity
        - Patterns and trends

        Args:
            location_name: Location to analyze

        Returns:
            Analytics and insights about location
        """
        service = await self._ensure_connection()

        insights = await service.get_location_insights(location_name)

        return insights

    async def find_historical_patterns(
        self,
        origin: str,
        destination: str
    ) -> List[Dict]:
        """
        Find historical shipment patterns for a route

        Useful for:
        - Learning from past successes/failures
        - Predicting optimal truck types
        - Estimating realistic timelines
        - Identifying seasonal patterns

        Args:
            origin: Origin location
            destination: Destination location

        Returns:
            Historical shipments with outcomes
        """
        service = await self._ensure_connection()

        similar_shipments = await service.find_similar_shipments(
            origin=origin,
            destination=destination
        )

        return similar_shipments

    async def get_network_overview(self) -> Dict:
        """
        Get high-level overview of entire freight network

        Returns:
        - Total shipments in system
        - Total trucks
        - Total locations
        - Total routes
        - Network health metrics

        Returns:
            Network-wide statistics
        """
        service = await self._ensure_connection()

        stats = await service.get_network_stats()

        return stats

    # ==================== AGENTIC CYPHER QUERY TOOL ====================

    async def query_graph_with_cypher(
        self,
        cypher_query: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> List[Dict]:
        """
        **POWERFUL AGENTIC TOOL**: Execute custom Cypher queries on the graph

        This allows Claude to:
        - Write and execute arbitrary graph queries
        - Explore complex relationships
        - Discover patterns not covered by predefined tools
        - Answer questions requiring graph traversal
        - Perform advanced analytics

        Examples:
        - "Find all shipments from LA to NYC in the last month"
        - "What trucks have > 80% average utilization?"
        - "Show the busiest routes by shipment count"
        - "Find items that are frequently damaged"

        Args:
            cypher_query: Cypher query string (Neo4j graph query language)
            parameters: Optional query parameters for safety (prevent injection)

        Returns:
            Query results as list of dictionaries

        Example Cypher queries:
        ```
        // Find all high-priority shipments
        MATCH (s:Shipment {priority: 'high'})
        RETURN s

        // Find shortest routes between locations
        MATCH p=shortestPath((a:Location)-[:STARTS_AT|ENDS_AT*]-(b:Location))
        WHERE a.name = 'Los Angeles' AND b.name = 'New York'
        RETURN p, length(p) as hops

        // Find trucks with best utilization
        MATCH (t:Truck)-[a:ASSIGNED_TO]->(s:Shipment)
        WITH t, avg(a.utilization) as avg_util
        WHERE avg_util > 70
        RETURN t.id, t.type, avg_util
        ORDER BY avg_util DESC
        ```

        SAFETY NOTE: Always use parameterized queries when user input is involved
        """
        service = await self._ensure_connection()

        try:
            results = await service.query_graph_with_cypher(
                cypher_query=cypher_query,
                params=parameters or {}
            )

            return results

        except Exception as e:
            logger.error(f"Cypher query failed: {e}")
            return {
                "error": str(e),
                "query": cypher_query,
                "suggestion": "Check Cypher syntax or use predefined graph tools"
            }


# Global instance
graph_tools = GraphTools()
