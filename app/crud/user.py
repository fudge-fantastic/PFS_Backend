from typing import List, Optional
from app.models import User, UserRole
from app.schemas import UserCreate, UserUpdate
from app.services.auth import get_password_hash, verify_password
from bson import ObjectId
from datetime import datetime

class UserCRUD:
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        if not ObjectId.is_valid(user_id):
            return None
        return await User.get(ObjectId(user_id))
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        return await User.find_one(User.email == email)
    
    async def get_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users with pagination."""
        return await User.find_all().skip(skip).limit(limit).to_list()
    
    async def get_users_count(self) -> int:
        """Get total count of users."""
        return await User.count()
    
    async def create_user(self, user: UserCreate) -> User:
        """Create new user."""
        hashed_password = get_password_hash(user.password)
        db_user = User(
            email=user.email,
            hashed_password=hashed_password,
            role="USER"
        )
        return await db_user.insert()
    
    async def update_user(self, user_id: str, user_update: UserUpdate) -> Optional[User]:
        """Update user information."""
        if not ObjectId.is_valid(user_id):
            return None
        
        db_user = await self.get_user_by_id(user_id)
        if not db_user:
            return None
        
        update_data = user_update.dict(exclude_unset=True)
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
        
        update_data["updated_at"] = datetime.utcnow()
        
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        return await db_user.save()
    
    async def delete_user(self, user_id: str) -> bool:
        """Delete user."""
        if not ObjectId.is_valid(user_id):
            return False
        
        db_user = await self.get_user_by_id(user_id)
        if not db_user:
            return False
        
        await db_user.delete()
        return True
    
    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password."""
        print(f"Authenticating user: {email}, {password}")
        user = await self.get_user_by_email(email)
        if not user:
            print("User not found.")
            return None
        print(f"User found: {user.email}")
        if not verify_password(password, user.hashed_password):
            print("Password verification failed.")
            return None
        print("Authentication successful.")
        return user

user_crud = UserCRUD()
