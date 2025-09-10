from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from typing import List, Optional
import time
from app.schemas import (
    ProductCreate, ProductUpdate, Product, ProductResponse,
    ProductListResponse, APIResponse
)
from app.crud.product import product_crud
from app.crud.category import category_crud
from app.dependencies.auth import get_current_user, get_current_admin_user
from app.services.upload import upload_service
from app.services.email import email_service
from app.models import User as UserModel, Product as ProductModel
from app.config import settings

# Import ImageKit service for authentication
try:
    from app.services.imagekit_service import get_imagekit_service
    IMAGEKIT_AVAILABLE = True
except ImportError:
    IMAGEKIT_AVAILABLE = False

router = APIRouter(prefix="/products", tags=["Products"])

async def product_to_response(product: ProductModel) -> ProductResponse:
    """Convert Product model to ProductResponse with category name."""
    # Fetch category name if needed
    category_name = None
    if product.category_id:
        await product.fetch_link(ProductModel.category_id)
        category_name = product.category_id.name if product.category_id else None
    
    return ProductResponse(
        id=str(product.id),
        title=product.title,
        description=product.description,
        short_description=product.short_description,
        price=product.price,
        category_id=str(product.category_id.id) if product.category_id else None,
        category_name=category_name,
        rating=product.rating,
        images=product.images,
        is_locked=product.is_locked,
        created_at=product.created_at,
        updated_at=product.updated_at
    )

@router.post("/", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    title: str = Form(..., max_length=150),
    description: Optional[str] = Form(None, max_length=1000),
    short_description: Optional[str] = Form(None, max_length=50),
    price: float = Form(..., gt=0),
    category_id: str = Form(...),
    rating: float = Form(0.0, ge=0.0, le=5.0),
    images: List[UploadFile] = File(default=[], description="Upload product images (max 5 files)"),
    current_user: UserModel = Depends(get_current_admin_user)
):
    """Create a new product (Admin only)."""
    try:
        # Validate category exists and is active before creating product
        category = await category_crud.get_category_by_id(category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category with ID {category_id} not found"
            )
        if not category.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category '{category.name}' is currently inactive"
            )
        
        # Handle image uploads
        image_paths = []
        if images and len(images) > 0:
            # Filter out empty files (files with no filename)
            valid_images = [img for img in images if img.filename and img.filename.strip()]
            
            if len(valid_images) > 5:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Maximum 5 images allowed per product"
                )
            
            if valid_images:
                image_paths = await upload_service.upload_product_images(valid_images)
        
        # Create product data with validation
        try:
            product_data = ProductCreate(
                title=title,
                description=description,
                short_description=short_description,
                price=price,
                category_id=category_id,
                rating=rating,
                images=image_paths
            )
        except Exception as validation_error:
            from pydantic import ValidationError
            if isinstance(validation_error, ValidationError):
                error_messages = []
                for error in validation_error.errors():
                    field = error["loc"][-1] if error["loc"] else "unknown"
                    message = error["msg"]
                    error_messages.append(f"{field}: {message}")
                detail = "Validation failed: " + "; ".join(error_messages)
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
            else:
                raise
        
        db_product = await product_crud.create_product(product_data)
        
        # Convert to response format with category name
        product_data = await product_to_response(db_product)
        
        return APIResponse(
            success=True,
            message="Product created successfully",
            data=product_data.dict()
        )
    except HTTPException:
        # Re-raise HTTPException as-is
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        # Import ValidationError for better error handling
        from pydantic import ValidationError
        if isinstance(e, ValidationError):
            error_messages = []
            for error in e.errors():
                field = " -> ".join(str(loc) for loc in error["loc"])
                message = error["msg"]
                error_messages.append(f"{field}: {message}")
            detail = "Validation errors: " + "; ".join(error_messages)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
        else:
            detail = f"Failed to create product: {str(e)}"
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )

@router.get("/unlocked", response_model=ProductListResponse)
async def list_unlocked_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    category_id: Optional[str] = Query(None)
):
    """List only unlocked products with optional category filter."""
    try:
        # Validate category if provided
        if category_id:
            category = await category_crud.get_category_by_id(category_id)
            if not category or not category.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Category with ID {category_id} not found or inactive"
                )
        
        products = await product_crud.get_unlocked_products(skip=skip, limit=limit, category_id=category_id)
        total_count = await product_crud.get_unlocked_products_count(category_id=category_id)
        
        # Convert products to response format with category names
        products_data = [await product_to_response(product) for product in products]
        
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
    category_id: Optional[str] = Query(None)
):
    """List all products with optional category filter."""
    try:
        # Validate category if provided
        if category_id:
            category = await category_crud.get_category_by_id(category_id)
            if not category or not category.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Category with ID {category_id} not found or inactive"
                )
        
        products = await product_crud.get_products(skip=skip, limit=limit, category_id=category_id)
        total_count = await product_crud.get_products_count(category_id=category_id)
        
        # Convert products to response format with category names
        products_data = [await product_to_response(product) for product in products]
        
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
async def get_product(product_id: str):
    """Get product details by ID."""
    product = await product_crud.get_product_by_id(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Convert to response format with category name
    product_data = await product_to_response(product)
    
    return APIResponse(
        success=True,
        message="Product details retrieved successfully",
        data=product_data.dict()
    )

@router.put("/{product_id}", response_model=APIResponse)
async def update_product(
    product_id: str,
    title: Optional[str] = Form(None, max_length=150),
    description: Optional[str] = Form(None, max_length=1000),
    short_description: Optional[str] = Form(None, max_length=50),
    price: Optional[float] = Form(None, gt=0),
    category_id: Optional[str] = Form(None),
    rating: Optional[float] = Form(None, ge=0.0, le=5.0),
    images: List[UploadFile] = File(default=[], description="Upload product images (max 5 files, replaces existing)"),
    current_user: UserModel = Depends(get_current_admin_user)
):
    """Update product (Admin only)."""
    try:
        # Check if product exists
        existing_product = await product_crud.get_product_by_id(product_id)
        if not existing_product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
    # No word count constraint for short_description
        
        # Handle new image uploads
        image_paths = None
        if images and len(images) > 0:
            # Filter out empty files (files with no filename)
            valid_images = [img for img in images if img.filename and img.filename.strip()]
            
            if len(valid_images) > 5:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Maximum 5 images allowed per product"
                )
            
            if valid_images:
                # Delete old images
                if existing_product.images:
                    upload_service.delete_product_images(existing_product.images)
                
                # Upload new images
                image_paths = await upload_service.upload_product_images(valid_images)
        
        # Create update object
        update_data = {}
        if title is not None:
            update_data["title"] = title
        if description is not None:
            update_data["description"] = description
        if short_description is not None:
            update_data["short_description"] = short_description
        if price is not None:
            update_data["price"] = price
        if category_id is not None:
            update_data["category_id"] = category_id
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
        updated_product = await product_crud.update_product(product_id, product_update)
        
        # Convert to response format with category name
        product_data = await product_to_response(updated_product)
        
        return APIResponse(
            success=True,
            message="Product updated successfully",
            data=product_data.dict()
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
    product_id: str,
    current_user: UserModel = Depends(get_current_admin_user)
):
    """Delete product (Admin only)."""
    try:
        success = await product_crud.delete_product(product_id)
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
    product_id: str,
    current_user: UserModel = Depends(get_current_admin_user)
):
    """Lock product to prevent modifications (Admin only)."""
    try:
        locked_product = await product_crud.lock_product(product_id)
        if not locked_product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        # Fetch category name
        category_name = None
        if locked_product.category_id:
            await locked_product.fetch_link(ProductModel.category_id)
            category_name = locked_product.category_id.name if locked_product.category_id else None
        
        return APIResponse(
            success=True,
            message="Product locked successfully",
            data={
                "id": str(locked_product.id),
                "title": locked_product.title,
                "category_id": str(locked_product.category_id.id) if locked_product.category_id else None,
                "category_name": category_name,
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
    product_id: str,
    current_user: UserModel = Depends(get_current_admin_user)
):
    """Unlock product to allow modifications (Admin only)."""
    try:
        unlocked_product = await product_crud.unlock_product(product_id)
        if not unlocked_product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        # Fetch category name
        category_name = None
        if unlocked_product.category_id:
            await unlocked_product.fetch_link(ProductModel.category_id)
            category_name = unlocked_product.category_id.name if unlocked_product.category_id else None
        
        return APIResponse(
            success=True,
            message="Product unlocked successfully",
            data={
                "id": str(unlocked_product.id),
                "title": unlocked_product.title,
                "category_id": str(unlocked_product.category_id.id) if unlocked_product.category_id else None,
                "category_name": category_name,
                "is_locked": unlocked_product.is_locked
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to unlock product: {str(e)}"
        )