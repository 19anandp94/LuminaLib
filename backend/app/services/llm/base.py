"""
Abstract base class for LLM providers.
This enables swapping LLM backends via dependency injection.
"""
from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """Abstract LLM provider interface."""

    @abstractmethod
    async def generate_summary(self, text: str, max_length: int = 500) -> str:
        """
        Generate a summary of the given text.
        
        Args:
            text: Text to summarize
            max_length: Maximum length of summary
            
        Returns:
            str: Generated summary
        """
        pass

    @abstractmethod
    async def analyze_sentiment(self, text: str) -> dict:
        """
        Analyze sentiment of the given text.
        
        Args:
            text: Text to analyze
            
        Returns:
            dict: Sentiment analysis result with 'score' (-1 to 1) and 'label'
        """
        pass

    @abstractmethod
    async def generate_consensus(self, reviews: list[str]) -> str:
        """
        Generate a consensus summary from multiple reviews.
        
        Args:
            reviews: List of review texts
            
        Returns:
            str: Consensus summary
        """
        pass

