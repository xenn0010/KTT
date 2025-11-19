#!/usr/bin/env python3
"""
Initialize KITT database with schema and sample data
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from kitt_mcp.database import db
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Initialize database"""
    logger.info("🗄️  Initializing KITT database...")

    try:
        # Initialize schema
        await db.initialize_schema()
        logger.info("✅ Database schema created successfully")

        # Verify tables exist
        import aiosqlite
        async with aiosqlite.connect(db.db_path) as conn:
            async with conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ) as cursor:
                tables = await cursor.fetchall()
                table_names = [t[0] for t in tables]

                logger.info(f"📋 Created tables: {', '.join(table_names)}")

        # Verify sample trucks
        trucks = await db.get_available_trucks()
        logger.info(f"🚛 Sample trucks available: {len(trucks)}")
        for truck in trucks:
            logger.info(
                f"   - {truck['id']}: {truck['name']} "
                f"({truck['width']}x{truck['height']}x{truck['depth']}, "
                f"max {truck['max_weight']}kg)"
            )

        logger.info("✅ Database initialized successfully!")
        logger.info(f"📁 Database file: {db.db_path}")

    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
