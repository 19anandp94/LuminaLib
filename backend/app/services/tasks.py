"""
Background task service for async processing.
Handles book summarization and review analysis asynchronously.
"""
import asyncio
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.models.book import Book
from app.models.review import Review
from app.services.llm import get_llm_provider
from app.services.storage import get_storage_provider


async def process_book_summarization(book_id: int) -> None:
    """
    Background task to generate book summary using LLM.
    
    Args:
        book_id: ID of the book to summarize
    """
    async with AsyncSessionLocal() as db:
        # Get book
        result = await db.execute(select(Book).where(Book.id == book_id))
        book = result.scalar_one_or_none()
        
        if not book:
            return
        
        try:
            # Download book content
            storage = get_storage_provider()
            content_bytes = await storage.download_file(book.file_path)
            
            # Extract text based on file type
            if book.file_type == "txt":
                content = content_bytes.decode("utf-8")
            elif book.file_type == "pdf":
                # For PDF, we'd use PyPDF2 or similar
                # Simplified for now
                content = content_bytes.decode("utf-8", errors="ignore")
            else:
                content = content_bytes.decode("utf-8", errors="ignore")
            
            # Generate summary using LLM
            llm = get_llm_provider()
            summary = await llm.generate_summary(content)
            
            # Update book with summary
            book.ai_summary = summary
            book.summary_generated_at = datetime.utcnow()
            await db.commit()
            
        except Exception as e:
            print(f"Error generating summary for book {book_id}: {e}")
            await db.rollback()


async def process_review_analysis(book_id: int) -> None:
    """
    Background task to analyze reviews and update consensus.
    
    Args:
        book_id: ID of the book whose reviews to analyze
    """
    async with AsyncSessionLocal() as db:
        # Get all reviews for the book
        result = await db.execute(
            select(Review).where(Review.book_id == book_id)
        )
        reviews = result.scalars().all()
        
        if not reviews:
            return
        
        try:
            llm = get_llm_provider()
            
            # Analyze sentiment for each review if not already done
            for review in reviews:
                if review.sentiment_score is None and review.review_text:
                    sentiment = await llm.analyze_sentiment(review.review_text)
                    review.sentiment_score = sentiment.get("score", 0.0)
                    review.sentiment_label = sentiment.get("label", "neutral")
            
            # Generate consensus from all reviews
            review_texts = [r.review_text for r in reviews if r.review_text]
            if review_texts:
                consensus = await llm.generate_consensus(review_texts)
                
                # Update book with consensus
                result = await db.execute(select(Book).where(Book.id == book_id))
                book = result.scalar_one_or_none()
                if book:
                    book.review_consensus = consensus
                    book.consensus_updated_at = datetime.utcnow()
            
            await db.commit()
            
        except Exception as e:
            print(f"Error analyzing reviews for book {book_id}: {e}")
            await db.rollback()


def schedule_book_summarization(book_id: int) -> None:
    """
    Schedule book summarization task.
    
    In production, this would use Celery or similar.
    For now, we run it in the background using asyncio.
    """
    asyncio.create_task(process_book_summarization(book_id))


def schedule_review_analysis(book_id: int) -> None:
    """
    Schedule review analysis task.
    
    In production, this would use Celery or similar.
    For now, we run it in the background using asyncio.
    """
    asyncio.create_task(process_review_analysis(book_id))

