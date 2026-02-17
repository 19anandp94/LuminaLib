"""Review management routes."""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import CurrentUser
from app.core.database import get_db
from app.models.book import Book
from app.models.borrow import BorrowRecord
from app.models.review import Review
from app.schemas.review import Review as ReviewSchema
from app.schemas.review import ReviewAnalysis, ReviewCreate
from app.services.recommendations import RecommendationEngine
from app.services.tasks import schedule_review_analysis

router = APIRouter(prefix="/books/{book_id}/reviews", tags=["Reviews"])


@router.post("", response_model=ReviewSchema, status_code=status.HTTP_201_CREATED)
async def create_review(
    book_id: int,
    review_data: ReviewCreate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Review:
    """
    Submit a review for a book.
    
    Users can only review books they have borrowed.
    Triggers async sentiment analysis and consensus update.
    """
    # Check if book exists
    book_result = await db.execute(select(Book).where(Book.id == book_id))
    book = book_result.scalar_one_or_none()
    
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found",
        )
    
    # Check if user has borrowed this book
    borrow_result = await db.execute(
        select(BorrowRecord)
        .where(BorrowRecord.user_id == current_user.id)
        .where(BorrowRecord.book_id == book_id)
    )
    if not borrow_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only review books you have borrowed",
        )
    
    # Check if user already reviewed this book
    existing_review = await db.execute(
        select(Review)
        .where(Review.user_id == current_user.id)
        .where(Review.book_id == book_id)
    )
    if existing_review.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already reviewed this book",
        )
    
    # Create review
    review = Review(
        user_id=current_user.id,
        book_id=book_id,
        rating=review_data.rating,
        review_text=review_data.review_text,
    )
    
    db.add(review)
    await db.commit()
    await db.refresh(review)
    
    # Update user preferences
    engine = RecommendationEngine(db)
    await engine.update_user_preferences(current_user.id)
    
    # Schedule async review analysis
    schedule_review_analysis(book_id)
    
    return review


@router.get("", response_model=list[ReviewSchema])
async def list_reviews(
    book_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[Review]:
    """Get all reviews for a book."""
    result = await db.execute(
        select(Review)
        .where(Review.book_id == book_id)
        .order_by(Review.created_at.desc())
    )
    return result.scalars().all()


@router.get("/analysis", response_model=ReviewAnalysis)
async def get_review_analysis(
    book_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ReviewAnalysis:
    """
    Get GenAI-aggregated analysis of all reviews for a book.
    """
    # Get book
    book_result = await db.execute(select(Book).where(Book.id == book_id))
    book = book_result.scalar_one_or_none()
    
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found",
        )
    
    # Get review statistics
    reviews_result = await db.execute(
        select(Review).where(Review.book_id == book_id)
    )
    reviews = reviews_result.scalars().all()
    
    total_reviews = len(reviews)
    avg_rating = sum(r.rating for r in reviews) / total_reviews if total_reviews > 0 else 0.0
    
    # Sentiment distribution
    sentiment_dist = {"positive": 0, "neutral": 0, "negative": 0}
    for review in reviews:
        if review.sentiment_label:
            sentiment_dist[review.sentiment_label] = sentiment_dist.get(review.sentiment_label, 0) + 1
    
    return ReviewAnalysis(
        book_id=book_id,
        total_reviews=total_reviews,
        average_rating=avg_rating,
        sentiment_distribution=sentiment_dist,
        consensus_summary=book.review_consensus,
        last_updated=book.consensus_updated_at,
    )

