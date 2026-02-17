"""Ollama LLM provider implementation."""
import httpx

from app.services.llm.base import LLMProvider


class OllamaProvider(LLMProvider):
    """Ollama LLM implementation for local models."""

    def __init__(self, base_url: str, model: str):
        """
        Initialize Ollama provider.
        
        Args:
            base_url: Ollama server base URL
            model: Model name (e.g., 'llama3')
        """
        self.base_url = base_url.rstrip("/")
        self.model = model

    async def _generate(self, prompt: str) -> str:
        """Internal method to generate text from Ollama."""
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.base_url}/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": False},
            )
            response.raise_for_status()
            return response.json()["response"]

    async def generate_summary(self, text: str, max_length: int = 500) -> str:
        """Generate a summary using Ollama."""
        # Truncate text if too long to avoid context limits
        max_input = 4000
        if len(text) > max_input:
            text = text[:max_input] + "..."

        prompt = f"""Summarize the following book content in approximately {max_length} characters. 
Focus on the main themes, plot, and key takeaways. Be concise and informative.

Book content:
{text}

Summary:"""

        return await self._generate(prompt)

    async def analyze_sentiment(self, text: str) -> dict:
        """Analyze sentiment using Ollama."""
        prompt = f"""Analyze the sentiment of the following review. 
Respond with ONLY a JSON object containing 'score' (a number from -1 to 1, where -1 is very negative, 0 is neutral, and 1 is very positive) and 'label' (one of: 'positive', 'neutral', 'negative').

Review:
{text}

JSON response:"""

        response = await self._generate(prompt)
        
        # Parse the response - extract JSON
        try:
            import json
            # Try to find JSON in the response
            start = response.find("{")
            end = response.rfind("}") + 1
            if start != -1 and end > start:
                result = json.loads(response[start:end])
                return result
        except Exception:
            pass
        
        # Fallback: simple heuristic
        text_lower = text.lower()
        if any(word in text_lower for word in ["excellent", "amazing", "love", "great"]):
            return {"score": 0.8, "label": "positive"}
        elif any(word in text_lower for word in ["terrible", "awful", "hate", "bad"]):
            return {"score": -0.8, "label": "negative"}
        else:
            return {"score": 0.0, "label": "neutral"}

    async def generate_consensus(self, reviews: list[str]) -> str:
        """Generate consensus from reviews using Ollama."""
        reviews_text = "\n\n".join([f"Review {i+1}: {r}" for i, r in enumerate(reviews)])
        
        prompt = f"""Analyze the following book reviews and generate a consensus summary. 
Highlight common themes, overall sentiment, and key points that multiple reviewers mentioned.
Keep it concise (2-3 sentences).

{reviews_text}

Consensus summary:"""

        return await self._generate(prompt)

