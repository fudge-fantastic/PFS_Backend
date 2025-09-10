#!/usr/bin/env python3
"""
MongoDB database initialization script for PixelForge Backend
Creates admin user and initializes MongoDB collections
"""

import asyncio
import sys
import os

# Add the parent directory to the path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import connect_to_mongo, close_mongo_connection, init_db
from app.models import User
from app.crud.user import user_crud
from app.schemas import UserCreate

async def init_mongodb():
    """Initialize MongoDB connection and Beanie."""
    print("Connecting to MongoDB...")
    await connect_to_mongo()
    await init_db()
    print("✓ MongoDB connection and Beanie initialized successfully")

async def create_admin_user():
    """Create default admin user."""
    try:
        # Check if admin already exists
        admin_email = "admin@pfs.in"
        existing_admin = await user_crud.get_user_by_email(admin_email)
        
        if existing_admin:
            print(f"✓ Admin user already exists: {admin_email}")
            return existing_admin
        
        # Create admin user
        admin_data = UserCreate(
            email=admin_email,
            password="admin1234"  # Change this in production
        )
        
        admin_user = await user_crud.create_user(admin_data)
        
        # Update role to ADMIN
        admin_user.role = "ADMIN"
        await admin_user.save()
        
        print(f"✓ Admin user created successfully: {admin_email}")
        print(f"  Default password: admin1234 (CHANGE THIS IN PRODUCTION)")
        return admin_user
        
    except Exception as e:
        print(f"✗ Failed to create admin user: {str(e)}")
        return None

async def create_sample_categories():
    """Create sample categories for products."""
    from app.crud.category import category_crud
    from app.schemas import CategoryCreate
    
    try:
        categories = [
            {"name": "Photo Magnets", "description": "Custom photo magnets for personal use"},
            {"name": "Fridge Magnets", "description": "Decorative fridge magnets"},
            {"name": "Retro Prints", "description": "Vintage style prints and posters"}
        ]
        
        created_categories = []
        for cat_data in categories:
            existing_category = await category_crud.get_category_by_name(cat_data["name"])
            if existing_category:
                print(f"✓ Category already exists: {cat_data['name']}")
                created_categories.append(existing_category)
                continue
            
            category = await category_crud.create_category(CategoryCreate(**cat_data))
            created_categories.append(category)
            print(f"✓ Category created: {cat_data['name']}")
        
        return created_categories
        
    except Exception as e:
        print(f"✗ Failed to create sample categories: {str(e)}")
        return []

async def main():
    """Main initialization function."""
    print("🚀 Initializing PixelForge Backend MongoDB Database...")
    print("=" * 50)
    
    try:
        # Initialize MongoDB
        await init_mongodb()
        
        # Create admin user
        admin = await create_admin_user()
        
        # Create sample categories
        categories = await create_sample_categories()
        
        print("=" * 50)
        print("📋 Database Initialization Summary:")
        print(f"   • MongoDB: Connected and initialized")
        print(f"   • Admin users: {1 if admin else 0}")
        print(f"   • Categories: {len(categories)}")
        print()
        print("🔐 Default Credentials:")
        print("   Admin: admin@pfs.in / admin1234")
        print()
        print("⚠️  IMPORTANT: Change default passwords in production!")
        print("✅ MongoDB initialization completed successfully!")
        
    except Exception as e:
        print(f"✗ Failed to initialize database: {str(e)}")
    finally:
        await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(main())
