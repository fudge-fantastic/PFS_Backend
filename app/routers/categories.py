from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.schemas import (
    CategoryCreate, CategoryUpdate, Category, 
    CategoryListResponse, APIResponse
)
from app.crud.category import category_crud
from app.dependencies.auth import get_current_admin_user
from app.models import User as UserModel

router = APIRouter(prefix="/categories", tags=["Categories"])

@router.post("/", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category: CategoryCreate,
    current_user: UserModel = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Create a new category (Admin only)."""
    try:
        db_category = category_crud.create_category(db, category)
        
        return APIResponse(
            success=True,
            message="Category created successfully",
            data={
                "id": db_category.id,
                "name": db_category.name,
                "description": db_category.description,
                "is_active": db_category.is_active,
                "created_at": db_category.created_at.isoformat()
            }
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create category: {str(e)}"
        )

@router.get("/", response_model=CategoryListResponse)
async def list_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    active_only: bool = Query(False, description="Filter to show only active categories"),
    db: Session = Depends(get_db)
):
    """List all categories with optional filtering."""
    try:
        categories = category_crud.get_categories(db, skip=skip, limit=limit, active_only=active_only)
        total_count = category_crud.get_categories_count(db, active_only=active_only)
        
        categories_data = []
        for category in categories:
            categories_data.append({
                "id": category.id,
                "name": category.name,
                "description": category.description,
                "is_active": category.is_active,
                "created_at": category.created_at.isoformat(),
                "updated_at": category.updated_at.isoformat()
            })
        
        filter_text = "active " if active_only else ""
        return CategoryListResponse(
            success=True,
            message=f"Retrieved {len(categories)} {filter_text}categories successfully",
            data=categories_data,
            total=total_count
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve categories: {str(e)}"
        )

@router.get("/active", response_model=CategoryListResponse)
async def list_active_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """List only active categories (public endpoint)."""
    try:
        categories = category_crud.get_categories(db, skip=skip, limit=limit, active_only=True)
        total_count = category_crud.get_categories_count(db, active_only=True)
        
        categories_data = []
        for category in categories:
            categories_data.append({
                "id": category.id,
                "name": category.name,
                "description": category.description,
                "is_active": category.is_active,
                "created_at": category.created_at.isoformat(),
                "updated_at": category.updated_at.isoformat()
            })
        
        return CategoryListResponse(
            success=True,
            message=f"Retrieved {len(categories)} active categories successfully",
            data=categories_data,
            total=total_count
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve active categories: {str(e)}"
        )

@router.get("/{category_id}", response_model=APIResponse)
async def get_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    """Get category details by ID."""
    category = category_crud.get_category_by_id(db, category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    return APIResponse(
        success=True,
        message="Category details retrieved successfully",
        data={
            "id": category.id,
            "name": category.name,
            "description": category.description,
            "is_active": category.is_active,
            "created_at": category.created_at.isoformat(),
            "updated_at": category.updated_at.isoformat()
        }
    )

@router.put("/{category_id}", response_model=APIResponse)
async def update_category(
    category_id: int,
    category_update: CategoryUpdate,
    current_user: UserModel = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Update category (Admin only)."""
    try:
        updated_category = category_crud.update_category(db, category_id, category_update)
        if not updated_category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        
        return APIResponse(
            success=True,
            message="Category updated successfully",
            data={
                "id": updated_category.id,
                "name": updated_category.name,
                "description": updated_category.description,
                "is_active": updated_category.is_active,
                "updated_at": updated_category.updated_at.isoformat()
            }
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update category: {str(e)}"
        )

@router.delete("/{category_id}", response_model=APIResponse)
async def delete_category(
    category_id: int,
    hard_delete: bool = Query(False, description="Permanently delete category (use with caution)"),
    current_user: UserModel = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Delete category (Admin only). By default performs soft delete."""
    try:
        if hard_delete:
            success = category_crud.hard_delete_category(db, category_id)
            delete_type = "permanently deleted"
        else:
            success = category_crud.delete_category(db, category_id)
            delete_type = "deactivated"
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        
        return APIResponse(
            success=True,
            message=f"Category {delete_type} successfully",
            data={"id": category_id, "deleted": hard_delete}
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete category: {str(e)}"
        )
