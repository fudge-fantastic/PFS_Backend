from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from app.models import User, UserRole
from app.schemas import UserCreate, UserUpdate
from app.services.auth import get_password_hash, verify_password

class UserCRUD:
    def get_user_by_id(self, db: Session, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_email(self, db: Session, email: str) -> Optional[User]:
        """Get user by email."""
        return db.query(User).filter(User.email == email).first()
    
    def get_users(self, db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users with pagination."""
        return db.query(User).offset(skip).limit(limit).all()
    
    def get_users_count(self, db: Session) -> int:
        """Get total count of users."""
        return db.query(User).count()
    
    def create_user(self, db: Session, user: UserCreate) -> User:
        """Create new user."""
        hashed_password = get_password_hash(user.password)
        db_user = User(
            email=user.email,
            hashed_password=hashed_password,
            role="USER"  # Default role as uppercase string
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    def update_user(self, db: Session, user_id: int, user_update: UserUpdate) -> Optional[User]:
        """Update user information."""
        db_user = self.get_user_by_id(db, user_id)
        if not db_user:
            return None
        
        update_data = user_update.dict(exclude_unset=True)
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
        
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        db.commit()
        db.refresh(db_user)
        return db_user
    
    def delete_user(self, db: Session, user_id: int) -> bool:
        """Delete user."""
        db_user = self.get_user_by_id(db, user_id)
        if not db_user:
            return False
        
        db.delete(db_user)
        db.commit()
        return True
    
    def authenticate_user(self, db: Session, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password."""
        print(f"Authenticating user: {email}, {password}")  # Debug: show email
        user = self.get_user_by_email(db, email)
        if not user:
            print("User not found.")  # Debug: user not found
            return None
        print(f"User found: {user.email}")  # Debug: user found
        if not verify_password(password, user.hashed_password):
            print("Password verification failed.")  # Debug: password failed
            return None
        print("Authentication successful.")  # Debug: success
        return user

user_crud = UserCRUD()
