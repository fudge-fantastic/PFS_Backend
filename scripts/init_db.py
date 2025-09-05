#!/usr/bin/env python3
"""
Database initialization script for PixelForge Backend
Creates admin user and sample data
"""

import asyncio
import sys
import os

# Add the parent directory to the path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models import Base, User
from app.services.auth import get_password_hash
from app.crud.user import user_crud
from app.schemas import UserCreate

def create_tables():
    """Create database tables."""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created successfully")

def create_admin_user():
    """Create default admin user."""
    db = SessionLocal()
    try:
        # Check if admin already exists
        admin_email = "admin@pfs.in"
        existing_admin = user_crud.get_user_by_email(db, admin_email)
        
        if existing_admin:
            print(f"✓ Admin user already exists: {admin_email}")
            return existing_admin
        
        # Create admin user
        admin_data = UserCreate(
            email=admin_email,
            password="admin1234"  # Change this in production
        )
        
        admin_user = user_crud.create_user(db, admin_data)
        
        # Manually set admin role
        admin_user.role = "ADMIN"  # Use uppercase to match database
        db.commit()
        db.refresh(admin_user)
        
        print(f"✓ Admin user created successfully: {admin_email}")
        print(f"  Default password: admin (CHANGE THIS IN PRODUCTION)")
        return admin_user
        
    except Exception as e:
        print(f"✗ Failed to create admin user: {str(e)}")
        db.rollback()
        return None
    finally:
        db.close()

# def create_sample_users():
#     """Create sample regular users."""
#     db = SessionLocal()
#     try:
#         sample_users = [
#             {"email": "user1@pixelforgestudio.in", "password": "user123456"},
#             {"email": "user2@pixelforgestudio.in", "password": "user123456"},
#         ]
        
#         created_users = []
#         for user_data in sample_users:
#             existing_user = user_crud.get_user_by_email(db, user_data["email"])
#             if existing_user:
#                 print(f"✓ Sample user already exists: {user_data['email']}")
#                 created_users.append(existing_user)
#                 continue
            
#             user = user_crud.create_user(db, UserCreate(**user_data))
#             created_users.append(user)
#             print(f"✓ Sample user created: {user_data['email']}")
        
#         return created_users
        
#     except Exception as e:
#         print(f"✗ Failed to create sample users: {str(e)}")
#         db.rollback()
#         return []
#     finally:
#         db.close()

def main():
    """Main initialization function."""
    print("🚀 Initializing PixelForge Backend Database...")
    print("=" * 50)
    
    # Create tables
    create_tables()
    
    # Create admin user
    admin = create_admin_user()
    
    print("=" * 50)
    print("📋 Database Initialization Summary:")
    print(f"   • Tables: Created/Verified")
    print(f"   • Admin users: {1 if admin else 0}")
    print()
    print("🔐 Default Credentials:")
    print("   Admin: admin@pfs.in / admin1234")
    print()
    print("⚠️  IMPORTANT: Change default passwords in production!")
    print("✅ Database initialization completed successfully!")

if __name__ == "__main__":
    main()
