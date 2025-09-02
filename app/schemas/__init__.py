from pydantic import BaseModel, EmailStr, Field, validator
from typing import List, Optional
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "ADMIN"
    USER = "USER"

class ProductCategory(str, Enum):
    PHOTO_MAGNETS = "Photo Magnets"
    FRIDGE_MAGNETS = "Fridge Magnets"
    RETRO_PRINTS = "Retro Prints"

# User Schemas
class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8)

class User(UserBase):
    id: int
    role: UserRole
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class UserInDB(User):
    hashed_password: str

# Product Schemas
class ProductBase(BaseModel):
    title: str = Field(..., max_length=150)
    price: float = Field(..., gt=0)
    category: ProductCategory
    rating: Optional[float] = Field(0.0, ge=0.0, le=5.0)

class ProductCreate(ProductBase):
    images: Optional[List[str]] = Field(default=[], max_items=5)
    
    @validator('images')
    def validate_images(cls, v):
        if v and len(v) > 5:
            raise ValueError('Maximum 5 images allowed per product')
        return v

class ProductUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=150)
    price: Optional[float] = Field(None, gt=0)
    category: Optional[ProductCategory] = None
    rating: Optional[float] = Field(None, ge=0.0, le=5.0)
    images: Optional[List[str]] = Field(None, max_items=5)
    is_locked: Optional[bool] = None

class Product(ProductBase):
    id: int
    images: List[str]
    is_locked: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Auth Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# Inquiry Schemas
class InquiryRequest(BaseModel):
    first_name: str = Field(..., max_length=50, description="First name of the inquirer")
    last_name: str = Field(..., max_length=50, description="Last name of the inquirer")
    email: EmailStr = Field(..., description="Email address of the inquirer")
    phone_number: Optional[str] = Field(None, max_length=20, description="Phone number (optional)")
    subject: str = Field(..., max_length=100, description="Subject of the inquiry")
    message: str = Field(..., max_length=1000, description="Inquiry message")
    subscribe_newsletter: bool = Field(False, description="Whether to subscribe to newsletter")

    @validator('first_name', 'last_name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Name fields cannot be empty')
        return v.strip()

    @validator('subject')
    def validate_subject(cls, v):
        if not v.strip():
            raise ValueError('Subject cannot be empty')
        return v.strip()

    @validator('message')
    def validate_message(cls, v):
        if not v.strip():
            raise ValueError('Message cannot be empty')
        if len(v.strip()) < 10:
            raise ValueError('Message must be at least 10 characters long')
        return v.strip()

    @validator('phone_number')
    def validate_phone(cls, v):
        if v:
            # Remove common phone number formatting
            clean_phone = ''.join(filter(str.isdigit, v))
            if len(clean_phone) < 10:
                raise ValueError('Phone number must be at least 10 digits')
        return v

# Response Schemas
class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None

class ProductListResponse(BaseModel):
    success: bool
    message: str
    data: List[Product]
    total: int

class UserListResponse(BaseModel):
    success: bool
    message: str
    data: List[User]
    total: int
