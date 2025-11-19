import aiosqlite
import json
from typing import Optional, List, Dict, Any
from datetime import datetime
from pathlib import Path
import logging

from config.settings import settings

logger = logging.getLogger(__name__)


class Database:
    """Async SQLite database manager for KITT"""

    def __init__(self, db_path: str = None):
        self.db_path = db_path or settings.DATABASE_URL.replace("sqlite:///", "")
        self.connection: Optional[aiosqlite.Connection] = None

    async def connect(self):
        """Connect to database"""
        self.connection = await aiosqlite.connect(self.db_path)
        self.connection.row_factory = aiosqlite.Row
        logger.info(f"Connected to database: {self.db_path}")

    async def disconnect(self):
        """Disconnect from database"""
        if self.connection:
            await self.connection.close()
            logger.info("Disconnected from database")

    async def initialize_schema(self):
        """Initialize database schema from schema.sql"""
        schema_path = Path(__file__).parent.parent / "schema.sql"

        if not schema_path.exists():
            raise FileNotFoundError(f"Schema file not found: {schema_path}")

        async with aiosqlite.connect(self.db_path) as db:
            with open(schema_path, 'r') as f:
                schema_sql = f.read()
            await db.executescript(schema_sql)
            await db.commit()

        logger.info("Database schema initialized")

    # Shipment operations
    async def create_shipment(
        self,
        shipment_id: str,
        origin: str,
        destination: str,
        priority: str = "medium",
        deadline: datetime = None
    ) -> str:
        """Create a new shipment"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO shipments (id, origin, destination, priority, deadline)
                VALUES (?, ?, ?, ?, ?)
            """, (shipment_id, origin, destination, priority, deadline))
            await db.commit()

        logger.info(f"Created shipment: {shipment_id}")
        return shipment_id

    async def get_shipment(self, shipment_id: str) -> Optional[Dict[str, Any]]:
        """Get shipment by ID"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM shipments WHERE id = ?",
                (shipment_id,)
            ) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None

    async def update_shipment_status(self, shipment_id: str, status: str) -> bool:
        """Update shipment status"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                UPDATE shipments
                SET status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (status, shipment_id))
            await db.commit()

        logger.info(f"Updated shipment {shipment_id} status to {status}")
        return True

    async def list_shipments(
        self,
        status: str = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """List shipments with optional status filter"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row

            if status:
                query = "SELECT * FROM shipments WHERE status = ? ORDER BY created_at DESC LIMIT ?"
                params = (status, limit)
            else:
                query = "SELECT * FROM shipments ORDER BY created_at DESC LIMIT ?"
                params = (limit,)

            async with db.execute(query, params) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    # Item operations
    async def add_item(
        self,
        item_id: str,
        shipment_id: str,
        width: float,
        height: float,
        depth: float,
        weight: float,
        fragile: bool = False,
        stackable: bool = True,
        description: str = None
    ) -> str:
        """Add item to shipment"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO items
                (id, shipment_id, width, height, depth, weight, fragile, stackable, description)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (item_id, shipment_id, width, height, depth, weight, fragile, stackable, description))
            await db.commit()

        logger.info(f"Added item {item_id} to shipment {shipment_id}")
        return item_id

    async def get_shipment_items(self, shipment_id: str) -> List[Dict[str, Any]]:
        """Get all items for a shipment"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM items WHERE shipment_id = ?",
                (shipment_id,)
            ) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    # Packing plan operations
    async def save_packing_plan(
        self,
        plan_id: str,
        shipment_id: str,
        truck_id: str,
        plan_data: dict,
        utilization: float,
        risk_score: float,
        algorithm_used: str = "deeppack3d",
        computation_time_ms: int = 0
    ) -> str:
        """Save packing plan"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO packing_plans
                (id, shipment_id, truck_id, plan_data, utilization, risk_score,
                 algorithm_used, computation_time_ms)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                plan_id, shipment_id, truck_id, json.dumps(plan_data),
                utilization, risk_score, algorithm_used, computation_time_ms
            ))
            await db.commit()

        logger.info(f"Saved packing plan {plan_id} for shipment {shipment_id}")
        return plan_id

    async def get_packing_plan(self, plan_id: str) -> Optional[Dict[str, Any]]:
        """Get packing plan by ID"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM packing_plans WHERE id = ?",
                (plan_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    result = dict(row)
                    result['plan_data'] = json.loads(result['plan_data'])
                    return result
                return None

    async def get_shipment_packing_plans(
        self,
        shipment_id: str
    ) -> List[Dict[str, Any]]:
        """Get all packing plans for a shipment"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM packing_plans WHERE shipment_id = ? ORDER BY created_at DESC",
                (shipment_id,)
            ) as cursor:
                rows = await cursor.fetchall()
                results = []
                for row in rows:
                    result = dict(row)
                    result['plan_data'] = json.loads(result['plan_data'])
                    results.append(result)
                return results

    # Truck operations
    async def get_available_trucks(self) -> List[Dict[str, Any]]:
        """Get all available trucks"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM trucks WHERE status = 'available'"
            ) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    async def get_truck(self, truck_id: str) -> Optional[Dict[str, Any]]:
        """Get truck by ID"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM trucks WHERE id = ?",
                (truck_id,)
            ) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None

    async def update_truck_status(self, truck_id: str, status: str) -> bool:
        """Update truck status"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                UPDATE trucks
                SET status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (status, truck_id))
            await db.commit()

        logger.info(f"Updated truck {truck_id} status to {status}")
        return True

    # Route analytics operations
    async def save_route_analytics(
        self,
        route_id: str,
        origin: str,
        destination: str,
        distance_km: float = None,
        duration_minutes: int = None,
        weather_condition: str = None,
        weather_severity: int = None,
        traffic_level: str = None,
        road_quality_score: float = None,
        estimated_damage_risk: float = None
    ) -> str:
        """Save route analytics data"""
        import uuid
        analytics_id = str(uuid.uuid4())

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO route_analytics
                (id, route_id, origin, destination, distance_km, duration_minutes,
                 weather_condition, weather_severity, traffic_level,
                 road_quality_score, estimated_damage_risk)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                analytics_id, route_id, origin, destination, distance_km,
                duration_minutes, weather_condition, weather_severity,
                traffic_level, road_quality_score, estimated_damage_risk
            ))
            await db.commit()

        logger.info(f"Saved route analytics for {route_id}")
        return analytics_id

    async def get_route_analytics(
        self,
        route_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get recent route analytics"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT * FROM route_analytics
                WHERE route_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (route_id, limit)) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    # AI prediction operations
    async def save_ai_prediction(
        self,
        shipment_id: str,
        prediction_type: str,
        prediction_data: dict,
        model_version: str = None,
        confidence: float = None
    ) -> str:
        """Save AI prediction"""
        import uuid
        prediction_id = str(uuid.uuid4())

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO ai_predictions
                (id, shipment_id, prediction_type, model_version, prediction_data, confidence)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                prediction_id, shipment_id, prediction_type,
                model_version, json.dumps(prediction_data), confidence
            ))
            await db.commit()

        logger.info(f"Saved AI prediction {prediction_id} for shipment {shipment_id}")
        return prediction_id

    async def get_shipment_predictions(
        self,
        shipment_id: str
    ) -> List[Dict[str, Any]]:
        """Get all AI predictions for a shipment"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT * FROM ai_predictions
                WHERE shipment_id = ?
                ORDER BY created_at DESC
            """, (shipment_id,)) as cursor:
                rows = await cursor.fetchall()
                results = []
                for row in rows:
                    result = dict(row)
                    result['prediction_data'] = json.loads(result['prediction_data'])
                    results.append(result)
                return results

    # Damage incident operations
    async def record_damage_incident(
        self,
        shipment_id: str,
        incident_type: str,
        severity: int,
        description: str = None,
        route_id: str = None,
        contributing_factors: dict = None
    ) -> str:
        """Record damage incident"""
        import uuid
        incident_id = str(uuid.uuid4())

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO damage_incidents
                (id, shipment_id, route_id, incident_type, severity,
                 description, contributing_factors)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                incident_id, shipment_id, route_id, incident_type,
                severity, description, json.dumps(contributing_factors) if contributing_factors else None
            ))
            await db.commit()

        logger.info(f"Recorded damage incident {incident_id} for shipment {shipment_id}")
        return incident_id

    async def get_all_shipments(self, limit: int = 100, status: str = None, priority: str = None) -> List[Dict[str, Any]]:
        """Get all shipments with optional filters"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row

            query = "SELECT * FROM shipments"
            params = []
            conditions = []

            if status:
                conditions.append("status = ?")
                params.append(status)

            if priority:
                conditions.append("priority = ?")
                params.append(priority)

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)

            async with db.execute(query, params) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    async def get_all_packing_plans(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all packing plans"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row

            async with db.execute("""
                SELECT * FROM packing_plans
                ORDER BY created_at DESC
                LIMIT ?
            """, (limit,)) as cursor:
                rows = await cursor.fetchall()
                results = []
                for row in rows:
                    result = dict(row)
                    if result.get('packing_result'):
                        result['packing_result'] = json.loads(result['packing_result'])
                    results.append(result)
                return results


# Global database instance
db = Database()
