#!/usr/bin/env python3
"""
Dummy data seeding script for PixelForge Backend
Inserts realistic sample data for testing and development
"""

import sys
import os
import random
from datetime import datetime, timedelta

# Add the parent directory to the path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.crud.user import user_crud
from app.crud.product import product_crud
from app.schemas import UserCreate, ProductCreate
from app.models import ProductCategory

def create_dummy_users():
    """Create 10 dummy users with varied profiles."""
    db = SessionLocal()
    try:
        dummy_users = [
            {"email": "alice.johnson@example.com", "password": "password123", "role": "USER"},
            {"email": "bob.smith@example.com", "password": "password123", "role": "USER"},
            {"email": "carol.davis@example.com", "password": "password123", "role": "USER"},
            {"email": "david.wilson@example.com", "password": "password123", "role": "USER"},
            {"email": "emma.brown@example.com", "password": "password123", "role": "USER"},
            {"email": "frank.miller@example.com", "password": "password123", "role": "USER"},
            {"email": "grace.taylor@example.com", "password": "password123", "role": "USER"},
            {"email": "henry.anderson@example.com", "password": "password123", "role": "USER"},
            {"email": "isabel.garcia@example.com", "password": "password123", "role": "ADMIN"},
            {"email": "jack.martinez@example.com", "password": "password123", "role": "USER"},
        ]
        
        created_users = []
        for user_data in dummy_users:
            existing_user = user_crud.get_user_by_email(db, user_data["email"])
            if existing_user:
                print(f"✓ User already exists: {user_data['email']}")
                created_users.append(existing_user)
                continue
            
            # Create user
            user_create = UserCreate(email=user_data["email"], password=user_data["password"])
            user = user_crud.create_user(db, user_create)
            
            # Set role if not default
            if user_data["role"] != "USER":
                user.role = user_data["role"]
                db.commit()
                db.refresh(user)
            
            created_users.append(user)
            print(f"✓ Created user: {user_data['email']} ({user_data['role']})")
        
        return created_users
        
    except Exception as e:
        print(f"✗ Failed to create dummy users: {str(e)}")
        db.rollback()
        return []
    finally:
        db.close()

def create_dummy_products():
    """Create 10 dummy products with varied categories and properties."""
    db = SessionLocal()
    try:
        dummy_products = [
            {
                "title": "Vintage Family Portrait Magnet",
                "price": 24.99,
                "category": "Photo Magnets",
                "rating": 4.8,
                "images": ["family_portrait_1.jpg", "family_portrait_2.jpg"],
                "is_locked": False
            },
            {
                "title": "Wedding Memory Magnet Set",
                "price": 35.50,
                "category": "Photo Magnets",
                "rating": 4.9,
                "images": ["wedding_magnet_1.jpg"],
                "is_locked": False
            },
            {
                "title": "Baby's First Year Collection",
                "price": 42.00,
                "category": "Photo Magnets",
                "rating": 4.7,
                "images": ["baby_collection_1.jpg", "baby_collection_2.jpg", "baby_collection_3.jpg"],
                "is_locked": True
            },
            {
                "title": "Cool Cat Fridge Magnet",
                "price": 12.99,
                "category": "Fridge Magnets",
                "rating": 4.3,
                "images": ["cool_cat_magnet.jpg"],
                "is_locked": False
            },
            {
                "title": "Motivational Quote Magnets",
                "price": 18.75,
                "category": "Fridge Magnets",
                "rating": 4.2,
                "images": ["motivational_1.jpg", "motivational_2.jpg"],
                "is_locked": False
            },
            {
                "title": "Kitchen Utensils Fun Magnets",
                "price": 22.30,
                "category": "Fridge Magnets",
                "rating": 4.5,
                "images": ["kitchen_utensils.jpg"],
                "is_locked": False
            },
            {
                "title": "1950s Diner Retro Print",
                "price": 45.00,
                "category": "Retro Prints",
                "rating": 4.6,
                "images": ["diner_retro_1.jpg", "diner_retro_2.jpg"],
                "is_locked": False
            },
            {
                "title": "Classic Car Collection Print",
                "price": 38.99,
                "category": "Retro Prints",
                "rating": 4.4,
                "images": ["classic_cars.jpg"],
                "is_locked": True
            },
            {
                "title": "Vintage Travel Posters",
                "price": 52.50,
                "category": "Retro Prints",
                "rating": 4.8,
                "images": ["travel_poster_1.jpg", "travel_poster_2.jpg", "travel_poster_3.jpg"],
                "is_locked": False
            },
            {
                "title": "Art Deco Architecture Print",
                "price": 48.75,
                "category": "Retro Prints",
                "rating": 4.7,
                "images": ["art_deco_1.jpg"],
                "is_locked": False
            }
        ]
        
        created_products = []
        for product_data in dummy_products:
            # Check if product with same title already exists
            existing_products = product_crud.get_products(db, skip=0, limit=100)
            if any(p.title == product_data["title"] for p in existing_products):
                print(f"✓ Product already exists: {product_data['title']}")
                continue
            
            # Create product
            product_create = ProductCreate(
                title=product_data["title"],
                price=product_data["price"],
                category=product_data["category"],
                rating=product_data["rating"],
                images=product_data["images"]
            )
            
            product = product_crud.create_product(db, product_create)
            
            # Set locked status if specified
            if product_data["is_locked"]:
                product.is_locked = True
                db.commit()
                db.refresh(product)
            
            created_products.append(product)
            lock_status = " (LOCKED)" if product_data["is_locked"] else ""
            print(f"✓ Created product: {product_data['title']} - ${product_data['price']}{lock_status}")
        
        return created_products
        
    except Exception as e:
        print(f"✗ Failed to create dummy products: {str(e)}")
        db.rollback()
        return []
    finally:
        db.close()

def display_statistics():
    """Display current database statistics."""
    db = SessionLocal()
    try:
        # Count users
        all_users = user_crud.get_users(db, skip=0, limit=1000)
        total_users = len(all_users)
        admin_users = len([u for u in all_users if u.role.upper() == "ADMIN"])
        regular_users = total_users - admin_users
        
        # Count products by category and status
        all_products = product_crud.get_products(db, skip=0, limit=1000)
        total_products = len(all_products)
        
        photo_magnets = len([p for p in all_products if p.category == "Photo Magnets"])
        fridge_magnets = len([p for p in all_products if p.category == "Fridge Magnets"])
        retro_prints = len([p for p in all_products if p.category == "Retro Prints"])
        
        locked_products = len([p for p in all_products if p.is_locked])
        unlocked_products = total_products - locked_products
        
        print("📊 Database Statistics:")
        print(f"   • Total Users: {total_users}")
        print(f"     - Admin Users: {admin_users}")
        print(f"     - Regular Users: {regular_users}")
        print(f"   • Total Products: {total_products}")
        print(f"     - Photo Magnets: {photo_magnets}")
        print(f"     - Fridge Magnets: {fridge_magnets}")
        print(f"     - Retro Prints: {retro_prints}")
        print(f"   • Product Status:")
        print(f"     - Unlocked: {unlocked_products}")
        print(f"     - Locked: {locked_products}")
        
    except Exception as e:
        print(f"✗ Failed to get statistics: {str(e)}")
    finally:
        db.close()

def main():
    """Main seeding function."""
    print("🌱 Seeding PixelForge Database with Dummy Data...")
    print("=" * 55)
    
    # Create dummy users
    print("👥 Creating dummy users...")
    users = create_dummy_users()
    print(f"   Created/Found {len(users)} users\n")
    
    # Create dummy products
    print("🎨 Creating dummy products...")
    products = create_dummy_products()
    print(f"   Created/Found {len(products)} products\n")
    
    print("=" * 55)
    display_statistics()
    print()
    print("🔐 Dummy User Credentials (all use password: 'password123'):")
    print("   • alice.johnson@example.com")
    print("   • bob.smith@example.com")
    print("   • carol.davis@example.com")
    print("   • david.wilson@example.com")
    print("   • emma.brown@example.com")
    print("   • frank.miller@example.com")
    print("   • grace.taylor@example.com")
    print("   • henry.anderson@example.com")
    print("   • isabel.garcia@example.com (ADMIN)")
    print("   • jack.martinez@example.com")
    print()
    print("✅ Dummy data seeding completed successfully!")

if __name__ == "__main__":
    main()
