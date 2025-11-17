import uuid
from datetime import datetime
import asyncpg
from typing import Optional, List
from models.user import UserCreate, UserUpdate, UserResponse, UserRole
from database.postgresql.repository import BaseRepository


class UserRepository(BaseRepository):
    """Repository for user operations"""

    def __init__(self, pool: asyncpg.Pool):
        super().__init__(pool, "users")

    async def find_by_email(self, email: str) -> Optional[dict]:
        """Find user by email"""
        results = await self.find_by_filter({"email": email, "is_active": True}, limit=1)
        return results[0] if results else None

    async def find_by_firebase_uid(self, firebase_uid: str) -> Optional[dict]:
        """Find user by Firebase UID"""
        results = await self.find_by_filter({"firebase_uid": firebase_uid, "is_active": True}, limit=1)
        return results[0] if results else None


class UserService:
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool
        self.repository = UserRepository(pool)

    async def create_user(self, user_data: UserCreate) -> UserResponse:
        """Create a new user in PostgreSQL"""
        try:
            # Convert user data to dictionary
            user_dict = {
                "user_id": str(uuid.uuid4()),
                "email": user_data.email,
                "display_name": user_data.display_name,
                "photo_url": user_data.photo_url,
                "role": user_data.role.value if user_data.role else "patient",
                "is_onboarded": user_data.is_onboarded,
                "firebase_uid": user_data.firebase_uid,
                "provider_id": user_data.provider_id,
                "is_active": True
            }
            
            # Use repository pattern for insertion
            inserted_data = await self.repository.insert(user_dict)
            
            # Convert role for response
            inserted_data["role"] = UserRole(inserted_data["role"])
            
            return UserResponse(**inserted_data)
        except Exception as e:
            raise Exception(f"Failed to insert user: {str(e)}")

    async def get_user_by_firebase_uid(self, firebase_uid: str) -> Optional[UserResponse]:
        """Get user by Firebase UID"""
        try:
            user_data = await self.repository.find_by_firebase_uid(firebase_uid)
            if user_data:
                user_data["role"] = UserRole(user_data["role"])
                return UserResponse(**user_data)
            return None
        except Exception as e:
            print(f"Error fetching user by Firebase UID: {e}")
            return None

    async def get_user_by_email(self, email: str) -> Optional[UserResponse]:
        """Get user by email"""
        try:
            user_data = await self.repository.find_by_email(email)
            if user_data:
                user_data["role"] = UserRole(user_data["role"])
                return UserResponse(**user_data)
            return None
        except Exception as e:
            print(f"Error fetching user by email: {e}")
            return None

    async def get_user_by_id(self, user_id: str) -> Optional[UserResponse]:
        """Get user by database ID"""
        try:
            user_data = await self.repository.find_by_id("user_id", user_id)
            if user_data and user_data.get("is_active", True):
                user_data["role"] = UserRole(user_data["role"])
                return UserResponse(**user_data)
            return None
        except Exception as e:
            print(f"Error fetching user by ID: {e}")
            return None

    async def update_user(self, user_id: str, user_data: UserUpdate) -> Optional[UserResponse]:
        """Update user information"""
        try:
            # Check if user exists
            existing_user = await self.get_user_by_id(user_id)
            if not existing_user:
                return None
            
            # Convert user_data to dictionary, excluding unset fields
            update_fields = user_data.dict(exclude_unset=True)
            
            # Convert role enum to string if present
            if "role" in update_fields and isinstance(update_fields["role"], UserRole):
                update_fields["role"] = update_fields["role"].value
            
            # Use repository pattern for update
            await self.repository.update("user_id", user_id, update_fields)
            
            # Return updated user
            return await self.get_user_by_id(user_id)
        except Exception as e:
            print(f"Error updating user: {e}")
            return None

    async def update_last_login(self, user_id: str) -> Optional[UserResponse]:
        """Update user's last login timestamp"""
        return await self.update_user(user_id, UserUpdate(last_login_at=datetime.utcnow()))

    async def set_user_onboarded(self, user_id: str) -> Optional[UserResponse]:
        """Mark user as onboarded"""
        return await self.update_user(user_id, UserUpdate(is_onboarded=True))
