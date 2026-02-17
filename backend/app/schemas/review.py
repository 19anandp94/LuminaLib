"""Review schemas."""
from datetime import datetime

from pydantic import BaseModel, Field


class ReviewCreate(BaseModel):
    """Schema for creating a review."""

    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5 stars")
    review_text: str | None = Field(None, description="Review text")


class Review(BaseModel):
    """Review schema for responses."""

    id: int
    user_id: int
    book_id: int
    rating: int
    review_text: str | None
    sentiment_score: float | None
    sentiment_label: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ReviewAnalysis(BaseModel):
    """Schema for aggregated review analysis."""

    book_id: int
    total_reviews: int
    average_rating: float
    sentiment_distribution: dict[str, int]
    consensus_summary: str | None
    last_updated: datetime | None

