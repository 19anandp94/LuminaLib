"""Recommendation routes."""
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import CurrentUser
from app.core.database import get_db
from app.schemas.book import Book as BookSchema
from app.services.recommendations import RecommendationEngine

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.get("", response_model=list[BookSchema])
async def get_recommendations(
    limit: int = 10,
    current_user: CurrentUser = None,
    db: Annotated[AsyncSession, Depends(get_db)] = None,
) -> list:
    """
    Get ML-based personalized book recommendations for the current user.
    
    Uses a hybrid approach combining content-based and collaborative filtering.
    """
    engine = RecommendationEngine(db)
    recommendations = await engine.get_recommendations(current_user.id, limit=limit)
    return recommendations

