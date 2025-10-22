from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
from config import settings
import logging

logger = logging.getLogger(__name__)

class MongoDB:
    """MongoDB connection manager with connection pooling and indexing"""

    client: Optional[AsyncIOMotorClient] = None
    database = None

    @classmethod
    async def connect(cls):
        """Connect to MongoDB with connection pooling configuration"""
        # Configure connection pool for better performance
        cls.client = AsyncIOMotorClient(
            settings.mongodb_url,
            maxPoolSize=50,  # Maximum connections in pool
            minPoolSize=10,  # Minimum connections to maintain
            maxIdleTimeMS=45000,  # Close idle connections after 45s
            serverSelectionTimeoutMS=5000,  # Timeout for server selection
            connectTimeoutMS=10000,  # Connection timeout
            socketTimeoutMS=20000,  # Socket timeout
        )
        cls.database = cls.client[settings.database_name]
        logger.info(f"Connected to MongoDB: {settings.database_name}")

        # Create indexes for better query performance
        await cls._create_indexes()

    @classmethod
    async def _create_indexes(cls):
        """Create database indexes for optimized queries"""
        try:
            # Conversations collection indexes
            conversations = cls.database["conversations"]
            await conversations.create_index("created_at")
            await conversations.create_index("updated_at")

            # Messages collection indexes
            messages = cls.database["messages"]
            await messages.create_index("conversation_id")
            await messages.create_index([("conversation_id", 1), ("timestamp", 1)])
            await messages.create_index("timestamp")

            logger.info("Database indexes created successfully")
        except Exception as e:
            logger.error(f"Error creating indexes: {e}")

    @classmethod
    async def close(cls):
        """Close MongoDB connection"""
        if cls.client:
            cls.client.close()
            print("MongoDB connection closed")

    @classmethod
    def get_collection(cls, collection_name: str):
        """Get a collection from the database"""
        if cls.database is None:
            raise Exception("Database not connected")
        return cls.database[collection_name]


# Convenience function to get database instance
def get_db():
    return MongoDB.database
