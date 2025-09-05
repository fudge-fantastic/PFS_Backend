from sqlalchemy.orm import Session
from typing import List, Optional
from app.models import Category
from app.schemas import CategoryCreate, CategoryUpdate

class CategoryCRUD:
    def get_category_by_id(self, db: Session, category_id: int) -> Optional[Category]:
        """Get category by ID."""
        return db.query(Category).filter(Category.id == category_id).first()
    
    def get_category_by_name(self, db: Session, name: str) -> Optional[Category]:
        """Get category by name."""
        return db.query(Category).filter(Category.name == name).first()
    
    def get_categories(self, db: Session, skip: int = 0, limit: int = 100, active_only: bool = False) -> List[Category]:
        """Get list of categories with optional pagination and active filter."""
        query = db.query(Category)
        if active_only:
            query = query.filter(Category.is_active == True)
        return query.offset(skip).limit(limit).all()
    
    def get_categories_count(self, db: Session, active_only: bool = False) -> int:
        """Get total count of categories."""
        query = db.query(Category)
        if active_only:
            query = query.filter(Category.is_active == True)
        return query.count()
    
    def create_category(self, db: Session, category: CategoryCreate) -> Category:
        """Create a new category."""
        # Check if category name already exists
        existing_category = self.get_category_by_name(db, category.name)
        if existing_category:
            raise ValueError(f"Category with name '{category.name}' already exists")
        
        db_category = Category(
            name=category.name,
            description=category.description,
            is_active=True
        )
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
        return db_category
    
    def update_category(self, db: Session, category_id: int, category_update: CategoryUpdate) -> Optional[Category]:
        """Update an existing category."""
        db_category = self.get_category_by_id(db, category_id)
        if not db_category:
            return None
        
        # Check if new name conflicts with existing category
        if category_update.name and category_update.name != db_category.name:
            existing_category = self.get_category_by_name(db, category_update.name)
            if existing_category:
                raise ValueError(f"Category with name '{category_update.name}' already exists")
        
        # Update fields
        update_data = category_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_category, field, value)
        
        db.commit()
        db.refresh(db_category)
        return db_category
    
    def delete_category(self, db: Session, category_id: int) -> bool:
        """Delete a category (soft delete by setting is_active=False)."""
        db_category = self.get_category_by_id(db, category_id)
        if not db_category:
            return False
        
        # Check if category has associated products
        from app.models import Product
        product_count = db.query(Product).filter(Product.category_id == category_id).count()
        if product_count > 0:
            raise ValueError(f"Cannot delete category. It has {product_count} associated products.")
        
        # Soft delete
        db_category.is_active = False
        db.commit()
        return True
    
    def hard_delete_category(self, db: Session, category_id: int) -> bool:
        """Permanently delete a category (use with caution)."""
        db_category = self.get_category_by_id(db, category_id)
        if not db_category:
            return False
        
        # Check if category has associated products
        from app.models import Product
        product_count = db.query(Product).filter(Product.category_id == category_id).count()
        if product_count > 0:
            raise ValueError(f"Cannot delete category. It has {product_count} associated products.")
        
        db.delete(db_category)
        db.commit()
        return True

# Create global instance
category_crud = CategoryCRUD()
