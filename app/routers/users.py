from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas import User, UserListResponse, APIResponse
from app.crud.user import user_crud
from app.dependencies.auth import get_current_user, get_current_admin_user
from app.models import User as UserModel

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me", response_model=APIResponse)
async def get_current_user_info(
    current_user: UserModel = Depends(get_current_user)
):
    """Get current logged-in user details."""
    return APIResponse(
        success=True,
        message="User details retrieved successfully",
        data={
            "id": current_user.id,
            "email": current_user.email,
            "role": current_user.role,  # Already a string
            "created_at": current_user.created_at.isoformat(),
            "updated_at": current_user.updated_at.isoformat()
        }
    )

@router.get("/", response_model=UserListResponse)
async def list_users(
    skip: int = 0,
    limit: int = 100,
    current_user: UserModel = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """List all users (Admin only)."""
    try:
        users = user_crud.get_users(db, skip=skip, limit=limit)
        total_count = user_crud.get_users_count(db)
        
        users_data = []
        for user in users:
            users_data.append({
                "id": user.id,
                "email": user.email,
                "role": user.role,  # Already a string
                "created_at": user.created_at.isoformat(),
                "updated_at": user.updated_at.isoformat()
            })
        
        return UserListResponse(
            success=True,
            message=f"Retrieved {len(users)} users successfully",
            data=users_data,
            total=total_count
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve users: {str(e)}"
        )

@router.get("/{user_id}", response_model=APIResponse)
async def get_user_by_id(
    user_id: int,
    current_user: UserModel = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get user by ID (Admin only)."""
    user = user_crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return APIResponse(
        success=True,
        message="User details retrieved successfully",
        data={
            "id": user.id,
            "email": user.email,
            "role": user.role,  # Already a string
            "created_at": user.created_at.isoformat(),
            "updated_at": user.updated_at.isoformat()
        }
    )
