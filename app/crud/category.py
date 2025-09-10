from typing import List, Optional
from app.models import Category, Product
from app.schemas import CategoryCreate, CategoryUpdate
from bson import ObjectId
from datetime import datetime

class CategoryCRUD:
    async def get_category_by_id(self, category_id: str) -> Optional[Category]:
        """Get category by ID."""
        if not ObjectId.is_valid(category_id):
            return None
        return await Category.get(ObjectId(category_id))
    
    async def get_category_by_name(self, name: str) -> Optional[Category]:
        """Get category by name."""
        return await Category.find_one(Category.name == name)
    
    async def get_categories(self, skip: int = 0, limit: int = 100, active_only: bool = False) -> List[Category]:
        """Get list of categories with optional pagination and active filter."""
        if active_only:
            query = Category.find(Category.is_active == True)
        else:
            query = Category.find_all()
        
        return await query.skip(skip).limit(limit).to_list()
    
    async def get_categories_count(self, active_only: bool = False) -> int:
        """Get total count of categories."""
        if active_only:
            return await Category.find(Category.is_active == True).count()
        return await Category.count()
    
    async def create_category(self, category: CategoryCreate) -> Category:
        """Create a new category."""
        # Check if category name already exists
        existing_category = await self.get_category_by_name(category.name)
        if existing_category:
            raise ValueError(f"Category with name '{category.name}' already exists")
        
        db_category = Category(
            name=category.name,
            description=category.description,
            is_active=True
        )
        return await db_category.insert()
    
    async def update_category(self, category_id: str, category_update: CategoryUpdate) -> Optional[Category]:
        """Update an existing category."""
        if not ObjectId.is_valid(category_id):
            return None
        
        db_category = await self.get_category_by_id(category_id)
        if not db_category:
            return None
        
        # Check if new name conflicts with existing category
        if category_update.name and category_update.name != db_category.name:
            existing_category = await self.get_category_by_name(category_update.name)
            if existing_category:
                raise ValueError(f"Category with name '{category_update.name}' already exists")
        
        # Update fields
        update_data = category_update.dict(exclude_unset=True)
        update_data["updated_at"] = datetime.utcnow()
        
        for field, value in update_data.items():
            setattr(db_category, field, value)
        
        return await db_category.save()
    
    async def delete_category(self, category_id: str) -> bool:
        """Delete a category (soft delete by setting is_active=False)."""
        if not ObjectId.is_valid(category_id):
            return False
        
        db_category = await self.get_category_by_id(category_id)
        if not db_category:
            return False
        
        # Check if category has associated products
        product_count = await Product.find(Product.category_id == db_category).count()
        if product_count > 0:
            raise ValueError(f"Cannot delete category. It has {product_count} associated products.")
        
        # Soft delete
        db_category.is_active = False
        db_category.updated_at = datetime.utcnow()
        await db_category.save()
        return True
    
    async def hard_delete_category(self, category_id: str) -> bool:
        """Permanently delete a category (use with caution)."""
        if not ObjectId.is_valid(category_id):
            return False
        
        db_category = await self.get_category_by_id(category_id)
        if not db_category:
            return False
        
        # Check if category has associated products
        product_count = await Product.find(Product.category_id == db_category).count()
        if product_count > 0:
            raise ValueError(f"Cannot delete category. It has {product_count} associated products.")
        
        await db_category.delete()
        return True

# Create global instance
category_crud = CategoryCRUD()
