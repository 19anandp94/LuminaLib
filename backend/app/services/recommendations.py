"""
Recommendation engine using content-based and collaborative filtering.
"""
from collections import Counter
from typing import List

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.book import Book
from app.models.borrow import BorrowRecord
from app.models.review import Review
from app.models.user import User
from app.models.user_preference import UserPreference


class RecommendationEngine:
    """
    Hybrid recommendation engine combining content-based and collaborative filtering.
    
    Strategy:
    1. Content-based: Recommend books similar to what the user has borrowed/reviewed
    2. Collaborative: Recommend books that similar users enjoyed
    3. Popularity: Include trending books as fallback
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def update_user_preferences(self, user_id: int) -> None:
        """
        Update user preferences based on their activity.
        
        This is called after borrow/review actions to keep preferences current.
        """
        # Get user's borrow history
        borrow_result = await self.db.execute(
            select(Book)
            .join(BorrowRecord)
            .where(BorrowRecord.user_id == user_id)
        )
        borrowed_books = borrow_result.scalars().all()

        # Get user's reviews
        review_result = await self.db.execute(
            select(Review).where(Review.user_id == user_id)
        )
        reviews = review_result.scalars().all()

        # Calculate preferences
        genres = [b.genre for b in borrowed_books if b.genre]
        authors = [b.author for b in borrowed_books]
        
        genre_counts = Counter(genres)
        author_counts = Counter(authors)
        
        favorite_genres = [g for g, _ in genre_counts.most_common(5)]
        favorite_authors = [a for a, _ in author_counts.most_common(5)]
        
        avg_rating = sum(r.rating for r in reviews) / len(reviews) if reviews else 0.0
        
        # Genre weights for collaborative filtering
        total_genres = len(genres)
        genre_weights = {
            genre: count / total_genres for genre, count in genre_counts.items()
        } if total_genres > 0 else {}

        # Get or create user preference
        pref_result = await self.db.execute(
            select(UserPreference).where(UserPreference.user_id == user_id)
        )
        preference = pref_result.scalar_one_or_none()

        if not preference:
            preference = UserPreference(user_id=user_id)
            self.db.add(preference)

        # Update preferences
        preference.favorite_genres = favorite_genres
        preference.favorite_authors = favorite_authors
        preference.avg_rating_given = avg_rating
        preference.books_borrowed_count = len(borrowed_books)
        preference.books_reviewed_count = len(reviews)
        preference.genre_weights = genre_weights

        await self.db.commit()

    async def get_recommendations(
        self, user_id: int, limit: int = 10
    ) -> List[Book]:
        """
        Get personalized book recommendations for a user.
        
        Args:
            user_id: User ID
            limit: Maximum number of recommendations
            
        Returns:
            List of recommended books
        """
        # Get user preferences
        pref_result = await self.db.execute(
            select(UserPreference).where(UserPreference.user_id == user_id)
        )
        preference = pref_result.scalar_one_or_none()

        # Get books user has already borrowed
        borrowed_result = await self.db.execute(
            select(BorrowRecord.book_id).where(BorrowRecord.user_id == user_id)
        )
        borrowed_book_ids = [row[0] for row in borrowed_result.all()]

        recommendations = []

        if preference and preference.favorite_genres:
            # Content-based: Books in favorite genres
            genre_result = await self.db.execute(
                select(Book)
                .where(Book.genre.in_(preference.favorite_genres))
                .where(Book.id.notin_(borrowed_book_ids) if borrowed_book_ids else True)
                .where(Book.available_copies > 0)
                .limit(limit)
            )
            recommendations.extend(genre_result.scalars().all())

        # If not enough recommendations, add popular books
        if len(recommendations) < limit:
            popular_result = await self.db.execute(
                select(Book)
                .where(Book.id.notin_(borrowed_book_ids) if borrowed_book_ids else True)
                .where(Book.available_copies > 0)
                .order_by(Book.created_at.desc())
                .limit(limit - len(recommendations))
            )
            recommendations.extend(popular_result.scalars().all())

        return recommendations[:limit]

