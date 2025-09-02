from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Enum, Text, JSON
from sqlalchemy.sql import func
from app.database import Base
import enum

class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    USER = "USER"

class ProductCategory(str, enum.Enum):
    PHOTO_MAGNETS = "Photo Magnets"
    FRIDGE_MAGNETS = "Fridge Magnets"
    RETRO_PRINTS = "Retro Prints"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), default="User", nullable=False)  # Store as string
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(150), nullable=False, index=True)
    price = Column(Float, nullable=False)
    category = Column(String(50), nullable=False, index=True)  # Store as string
    rating = Column(Float, default=0.0)
    images = Column(JSON, default=list)  # Use JSON for SQLite compatibility
    is_locked = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
