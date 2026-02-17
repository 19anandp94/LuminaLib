"""OpenAI LLM provider implementation."""
import json

import httpx

from app.services.llm.base import LLMProvider


class OpenAIProvider(LLMProvider):
    """OpenAI LLM implementation."""

    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        """
        Initialize OpenAI provider.
        
        Args:
            api_key: OpenAI API key
            model: Model name
        """
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.openai.com/v1"

    async def _chat_completion(self, messages: list[dict]) -> str:
        """Internal method to call OpenAI chat completion."""
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={"model": self.model, "messages": messages},
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]

    async def generate_summary(self, text: str, max_length: int = 500) -> str:
        """Generate a summary using OpenAI."""
        max_input = 4000
        if len(text) > max_input:
            text = text[:max_input] + "..."

        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant that summarizes books concisely.",
            },
            {
                "role": "user",
                "content": f"Summarize the following book content in approximately {max_length} characters:\n\n{text}",
            },
        ]

        return await self._chat_completion(messages)

    async def analyze_sentiment(self, text: str) -> dict:
        """Analyze sentiment using OpenAI."""
        messages = [
            {
                "role": "system",
                "content": "You analyze sentiment and respond only with JSON.",
            },
            {
                "role": "user",
                "content": f"Analyze sentiment of this review. Respond with JSON containing 'score' (-1 to 1) and 'label' (positive/neutral/negative):\n\n{text}",
            },
        ]

        response = await self._chat_completion(messages)
        return json.loads(response)

    async def generate_consensus(self, reviews: list[str]) -> str:
        """Generate consensus from reviews using OpenAI."""
        reviews_text = "\n\n".join([f"Review {i+1}: {r}" for i, r in enumerate(reviews)])

        messages = [
            {
                "role": "system",
                "content": "You analyze book reviews and generate consensus summaries.",
            },
            {
                "role": "user",
                "content": f"Generate a consensus summary (2-3 sentences) from these reviews:\n\n{reviews_text}",
            },
        ]

        return await self._chat_completion(messages)

