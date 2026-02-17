"""User preference model for ML-based recommendations."""
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ARRAY, DateTime, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class UserPreference(Base):
    """
    User preference model for ML-based recommendations.
    
    This model stores user reading preferences derived from their borrowing
    and review history. It's used by the recommendation engine to suggest
    relevant books.
    
    Design rationale:
    - favorite_genres: Array of genres the user frequently reads
    - favorite_authors: Array of authors the user enjoys
    - avg_rating_given: Average rating the user gives (helps identify harsh/lenient reviewers)
    - preferred_book_length: Preference for book length (short, medium, long)
    - reading_frequency: How often the user borrows books
    - genre_weights: JSONB storing genre preferences with weights for collaborative filtering
    - feature_vector: Array of floats representing user in latent feature space for matrix factorization
    """

    __tablename__ = "user_preferences"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True
    )
    
    # Content-based features
    favorite_genres: Mapped[list[str]] = mapped_column(
        ARRAY(String), default=list, nullable=False
    )
    favorite_authors: Mapped[list[str]] = mapped_column(
        ARRAY(String), default=list, nullable=False
    )
    avg_rating_given: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    
    # Behavioral features
    books_borrowed_count: Mapped[int] = mapped_column(default=0, nullable=False)
    books_reviewed_count: Mapped[int] = mapped_column(default=0, nullable=False)
    
    # Advanced ML features
    genre_weights: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    feature_vector: Mapped[list[float]] = mapped_column(
        ARRAY(Float), default=list, nullable=False
    )
    
    # Metadata
    last_updated: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="preferences")

    def __repr__(self) -> str:
        return f"<UserPreference(id={self.id}, user_id={self.user_id})>"

