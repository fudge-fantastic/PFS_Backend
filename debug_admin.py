#!/usr/bin/env python3
"""Debug script to check admin user role"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.crud.user import user_crud

def main():
    db = SessionLocal()
    try:
        # Check admin user
        admin_user = user_crud.get_user_by_email(db, "admin@pfs.in")
        if admin_user:
            print(f"Admin user found:")
            print(f"  ID: {admin_user.id}")
            print(f"  Email: {admin_user.email}")
            print(f"  Role: {admin_user.role}")
            print(f"  Role type: {type(admin_user.role)}")
        else:
            print("Admin user not found!")
            
        # Check all users
        users = user_crud.get_users(db, limit=10)
        print(f"\nAll users ({len(users)}):")
        for user in users:
            print(f"  {user.email} -> Role: {user.role} (type: {type(user.role)})")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
