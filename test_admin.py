#!/usr/bin/env python3
"""Test script to verify admin authentication"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.crud.user import user_crud
from app.dependencies.auth import get_current_admin_user

def test_admin_check():
    """Test admin role checking logic"""
    db = SessionLocal()
    try:
        # Get admin user
        admin_user = user_crud.get_user_by_email(db, "admin@pfs.in")
        if not admin_user:
            print("❌ Admin user not found!")
            return
            
        print(f"✓ Admin user found: {admin_user.email}")
        print(f"✓ Admin role: '{admin_user.role}' (type: {type(admin_user.role)})")
        
        # Test the role check logic
        try:
            # Simulate the check from get_current_admin_user
            if admin_user.role.lower() not in ["admin"]:
                raise HTTPException(status_code=403, detail="Not admin")
            print("✅ Admin role check PASSED")
        except HTTPException:
            print("❌ Admin role check FAILED")
            
        # Test other users
        users = user_crud.get_users(db, limit=5)
        print(f"\n📋 Testing role checks for {len(users)} users:")
        for user in users:
            is_admin = user.role.lower() in ["admin"]
            print(f"  {user.email}: '{user.role}' -> Admin: {is_admin}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_admin_check()
