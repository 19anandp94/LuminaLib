"""
LLM service factory for dependency injection.
Allows swapping LLM providers via configuration.
"""
from app.core.config import settings
from app.services.llm.base import LLMProvider
from app.services.llm.mock import MockLLMProvider
from app.services.llm.ollama import OllamaProvider
from app.services.llm.openai import OpenAIProvider


def get_llm_provider() -> LLMProvider:
    """
    Factory function to get the configured LLM provider.
    
    This enables swapping LLM backends by changing a single config line.
    
    Returns:
        LLMProvider: Configured LLM provider instance
    """
    provider = settings.llm_provider.lower()

    if provider == "ollama":
        return OllamaProvider(
            base_url=settings.ollama_base_url, model=settings.llm_model
        )
    elif provider == "openai":
        if not settings.openai_api_key:
            raise ValueError("OpenAI API key not configured")
        return OpenAIProvider(api_key=settings.openai_api_key, model=settings.llm_model)
    elif provider == "mock":
        return MockLLMProvider()
    else:
        raise ValueError(f"Unknown LLM provider: {provider}")


__all__ = ["LLMProvider", "get_llm_provider"]

