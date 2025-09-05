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
from app.crud.category import category_crud
from app.schemas import UserCreate, ProductCreate, CategoryCreate

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

def create_dummy_categories():
    """Create dummy categories."""
    db = SessionLocal()
    try:
        dummy_categories = [
            {"name": "Photo Magnets", "description": "Custom photo magnets for your memories"},
            {"name": "Fridge Magnets", "description": "Decorative magnets for your refrigerator"},
            {"name": "Retro Prints", "description": "Vintage-style prints and posters"}
        ]
        
        created_categories = []
        for category_data in dummy_categories:
            existing_category = category_crud.get_category_by_name(db, category_data["name"])
            if existing_category:
                print(f"✓ Category already exists: {category_data['name']}")
                created_categories.append(existing_category)
                continue
            
            # Create category
            category_create = CategoryCreate(
                name=category_data["name"], 
                description=category_data["description"]
            )
            category = category_crud.create_category(db, category_create)
            created_categories.append(category)
            print(f"✓ Created category: {category_data['name']}")
        
        return created_categories
        
    except Exception as e:
        print(f"✗ Failed to create dummy categories: {str(e)}")
        db.rollback()
        return []
    finally:
        db.close()

def create_dummy_products():
    """Create 10 dummy products with varied categories and properties."""
    db = SessionLocal()
    try:
        # Get category IDs
        photo_magnets_cat = category_crud.get_category_by_name(db, "Photo Magnets")
        fridge_magnets_cat = category_crud.get_category_by_name(db, "Fridge Magnets")
        retro_prints_cat = category_crud.get_category_by_name(db, "Retro Prints")
        
        if not all([photo_magnets_cat, fridge_magnets_cat, retro_prints_cat]):
            raise ValueError("Required categories not found. Please create categories first.")
        
        dummy_products = [
            {
                "title": "Vintage Family Portrait Magnet",
                "description": "A beautiful vintage-style magnet featuring your family portrait. Perfect for preserving precious memories on your refrigerator or any magnetic surface.",
                "short_description": "Vintage family portrait magnet",
                "price": 24.99,
                "category_id": photo_magnets_cat.id,
                "rating": 4.8,
                "images": ["family_portrait_1.jpg", "family_portrait_2.jpg"],
                "is_locked": False
            },
            {
                "title": "Wedding Memory Magnet Set",
                "description": "Celebrate your special day with this elegant wedding memory magnet set. Features high-quality printing and durable magnetic backing.",
                "short_description": "Wedding memory magnet set",
                "price": 35.50,
                "category_id": photo_magnets_cat.id,
                "rating": 4.9,
                "images": ["wedding_magnet_1.jpg"],
                "is_locked": False
            },
            {
                "title": "Baby's First Year Collection",
                "description": "Document your baby's precious first year with this adorable collection of photo magnets. Includes monthly milestone templates.",
                "short_description": "Baby first year collection",
                "price": 42.00,
                "category_id": photo_magnets_cat.id,
                "rating": 4.7,
                "images": ["baby_collection_1.jpg", "baby_collection_2.jpg", "baby_collection_3.jpg"],
                "is_locked": True
            },
            {
                "title": "Cool Cat Fridge Magnet",
                "description": "Add some personality to your kitchen with this adorable cool cat fridge magnet. Features a fun cartoon design that will make you smile every day.",
                "short_description": "Cool cat fridge magnet",
                "price": 12.99,
                "category_id": fridge_magnets_cat.id,
                "rating": 4.3,
                "images": ["cool_cat_magnet.jpg"],
                "is_locked": False
            },
            {
                "title": "Motivational Quote Magnets",
                "description": "Inspire yourself daily with these motivational quote magnets. Perfect for your workspace or kitchen to keep you motivated throughout the day.",
                "short_description": "Motivational quote magnet set",
                "price": 18.75,
                "category_id": fridge_magnets_cat.id,
                "rating": 4.2,
                "images": ["motivational_1.jpg", "motivational_2.jpg"],
                "is_locked": False
            },
            {
                "title": "Kitchen Utensils Fun Magnets",
                "description": "These playful kitchen utensil magnets are perfect for organizing your recipes and notes. Features colorful designs of various cooking tools.",
                "short_description": "Kitchen utensils fun magnets",
                "price": 22.30,
                "category_id": fridge_magnets_cat.id,
                "rating": 4.5,
                "images": ["kitchen_utensils.jpg"],
                "is_locked": False
            },
            {
                "title": "1950s Diner Retro Print",
                "description": "Step back in time with this authentic 1950s diner retro print. Features classic American diner aesthetics with vibrant colors and nostalgic charm.",
                "short_description": "Classic 1950s diner print",
                "price": 45.00,
                "category_id": retro_prints_cat.id,
                "rating": 4.6,
                "images": ["diner_retro_1.jpg", "diner_retro_2.jpg"],
                "is_locked": False
            },
            {
                "title": "Classic Car Collection Print",
                "description": "A stunning collection print featuring iconic classic cars from the golden age of automobiles. Perfect for car enthusiasts and vintage lovers.",
                "short_description": "Classic car collection print",
                "price": 38.99,
                "category_id": retro_prints_cat.id,
                "rating": 4.4,
                "images": ["classic_cars.jpg"],
                "is_locked": True
            },
            {
                "title": "Vintage Travel Posters",
                "description": "Bring wanderlust to your walls with these vintage travel posters. Features iconic destinations from around the world in classic poster style.",
                "short_description": "Vintage travel poster collection",
                "price": 52.50,
                "category_id": retro_prints_cat.id,
                "rating": 4.8,
                "images": ["travel_poster_1.jpg", "travel_poster_2.jpg", "travel_poster_3.jpg"],
                "is_locked": False
            },
            {
                "title": "Art Deco Architecture Print",
                "description": "Celebrate the elegance of Art Deco architecture with this sophisticated print. Features geometric patterns and iconic building designs.",
                "short_description": "Art Deco architecture print",
                "price": 48.75,
                "category_id": retro_prints_cat.id,
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
                description=product_data["description"],
                short_description=product_data["short_description"],
                price=product_data["price"],
                category_id=product_data["category_id"],
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
        
        # Get categories
        photo_magnets_cat = category_crud.get_category_by_name(db, "Photo Magnets")
        fridge_magnets_cat = category_crud.get_category_by_name(db, "Fridge Magnets")
        retro_prints_cat = category_crud.get_category_by_name(db, "Retro Prints")
        
        photo_magnets = len([p for p in all_products if p.category_id == photo_magnets_cat.id]) if photo_magnets_cat else 0
        fridge_magnets = len([p for p in all_products if p.category_id == fridge_magnets_cat.id]) if fridge_magnets_cat else 0
        retro_prints = len([p for p in all_products if p.category_id == retro_prints_cat.id]) if retro_prints_cat else 0
        
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
    
    # Create dummy categories
    print("🏷️  Creating dummy categories...")
    categories = create_dummy_categories()
    print(f"   Created/Found {len(categories)} categories\n")
    
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
