"""
Neo4j Graph Database Service
Manages freight logistics knowledge graph with shipments, routes, trucks, and relationships
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from neo4j import GraphDatabase, AsyncGraphDatabase
from config.settings import settings

logger = logging.getLogger(__name__)


class Neo4jService:
    """Service for Neo4j graph database operations"""

    def __init__(self):
        self.driver = None
        self.uri = settings.NEO4J_URI
        self.username = settings.NEO4J_USERNAME
        self.password = settings.NEO4J_PASSWORD
        self.database = settings.NEO4J_DATABASE

    async def connect(self):
        """Initialize Neo4j connection"""
        try:
            self.driver = AsyncGraphDatabase.driver(
                self.uri,
                auth=(self.username, self.password),
                database=self.database
            )
            # Verify connection
            await self.driver.verify_connectivity()
            logger.info("✅ Connected to Neo4j at %s", self.uri)
            return True
        except Exception as e:
            logger.error(f"❌ Failed to connect to Neo4j: {e}")
            return False

    async def close(self):
        """Close Neo4j connection"""
        if self.driver:
            await self.driver.close()
            logger.info("Neo4j connection closed")

    async def initialize_schema(self):
        """Create indexes and constraints for optimal performance"""
        queries = [
            # Unique constraints
            "CREATE CONSTRAINT shipment_id IF NOT EXISTS FOR (s:Shipment) REQUIRE s.id IS UNIQUE",
            "CREATE CONSTRAINT truck_id IF NOT EXISTS FOR (t:Truck) REQUIRE t.id IS UNIQUE",
            "CREATE CONSTRAINT route_id IF NOT EXISTS FOR (r:Route) REQUIRE r.id IS UNIQUE",
            "CREATE CONSTRAINT location_name IF NOT EXISTS FOR (l:Location) REQUIRE l.name IS UNIQUE",
            "CREATE CONSTRAINT item_id IF NOT EXISTS FOR (i:Item) REQUIRE i.id IS UNIQUE",

            # Indexes for performance
            "CREATE INDEX shipment_status IF NOT EXISTS FOR (s:Shipment) ON (s.status)",
            "CREATE INDEX shipment_priority IF NOT EXISTS FOR (s:Shipment) ON (s.priority)",
            "CREATE INDEX shipment_created IF NOT EXISTS FOR (s:Shipment) ON (s.created_at)",
            "CREATE INDEX route_distance IF NOT EXISTS FOR (r:Route) ON (r.distance_km)",
            "CREATE INDEX truck_capacity IF NOT EXISTS FOR (t:Truck) ON (t.max_weight)",
        ]

        async with self.driver.session() as session:
            for query in queries:
                try:
                    await session.run(query)
                    logger.info(f"✅ Schema: {query.split()[1]}")
                except Exception as e:
                    logger.warning(f"Schema creation (may already exist): {e}")

        logger.info("✅ Neo4j schema initialized")

    # ==================== SHIPMENT OPERATIONS ====================

    async def create_shipment_node(self, shipment_data: Dict[str, Any]) -> Dict:
        """Create a shipment node in the graph"""
        query = """
        CREATE (s:Shipment {
            id: $id,
            status: $status,
            priority: $priority,
            created_at: datetime($created_at),
            deadline: datetime($deadline),
            total_weight: $total_weight,
            total_volume: $total_volume,
            item_count: $item_count
        })
        RETURN s
        """

        async with self.driver.session() as session:
            result = await session.run(query, **shipment_data)
            record = await result.single()
            return dict(record["s"]) if record else {}

    async def link_shipment_to_locations(
        self,
        shipment_id: str,
        origin: str,
        destination: str
    ) -> bool:
        """Create or link shipment to origin and destination locations"""
        query = """
        MATCH (s:Shipment {id: $shipment_id})

        MERGE (origin:Location {name: $origin})
        ON CREATE SET origin.created_at = datetime()

        MERGE (dest:Location {name: $destination})
        ON CREATE SET dest.created_at = datetime()

        MERGE (s)-[:FROM]->(origin)
        MERGE (s)-[:TO]->(dest)

        RETURN s, origin, dest
        """

        async with self.driver.session() as session:
            result = await session.run(
                query,
                shipment_id=shipment_id,
                origin=origin,
                destination=destination
            )
            return await result.single() is not None

    async def add_items_to_shipment(
        self,
        shipment_id: str,
        items: List[Dict[str, Any]]
    ) -> int:
        """Add item nodes and link them to shipment"""
        query = """
        MATCH (s:Shipment {id: $shipment_id})
        UNWIND $items AS item
        CREATE (i:Item {
            id: item.id,
            width: item.width,
            height: item.height,
            depth: item.depth,
            weight: item.weight,
            fragile: item.fragile,
            stackable: item.stackable,
            description: item.description,
            volume: item.width * item.height * item.depth
        })
        MERGE (s)-[:CONTAINS]->(i)
        RETURN count(i) as items_added
        """

        async with self.driver.session() as session:
            result = await session.run(
                query,
                shipment_id=shipment_id,
                items=items
            )
            record = await result.single()
            return record["items_added"] if record else 0

    # ==================== ROUTE OPERATIONS ====================

    async def create_route(
        self,
        route_id: str,
        origin: str,
        destination: str,
        distance_km: float,
        duration_hours: float,
        road_quality: str = "good"
    ) -> Dict:
        """Create a route node and link to locations"""
        query = """
        MERGE (origin:Location {name: $origin})
        MERGE (dest:Location {name: $destination})

        CREATE (r:Route {
            id: $route_id,
            distance_km: $distance_km,
            duration_hours: $duration_hours,
            road_quality: $road_quality,
            created_at: datetime()
        })

        MERGE (r)-[:STARTS_AT]->(origin)
        MERGE (r)-[:ENDS_AT]->(dest)

        RETURN r
        """

        async with self.driver.session() as session:
            result = await session.run(
                query,
                route_id=route_id,
                origin=origin,
                destination=destination,
                distance_km=distance_km,
                duration_hours=duration_hours,
                road_quality=road_quality
            )
            record = await result.single()
            return dict(record["r"]) if record else {}

    async def assign_shipment_to_route(
        self,
        shipment_id: str,
        route_id: str
    ) -> bool:
        """Link shipment to a route"""
        query = """
        MATCH (s:Shipment {id: $shipment_id})
        MATCH (r:Route {id: $route_id})
        MERGE (s)-[:USES_ROUTE]->(r)
        RETURN s, r
        """

        async with self.driver.session() as session:
            result = await session.run(
                query,
                shipment_id=shipment_id,
                route_id=route_id
            )
            return await result.single() is not None

    # ==================== TRUCK OPERATIONS ====================

    async def create_truck_node(self, truck_data: Dict[str, Any]) -> Dict:
        """Create a truck node"""
        query = """
        CREATE (t:Truck {
            id: $id,
            license_plate: $license_plate,
            type: $type,
            max_weight: $max_weight,
            container_width: $container_width,
            container_height: $container_height,
            container_depth: $container_depth,
            capacity_volume: $container_width * $container_height * $container_depth,
            status: $status,
            created_at: datetime()
        })
        RETURN t
        """

        async with self.driver.session() as session:
            result = await session.run(query, **truck_data)
            record = await result.single()
            return dict(record["t"]) if record else {}

    async def assign_truck_to_shipment(
        self,
        shipment_id: str,
        truck_id: str,
        utilization: float
    ) -> bool:
        """Assign a truck to a shipment with utilization"""
        query = """
        MATCH (s:Shipment {id: $shipment_id})
        MATCH (t:Truck {id: $truck_id})
        MERGE (t)-[a:ASSIGNED_TO {
            utilization: $utilization,
            assigned_at: datetime()
        }]->(s)
        RETURN a
        """

        async with self.driver.session() as session:
            result = await session.run(
                query,
                shipment_id=shipment_id,
                truck_id=truck_id,
                utilization=utilization
            )
            return await result.single() is not None

    # ==================== QUERY OPERATIONS ====================

    async def find_optimal_truck_for_shipment(
        self,
        total_weight: float,
        total_volume: float,
        origin: str
    ) -> List[Dict]:
        """Find best trucks for shipment based on capacity and location"""
        query = """
        MATCH (t:Truck)
        WHERE t.max_weight >= $total_weight
          AND t.capacity_volume >= $total_volume
          AND t.status = 'available'

        OPTIONAL MATCH (t)-[:LOCATED_AT]->(loc:Location)

        RETURN t.id as truck_id,
               t.type as truck_type,
               t.max_weight as max_weight,
               t.capacity_volume as capacity_volume,
               loc.name as current_location,
               (t.capacity_volume - $total_volume) as spare_volume,
               (t.max_weight - $total_weight) as spare_weight

        ORDER BY spare_volume ASC, spare_weight ASC
        LIMIT 5
        """

        async with self.driver.session() as session:
            result = await session.run(
                query,
                total_weight=total_weight,
                total_volume=total_volume
            )
            return [dict(record) async for record in result]

    async def get_shipment_graph(self, shipment_id: str) -> Dict:
        """Get complete shipment graph with all relationships"""
        query = """
        MATCH (s:Shipment {id: $shipment_id})

        OPTIONAL MATCH (s)-[:FROM]->(origin:Location)
        OPTIONAL MATCH (s)-[:TO]->(dest:Location)
        OPTIONAL MATCH (s)-[:CONTAINS]->(items:Item)
        OPTIONAL MATCH (truck:Truck)-[:ASSIGNED_TO]->(s)
        OPTIONAL MATCH (s)-[:USES_ROUTE]->(route:Route)

        RETURN s as shipment,
               origin,
               dest as destination,
               collect(DISTINCT items) as items,
               truck,
               route
        """

        async with self.driver.session() as session:
            result = await session.run(query, shipment_id=shipment_id)
            record = await result.single()

            if not record:
                return {}

            return {
                "shipment": dict(record["shipment"]) if record["shipment"] else {},
                "origin": dict(record["origin"]) if record["origin"] else {},
                "destination": dict(record["destination"]) if record["destination"] else {},
                "items": [dict(item) for item in record["items"]],
                "truck": dict(record["truck"]) if record["truck"] else {},
                "route": dict(record["route"]) if record["route"] else {}
            }

    async def get_location_insights(self, location_name: str) -> Dict:
        """Get insights about a location's freight activity"""
        query = """
        MATCH (l:Location {name: $location_name})

        OPTIONAL MATCH (shipments_from:Shipment)-[:FROM]->(l)
        OPTIONAL MATCH (shipments_to:Shipment)-[:TO]->(l)
        OPTIONAL MATCH (routes_from:Route)-[:STARTS_AT]->(l)
        OPTIONAL MATCH (routes_to:Route)-[:ENDS_AT]->(l)

        RETURN l.name as location,
               count(DISTINCT shipments_from) as shipments_originated,
               count(DISTINCT shipments_to) as shipments_received,
               count(DISTINCT routes_from) as routes_starting,
               count(DISTINCT routes_to) as routes_ending,
               (count(DISTINCT shipments_from) + count(DISTINCT shipments_to)) as total_shipments
        """

        async with self.driver.session() as session:
            result = await session.run(query, location_name=location_name)
            record = await result.single()
            return dict(record) if record else {}

    async def find_similar_shipments(
        self,
        origin: str,
        destination: str,
        weight_range: float = 0.2
    ) -> List[Dict]:
        """Find similar historical shipments for learning patterns"""
        query = """
        MATCH (s:Shipment)-[:FROM]->(o:Location {name: $origin})
        MATCH (s)-[:TO]->(d:Location {name: $destination})

        OPTIONAL MATCH (t:Truck)-[:ASSIGNED_TO]->(s)
        OPTIONAL MATCH (s)-[:USES_ROUTE]->(r:Route)

        RETURN s.id as shipment_id,
               s.status as status,
               s.total_weight as weight,
               s.total_volume as volume,
               t.id as truck_id,
               r.distance_km as route_distance,
               s.created_at as created_at

        ORDER BY s.created_at DESC
        LIMIT 10
        """

        async with self.driver.session() as session:
            result = await session.run(
                query,
                origin=origin,
                destination=destination
            )
            return [dict(record) async for record in result]

    async def get_network_stats(self) -> Dict:
        """Get overall network statistics"""
        query = """
        MATCH (s:Shipment) WITH count(s) as total_shipments
        MATCH (t:Truck) WITH total_shipments, count(t) as total_trucks
        MATCH (l:Location) WITH total_shipments, total_trucks, count(l) as total_locations
        MATCH (r:Route) WITH total_shipments, total_trucks, total_locations, count(r) as total_routes
        MATCH (i:Item) WITH total_shipments, total_trucks, total_locations, total_routes, count(i) as total_items

        RETURN total_shipments,
               total_trucks,
               total_locations,
               total_routes,
               total_items
        """

        async with self.driver.session() as session:
            result = await session.run(query)
            record = await result.single()
            return dict(record) if record else {}

    # ==================== AGENTIC QUERY OPERATIONS ====================

    async def query_graph_with_cypher(self, cypher_query: str, params: Dict = None) -> List[Dict]:
        """
        Execute arbitrary Cypher query (for Claude to use)

        IMPORTANT: This allows Claude to write and execute Cypher queries
        to explore the knowledge graph dynamically
        """
        async with self.driver.session() as session:
            result = await session.run(cypher_query, params or {})
            return [dict(record) async for record in result]


# Global instance
neo4j_service = Neo4jService()


# Helper functions for easy import
async def get_neo4j_service() -> Neo4jService:
    """Get initialized Neo4j service"""
    if not neo4j_service.driver:
        await neo4j_service.connect()
        await neo4j_service.initialize_schema()
    return neo4j_service
