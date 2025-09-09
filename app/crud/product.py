from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_
from typing import List, Optional
from app.models import Product, Category
from app.schemas import ProductCreate, ProductUpdate
from app.services.upload import upload_service

class ProductCRUD:
    def get_product_by_id(self, db: Session, product_id: int) -> Optional[Product]:
        """Get product by ID with category information."""
        return db.query(Product).join(Category, Product.category_id == Category.id).options(joinedload(Product.category_rel)).filter(Product.id == product_id).first()
    
    def get_products(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100, 
        category_id: Optional[int] = None
    ) -> List[Product]:
        """Get all products with pagination and optional category filter."""
        query = db.query(Product).join(Category, Product.category_id == Category.id).options(joinedload(Product.category_rel))
        
        if category_id:
            query = query.filter(Product.category_id == category_id)
        
        return query.offset(skip).limit(limit).all()
    
    def get_products_count(self, db: Session, category_id: Optional[int] = None) -> int:
        """Get total count of products."""
        query = db.query(Product)
        
        if category_id:
            query = query.filter(Product.category_id == category_id)
        
        return query.count()
    
    def get_unlocked_products(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100, 
        category_id: Optional[int] = None
    ) -> List[Product]:
        """Get only unlocked products with pagination and optional category filter."""
        query = db.query(Product).join(Category, Product.category_id == Category.id).options(joinedload(Product.category_rel)).filter(Product.is_locked == False)
        
        if category_id:
            query = query.filter(Product.category_id == category_id)
        
        return query.offset(skip).limit(limit).all()
    
    def get_unlocked_products_count(self, db: Session, category_id: Optional[int] = None) -> int:
        """Get total count of unlocked products."""
        query = db.query(Product).filter(Product.is_locked == False)
        
        if category_id:
            query = query.filter(Product.category_id == category_id)
        
        return query.count()
    
    def create_product(self, db: Session, product: ProductCreate) -> Product:
        """Create new product."""
        # Validate that category exists and is active
        category = db.query(Category).filter(
            Category.id == product.category_id,
            Category.is_active == True
        ).first()
        
        if not category:
            raise ValueError(f"Category with ID {product.category_id} not found or inactive")
        
        db_product = Product(
            title=product.title,
            description=product.description,
            short_description=product.short_description,
            price=product.price,
            category_id=product.category_id,
            rating=product.rating,
            images=product.images or [],
            is_locked=False
        )
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        
        # Load the category relationship
        db_product = db.query(Product).options(joinedload(Product.category_rel)).filter(Product.id == db_product.id).first()
        return db_product
    
    def update_product(self, db: Session, product_id: int, product_update: ProductUpdate) -> Optional[Product]:
        """Update product information."""
        db_product = self.get_product_by_id(db, product_id)
        if not db_product:
            return None
        
        # Check if product is locked
        if db_product.is_locked:
            raise ValueError("Cannot update locked product")
        
        # Validate category if being updated
        if product_update.category_id:
            category = db.query(Category).filter(
                Category.id == product_update.category_id,
                Category.is_active == True
            ).first()
            
            if not category:
                raise ValueError(f"Category with ID {product_update.category_id} not found or inactive")
        
        update_data = product_update.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(db_product, field, value)
        
        db.commit()
        db.refresh(db_product)
        
        # Reload with category relationship
        db_product = db.query(Product).options(joinedload(Product.category_rel)).filter(Product.id == db_product.id).first()
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
        
        # Reload with category relationship
        db_product = db.query(Product).options(joinedload(Product.category_rel)).filter(Product.id == db_product.id).first()
        return db_product
    
    def unlock_product(self, db: Session, product_id: int) -> Optional[Product]:
        """Unlock a product to allow modifications."""
        db_product = self.get_product_by_id(db, product_id)
        if not db_product:
            return None
        
        db_product.is_locked = False
        db.commit()
        db.refresh(db_product)
        
        # Reload with category relationship
        db_product = db.query(Product).options(joinedload(Product.category_rel)).filter(Product.id == db_product.id).first()
        return db_product

product_crud = ProductCRUD()
