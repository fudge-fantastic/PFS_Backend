from typing import List, Optional
from app.models import Product, Category
from app.schemas import ProductCreate, ProductUpdate
from app.services.upload import upload_service
from bson import ObjectId
from datetime import datetime

class ProductCRUD:
    async def get_product_by_id(self, product_id: str) -> Optional[Product]:
        """Get product by ID with category information."""
        if not ObjectId.is_valid(product_id):
            return None
        return await Product.get(ObjectId(product_id), fetch_links=True)
    
    async def get_products(
        self, 
        skip: int = 0, 
        limit: int = 100, 
        category_id: Optional[str] = None
    ) -> List[Product]:
        """Get all products with pagination and optional category filter."""
        if category_id and ObjectId.is_valid(category_id):
            category = await Category.get(ObjectId(category_id))
            if not category:
                return []
            return await Product.find(Product.category_id == category).skip(skip).limit(limit).to_list()
        else:
            return await Product.find().skip(skip).limit(limit).to_list()
    
    async def get_products_count(self, category_id: Optional[str] = None) -> int:
        """Get total count of products."""
        if category_id and ObjectId.is_valid(category_id):
            category = await Category.get(ObjectId(category_id))
            if not category:
                return 0
            return await Product.find(Product.category_id == category).count()
        
        return await Product.find().count()
    
    async def get_unlocked_products(
        self, 
        skip: int = 0, 
        limit: int = 100, 
        category_id: Optional[str] = None
    ) -> List[Product]:
        """Get only unlocked products with pagination and optional category filter."""
        if category_id and ObjectId.is_valid(category_id):
            category = await Category.get(ObjectId(category_id))
            if not category:
                return []
            return await Product.find(
                Product.is_locked == False, 
                Product.category_id == category
            ).skip(skip).limit(limit).to_list()
        else:
            return await Product.find(Product.is_locked == False).skip(skip).limit(limit).to_list()
    
    async def get_unlocked_products_count(self, category_id: Optional[str] = None) -> int:
        """Get total count of unlocked products."""
        if category_id and ObjectId.is_valid(category_id):
            category = await Category.get(ObjectId(category_id))
            if not category:
                return 0
            return await Product.find(
                Product.is_locked == False, 
                Product.category_id == category
            ).count()
        
        return await Product.find(Product.is_locked == False).count()
    
    async def create_product(self, product: ProductCreate) -> Product:
        """Create new product."""
        # Validate that category exists and is active
        if not ObjectId.is_valid(product.category_id):
            raise ValueError(f"Invalid category ID: {product.category_id}")
        
        category = await Category.get(ObjectId(product.category_id))
        if not category or not category.is_active:
            raise ValueError(f"Category with ID {product.category_id} not found or inactive")
        
        db_product = Product(
            title=product.title,
            description=product.description,
            short_description=product.short_description,
            price=product.price,
            category_id=category,
            rating=product.rating,
            images=product.images or [],
            is_locked=False
        )
        return await db_product.insert()
    
    async def update_product(self, product_id: str, product_update: ProductUpdate) -> Optional[Product]:
        """Update product information."""
        if not ObjectId.is_valid(product_id):
            return None
        
        db_product = await self.get_product_by_id(product_id)
        if not db_product:
            return None
        
        # Check if product is locked
        if db_product.is_locked:
            raise ValueError("Cannot update locked product")
        
        # Validate category if being updated
        if product_update.category_id:
            if not ObjectId.is_valid(product_update.category_id):
                raise ValueError(f"Invalid category ID: {product_update.category_id}")
            
            category = await Category.get(ObjectId(product_update.category_id))
            if not category or not category.is_active:
                raise ValueError(f"Category with ID {product_update.category_id} not found or inactive")
        
        update_data = product_update.dict(exclude_unset=True)
        
        # Handle category_id update
        if "category_id" in update_data:
            category = await Category.get(ObjectId(update_data["category_id"]))
            update_data["category_id"] = category
        
        update_data["updated_at"] = datetime.utcnow()
        
        for field, value in update_data.items():
            setattr(db_product, field, value)
        
        return await db_product.save()
    
    async def delete_product(self, product_id: str) -> bool:
        """Delete product."""
        if not ObjectId.is_valid(product_id):
            return False
        
        db_product = await self.get_product_by_id(product_id)
        if not db_product:
            return False
        
        # Check if product is locked
        if db_product.is_locked:
            raise ValueError("Cannot delete locked product")
        
        # Delete associated images
        if db_product.images:
            upload_service.delete_product_images(db_product.images)
        
        await db_product.delete()
        return True
    
    async def lock_product(self, product_id: str) -> Optional[Product]:
        """Lock a product to prevent modifications."""
        if not ObjectId.is_valid(product_id):
            return None
        
        db_product = await self.get_product_by_id(product_id)
        if not db_product:
            return None
        
        db_product.is_locked = True
        db_product.updated_at = datetime.utcnow()
        return await db_product.save()
    
    async def unlock_product(self, product_id: str) -> Optional[Product]:
        """Unlock a product to allow modifications."""
        if not ObjectId.is_valid(product_id):
            return None
        
        db_product = await self.get_product_by_id(product_id)
        if not db_product:
            return None
        
        db_product.is_locked = False
        db_product.updated_at = datetime.utcnow()
        return await db_product.save()

product_crud = ProductCRUD()
