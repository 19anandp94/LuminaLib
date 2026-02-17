"""Book schemas."""
from datetime import datetime

from pydantic import BaseModel, Field


class BookBase(BaseModel):
    """Base book schema."""

    title: str = Field(..., max_length=500)
    author: str = Field(..., max_length=255)
    isbn: str | None = Field(None, max_length=20)
    description: str | None = None
    published_year: int | None = None
    genre: str | None = Field(None, max_length=100)


class BookCreate(BookBase):
    """Schema for creating a book (metadata only, file uploaded separately)."""

    total_copies: int = Field(default=1, ge=1)


class BookUpdate(BaseModel):
    """Schema for updating book metadata."""

    title: str | None = Field(None, max_length=500)
    author: str | None = Field(None, max_length=255)
    isbn: str | None = Field(None, max_length=20)
    description: str | None = None
    published_year: int | None = None
    genre: str | None = Field(None, max_length=100)
    total_copies: int | None = Field(None, ge=1)


class Book(BookBase):
    """Book schema for responses."""

    id: int
    file_type: str
    file_size: int
    ai_summary: str | None = None
    summary_generated_at: datetime | None = None
    review_consensus: str | None = None
    total_copies: int
    available_copies: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BookList(BaseModel):
    """Schema for paginated book list."""

    items: list[Book]
    total: int
    page: int
    page_size: int
    pages: int

