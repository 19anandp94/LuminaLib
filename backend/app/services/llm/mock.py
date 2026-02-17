"""Mock LLM provider for testing."""
from app.services.llm.base import LLMProvider


class MockLLMProvider(LLMProvider):
    """Mock LLM implementation for testing without actual LLM."""

    async def generate_summary(self, text: str, max_length: int = 500) -> str:
        """Generate a mock summary."""
        words = text.split()[:50]
        return f"[Mock Summary] {' '.join(words)}..."

    async def analyze_sentiment(self, text: str) -> dict:
        """Analyze sentiment with simple heuristics."""
        text_lower = text.lower()
        
        positive_words = ["excellent", "amazing", "love", "great", "wonderful", "fantastic"]
        negative_words = ["terrible", "awful", "hate", "bad", "horrible", "disappointing"]
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return {"score": 0.7, "label": "positive"}
        elif negative_count > positive_count:
            return {"score": -0.7, "label": "negative"}
        else:
            return {"score": 0.0, "label": "neutral"}

    async def generate_consensus(self, reviews: list[str]) -> str:
        """Generate a mock consensus."""
        return f"[Mock Consensus] Based on {len(reviews)} reviews, readers generally have mixed opinions about this book."

