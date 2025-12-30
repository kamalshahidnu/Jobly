"""Authentication API routes."""

from fastapi import APIRouter, HTTPException, Depends, status
from typing import Dict, Any
from ...auth.models import UserCreate, UserLogin, Token, UserResponse
from ...auth.jwt_handler import create_access_token, get_current_user
from ...services.user_service import UserService
from datetime import datetime

router = APIRouter(prefix="/auth", tags=["authentication"])

# Initialize user service
user_service = UserService()


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    """Register a new user.

    Args:
        user_data: User registration data

    Returns:
        Access token and user information

    Raises:
        HTTPException: If email already exists
    """
    try:
        user = user_service.create_user(user_data)

        # Create access token
        access_token = create_access_token(
            data={"sub": user.user_id, "email": user.email}
        )

        return Token(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse(
                user_id=user.user_id,
                email=user.email,
                name=user.name,
                phone=user.phone,
                created_at=user.created_at
            )
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin):
    """Authenticate a user and return access token.

    Args:
        credentials: User login credentials

    Returns:
        Access token and user information

    Raises:
        HTTPException: If credentials are invalid
    """
    user = user_service.authenticate_user(credentials.email, credentials.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token = create_access_token(
        data={"sub": user.user_id, "email": user.email}
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            user_id=user.user_id,
            email=user.email,
            name=user.name,
            phone=user.phone,
            created_at=user.created_at
        )
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get current user information.

    Args:
        current_user: Current authenticated user from token

    Returns:
        User information

    Raises:
        HTTPException: If user not found
    """
    user = user_service.get_user_by_id(current_user["sub"])

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return UserResponse(
        user_id=user.user_id,
        email=user.email,
        name=user.name,
        phone=user.phone,
        created_at=user.created_at
    )


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    updates: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Update current user information.

    Args:
        updates: Fields to update
        current_user: Current authenticated user from token

    Returns:
        Updated user information

    Raises:
        HTTPException: If update fails
    """
    user = user_service.update_user(current_user["sub"], updates)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return UserResponse(
        user_id=user.user_id,
        email=user.email,
        name=user.name,
        phone=user.phone,
        created_at=user.created_at
    )


@router.post("/change-password")
async def change_password(
    old_password: str,
    new_password: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Change user password.

    Args:
        old_password: Current password
        new_password: New password
        current_user: Current authenticated user from token

    Returns:
        Success message

    Raises:
        HTTPException: If password change fails
    """
    success = user_service.change_password(
        current_user["sub"],
        old_password,
        new_password
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to change password. Check your current password."
        )

    return {"message": "Password changed successfully"}


@router.delete("/me")
async def deactivate_account(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Deactivate current user account.

    Args:
        current_user: Current authenticated user from token

    Returns:
        Success message

    Raises:
        HTTPException: If deactivation fails
    """
    success = user_service.deactivate_user(current_user["sub"])

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to deactivate account"
        )

    return {"message": "Account deactivated successfully"}
