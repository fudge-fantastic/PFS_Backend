from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from app.models import Product, ProductCategory
from app.schemas import ProductCreate, ProductUpdate
from app.services.upload import upload_service

class ProductCRUD:
    def get_product_by_id(self, db: Session, product_id: int) -> Optional[Product]:
        """Get product by ID."""
        return db.query(Product).filter(Product.id == product_id).first()
    
    def get_products(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100, 
        category: Optional[str] = None  # Changed from ProductCategory to str
    ) -> List[Product]:
        """Get all products with pagination and optional category filter."""
        query = db.query(Product)
        
        if category:
            query = query.filter(Product.category == category)
        
        return query.offset(skip).limit(limit).all()
    
    def get_products_count(self, db: Session, category: Optional[str] = None) -> int:  # Changed from ProductCategory to str
        """Get total count of products."""
        query = db.query(Product)
        
        if category:
            query = query.filter(Product.category == category)
        
        return query.count()
    
    def get_unlocked_products(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100, 
        category: Optional[str] = None
    ) -> List[Product]:
        """Get only unlocked products with pagination and optional category filter."""
        query = db.query(Product).filter(Product.is_locked == False)
        
        if category:
            query = query.filter(Product.category == category)
        
        return query.offset(skip).limit(limit).all()
    
    def get_unlocked_products_count(self, db: Session, category: Optional[str] = None) -> int:
        """Get total count of unlocked products."""
        query = db.query(Product).filter(Product.is_locked == False)
        
        if category:
            query = query.filter(Product.category == category)
        
        return query.count()
    
    def create_product(self, db: Session, product: ProductCreate) -> Product:
        """Create new product."""
        db_product = Product(
            title=product.title,
            price=product.price,
            category=product.category.value if hasattr(product.category, 'value') else product.category,  # Handle both enum and string
            rating=product.rating,
            images=product.images or [],
            is_locked=False
        )
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        return db_product
    
    def update_product(self, db: Session, product_id: int, product_update: ProductUpdate) -> Optional[Product]:
        """Update product information."""
        db_product = self.get_product_by_id(db, product_id)
        if not db_product:
            return None
        
        # Check if product is locked
        if db_product.is_locked:
            raise ValueError("Cannot update locked product")
        
        update_data = product_update.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(db_product, field, value)
        
        db.commit()
        db.refresh(db_product)
        return db_product
    
    def delete_product(self, db: Session, product_id: int) -> bool:
        """Delete product."""
        db_product = self.get_product_by_id(db, product_id)
        if not db_product:
            return False
        
        # Check if product is locked
        if db_product.is_locked:
            raise ValueError("Cannot delete locked product")
        
        # Delete associated images
        if db_product.images:
            upload_service.delete_product_images(db_product.images)
        
        db.delete(db_product)
        db.commit()
        return True
    
    def lock_product(self, db: Session, product_id: int) -> Optional[Product]:
        """Lock a product to prevent modifications."""
        db_product = self.get_product_by_id(db, product_id)
        if not db_product:
            return None
        
        db_product.is_locked = True
        db.commit()
        db.refresh(db_product)
        return db_product
    
    def unlock_product(self, db: Session, product_id: int) -> Optional[Product]:
        """Unlock a product to allow modifications."""
        db_product = self.get_product_by_id(db, product_id)
        if not db_product:
            return None
        
        db_product.is_locked = False
        db.commit()
        db.refresh(db_product)
        return db_product

product_crud = ProductCRUD()
