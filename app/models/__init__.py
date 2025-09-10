from beanie import Document, Indexed, Link
from pydantic import Field, EmailStr
from typing import Optional, List
from datetime import datetime
import enum
from bson import ObjectId

class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    USER = "USER"

class User(Document):
    email: Indexed(EmailStr, unique=True)
    hashed_password: str
    role: str = Field(default="USER")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "users"

class Category(Document):
    name: Indexed(str, unique=True)
    description: Optional[str] = None
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "categories"

class Product(Document):
    title: Indexed(str)
    description: Optional[str] = None
    short_description: Optional[str] = None
    price: float
    category_id: Link[Category]
    rating: float = Field(default=0.0)
    images: List[str] = Field(default_factory=list)
    is_locked: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "products"
