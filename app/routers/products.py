from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.schemas import (
    ProductCreate, ProductUpdate, Product, 
    ProductListResponse, APIResponse, ProductCategory
)
from app.crud.product import product_crud
from app.dependencies.auth import get_current_user, get_current_admin_user
from app.services.upload import upload_service
from app.services.email import email_service
from app.models import User as UserModel
from app.config import settings

router = APIRouter(prefix="/products", tags=["Products"])

@router.post("/", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    title: str = Form(..., max_length=150),
    price: float = Form(..., gt=0),
    category: ProductCategory = Form(...),
    rating: float = Form(0.0, ge=0.0, le=5.0),
    images: Optional[List[UploadFile]] = File(None),
    current_user: UserModel = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Create a new product (Admin only)."""
    try:
        # Handle image uploads
        image_paths = []
        if images:
            if len(images) > 5:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Maximum 5 images allowed per product"
                )
            image_paths = await upload_service.upload_product_images(images)
        
        # Validate category
        if category.value not in settings.allowed_categories:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid category. Allowed categories: {', '.join(settings.allowed_categories)}"
            )
        
        # Create product
        product_data = ProductCreate(
            title=title,
            price=price,
            category=category,
            rating=rating,
            images=image_paths
        )
        
        db_product = product_crud.create_product(db, product_data)
        
        return APIResponse(
            success=True,
            message="Product created successfully",
            data={
                "id": db_product.id,
                "title": db_product.title,
                "price": db_product.price,
                "category": db_product.category,  # Already a string
                "rating": db_product.rating,
                "images": db_product.images,
                "is_locked": db_product.is_locked,
                "created_at": db_product.created_at.isoformat()
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create product: {str(e)}"
        )

@router.get("/unlocked", response_model=ProductListResponse)
async def list_unlocked_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    category: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """List only unlocked products with optional category filter."""
    try:
        # Validate category if provided
        if category and category not in settings.allowed_categories:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid category. Allowed categories: {', '.join(settings.allowed_categories)}"
            )
        
        products = product_crud.get_unlocked_products(db, skip=skip, limit=limit, category=category)
        total_count = product_crud.get_unlocked_products_count(db, category=category)
        
        products_data = []
        for product in products:
            products_data.append({
                "id": product.id,
                "title": product.title,
                "price": product.price,
                "category": product.category,
                "rating": product.rating,
                "images": product.images,
                "is_locked": product.is_locked,
                "created_at": product.created_at.isoformat(),
                "updated_at": product.updated_at.isoformat()
            })
        
        return ProductListResponse(
            success=True,
            message=f"Retrieved {len(products)} unlocked products successfully",
            data=products_data,
            total=total_count
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve unlocked products: {str(e)}"
        )

@router.get("/", response_model=ProductListResponse)
async def list_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    category: Optional[str] = Query(None),  # Changed from ProductCategory to str
    db: Session = Depends(get_db)
):
    """List all products with optional category filter."""
    try:
        # Validate category if provided
        if category and category not in settings.allowed_categories:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid category. Allowed categories: {', '.join(settings.allowed_categories)}"
            )
        
        products = product_crud.get_products(db, skip=skip, limit=limit, category=category)
        total_count = product_crud.get_products_count(db, category=category)
        
        products_data = []
        for product in products:
            products_data.append({
                "id": product.id,
                "title": product.title,
                "price": product.price,
                "category": product.category,  # Already a string
                "rating": product.rating,
                "images": product.images,
                "is_locked": product.is_locked,
                "created_at": product.created_at.isoformat(),
                "updated_at": product.updated_at.isoformat()
            })
        
        return ProductListResponse(
            success=True,
            message=f"Retrieved {len(products)} products successfully",
            data=products_data,
            total=total_count
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve products: {str(e)}"
        )

@router.get("/{product_id}", response_model=APIResponse)
async def get_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    """Get product details by ID."""
    product = product_crud.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    return APIResponse(
        success=True,
        message="Product details retrieved successfully",
        data={
            "id": product.id,
            "title": product.title,
            "price": product.price,
            "category": product.category,  # Already a string
            "rating": product.rating,
            "images": product.images,
            "is_locked": product.is_locked,
            "created_at": product.created_at.isoformat(),
            "updated_at": product.updated_at.isoformat()
        }
    )

@router.put("/{product_id}", response_model=APIResponse)
async def update_product(
    product_id: int,
    title: Optional[str] = Form(None, max_length=150),
    price: Optional[float] = Form(None, gt=0),
    category: Optional[ProductCategory] = Form(None),
    rating: Optional[float] = Form(None, ge=0.0, le=5.0),
    images: Optional[List[UploadFile]] = File(None),
    current_user: UserModel = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Update product (Admin only)."""
    try:
        # Check if product exists
        existing_product = product_crud.get_product_by_id(db, product_id)
        if not existing_product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        # Handle new image uploads
        image_paths = None
        if images:
            if len(images) > 5:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Maximum 5 images allowed per product"
                )
            # Delete old images
            if existing_product.images:
                upload_service.delete_product_images(existing_product.images)
            
            # Upload new images
            image_paths = await upload_service.upload_product_images(images)
        
        # Create update object
        update_data = {}
        if title is not None:
            update_data["title"] = title
        if price is not None:
            update_data["price"] = price
        if category is not None:
            update_data["category"] = category
        if rating is not None:
            update_data["rating"] = rating
        if image_paths is not None:
            update_data["images"] = image_paths
        
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields provided for update"
            )
        
        product_update = ProductUpdate(**update_data)
        updated_product = product_crud.update_product(db, product_id, product_update)
        
        return APIResponse(
            success=True,
            message="Product updated successfully",
            data={
                "id": updated_product.id,
                "title": updated_product.title,
                "price": updated_product.price,
                "category": updated_product.category,  # Already a string
                "rating": updated_product.rating,
                "images": updated_product.images,
                "is_locked": updated_product.is_locked,
                "updated_at": updated_product.updated_at.isoformat()
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update product: {str(e)}"
        )

@router.delete("/{product_id}", response_model=APIResponse)
async def delete_product(
    product_id: int,
    current_user: UserModel = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Delete product (Admin only)."""
    try:
        success = product_crud.delete_product(db, product_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        return APIResponse(
            success=True,
            message="Product deleted successfully",
            data={"id": product_id}
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete product: {str(e)}"
        )

@router.patch("/{product_id}/lock", response_model=APIResponse)
async def lock_product(
    product_id: int,
    current_user: UserModel = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Lock product to prevent modifications (Admin only)."""
    try:
        locked_product = product_crud.lock_product(db, product_id)
        if not locked_product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        return APIResponse(
            success=True,
            message="Product locked successfully",
            data={
                "id": locked_product.id,
                "title": locked_product.title,
                "is_locked": locked_product.is_locked
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to lock product: {str(e)}"
        )

@router.patch("/{product_id}/unlock", response_model=APIResponse)
async def unlock_product(
    product_id: int,
    current_user: UserModel = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Unlock product to allow modifications (Admin only)."""
    try:
        unlocked_product = product_crud.unlock_product(db, product_id)
        if not unlocked_product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        return APIResponse(
            success=True,
            message="Product unlocked successfully",
            data={
                "id": unlocked_product.id,
                "title": unlocked_product.title,
                "is_locked": unlocked_product.is_locked
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to unlock product: {str(e)}"
        )
