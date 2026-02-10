"""OpenRouter LLM provider."""

import httpx
from typing import List, Dict, Any, Optional, AsyncGenerator
import structlog
from config.settings import settings

logger = structlog.get_logger()


class OpenRouterProvider:
    """OpenRouter API provider for LLM interactions."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """Initialize OpenRouter provider."""
        self.api_key = api_key or settings.api_keys.openrouter
        self.base_url = settings.openrouter_base_url
        self.model = model or settings.default_model

        if not self.api_key:
            raise ValueError("OpenRouter API key not configured")

        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": "https://github.com/stockanalyzer",
                "X-Title": "Stock Analyzer Pro"
            },
            timeout=60.0
        )

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        stream: bool = False
    ) -> Dict[str, Any]:
        """Get chat completion from OpenRouter."""
        try:
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": stream
            }

            response = await self.client.post("/chat/completions", json=payload)
            response.raise_for_status()

            return response.json()

        except httpx.HTTPError as e:
            logger.error(f"OpenRouter API error: {e}")
            raise

    async def chat_completion_stream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> AsyncGenerator[str, None]:
        """Get streaming chat completion from OpenRouter."""
        try:
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": True
            }

            async with self.client.stream("POST", "/chat/completions", json=payload) as response:
                response.raise_for_status()

                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]  # Remove "data: " prefix

                        if data == "[DONE]":
                            break

                        try:
                            import json
                            chunk = json.loads(data)
                            if "choices" in chunk and len(chunk["choices"]) > 0:
                                delta = chunk["choices"][0].get("delta", {})
                                if "content" in delta:
                                    yield delta["content"]
                        except json.JSONDecodeError:
                            continue

        except httpx.HTTPError as e:
            logger.error(f"OpenRouter streaming error: {e}")
            raise

    async def function_call(
        self,
        messages: List[Dict[str, str]],
        functions: List[Dict[str, Any]],
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """Get chat completion with function calling."""
        try:
            payload = {
                "model": self.model,
                "messages": messages,
                "functions": functions,
                "function_call": "auto",
                "temperature": temperature
            }

            response = await self.client.post("/chat/completions", json=payload)
            response.raise_for_status()

            return response.json()

        except httpx.HTTPError as e:
            logger.error(f"OpenRouter function call error: {e}")
            raise

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    def set_model(self, model: str):
        """Change the model being used."""
        self.model = model
        logger.info(f"Switched to model: {model}")

    @staticmethod
    def get_available_models() -> List[str]:
        """Get list of popular models available on OpenRouter."""
        return [
            "xiaomi/mimo-v2-flash:free",
            "google/gemini-flash-1.5:free",
            "meta-llama/llama-3.2-3b-instruct:free",
            "anthropic/claude-3.5-sonnet",
            "anthropic/claude-3-opus",
            "openai/gpt-4-turbo",
            "openai/gpt-4",
            "openai/gpt-3.5-turbo",
            "meta-llama/llama-3.1-70b-instruct",
            "google/gemini-pro",
            "mistralai/mixtral-8x7b-instruct"
        ]
