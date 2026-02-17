"""User schemas."""
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user schema."""

    email: EmailStr
    username: str
    full_name: str | None = None


class User(UserBase):
    """User schema for responses."""

    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserProfile(User):
    """Extended user profile schema."""

    updated_at: datetime
    books_borrowed_count: int = 0
    books_reviewed_count: int = 0

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """Schema for updating user profile."""

    full_name: str | None = Field(None, max_length=255)
    email: EmailStr | None = None

