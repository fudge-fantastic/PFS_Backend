from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.config import settings
from typing import Optional
import asyncio

class Database:
    client: Optional[AsyncIOMotorClient] = None
    database = None

db = Database()

async def connect_to_mongo():
    """Create database connection"""
    db.client = AsyncIOMotorClient(settings.mongodb_url)
    db.database = db.client[settings.mongodb_database]

async def close_mongo_connection():
    """Close database connection"""
    if db.client:
        db.client.close()

async def init_db():
    """Initialize database with Beanie"""
    from app.models import User, Product, Category
    await init_beanie(database=db.database, document_models=[User, Product, Category])

def get_database():
    """Dependency to get database instance"""
    return db.database
