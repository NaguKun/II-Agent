from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
from config import settings

class MongoDB:
    """MongoDB connection manager"""

    client: Optional[AsyncIOMotorClient] = None
    database = None

    @classmethod
    async def connect(cls):
        """Connect to MongoDB"""
        cls.client = AsyncIOMotorClient(settings.mongodb_url)
        cls.database = cls.client[settings.database_name]
        print(f"Connected to MongoDB: {settings.database_name}")

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
