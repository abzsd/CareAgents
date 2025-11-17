"""
FastAPI routes for User operations using PostgreSQL
"""
from fastapi import APIRouter, Depends, HTTPException, status
import asyncpg
from typing import Optional

from database.postgresql.connection import get_postgresql_pool
from services.user_service import UserService
from models.user import UserCreate, UserUpdate, UserResponse

router = APIRouter(prefix="/users", tags=["users"])


async def get_user_service(pool: asyncpg.Pool = Depends(get_postgresql_pool)) -> UserService:
    """Dependency to get user service"""
    return UserService(pool)


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreate,
    service: UserService = Depends(get_user_service)
):
    """
    Create a new user.

    Args:
        user: User data

    Returns:
        Created user
    """
    try:
        # Check if user already exists
        existing_user = await service.get_user_by_firebase_uid(user.firebase_uid)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this Firebase UID already exists"
            )
        
        return await service.create_user(user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(e)}"
        )


@router.get("/firebase/{firebase_uid}", response_model=UserResponse)
async def get_user_by_firebase_uid(
    firebase_uid: str,
    service: UserService = Depends(get_user_service)
):
    """
    Get a user by Firebase UID.

    Args:
        firebase_uid: Firebase Authentication UID

    Returns:
        User data
    """
    user = await service.get_user_by_firebase_uid(firebase_uid)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with Firebase UID {firebase_uid} not found"
        )
    return user


@router.get("/email/{email}", response_model=UserResponse)
async def get_user_by_email(
    email: str,
    service: UserService = Depends(get_user_service)
):
    """
    Get a user by email.

    Args:
        email: User email

    Returns:
        User data
    """
    user = await service.get_user_by_email(email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with email {email} not found"
        )
    return user


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: str,
    service: UserService = Depends(get_user_service)
):
    """
    Get a user by database ID.

    Args:
        user_id: User database ID

    Returns:
        User data
    """
    user = await service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    service: UserService = Depends(get_user_service)
):
    """
    Update a user.

    Args:
        user_id: User ID
        user_data: Updated user data

    Returns:
        Updated user
    """
    user = await service.update_user(user_id, user_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    return user


@router.put("/{user_id}/onboarded", response_model=UserResponse)
async def set_user_onboarded(
    user_id: str,
    service: UserService = Depends(get_user_service)
):
    """
    Mark user as onboarded.

    Args:
        user_id: User ID

    Returns:
        Updated user
    """
    user = await service.set_user_onboarded(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    return user


@router.put("/{user_id}/last-login", response_model=UserResponse)
async def update_last_login(
    user_id: str,
    service: UserService = Depends(get_user_service)
):
    """
    Update user's last login timestamp.

    Args:
        user_id: User ID

    Returns:
        Updated user
    """
    user = await service.update_last_login(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    return user
