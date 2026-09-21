import time

from google import genai
from google.genai import types  # pyright: ignore[reportMissingImports]

from app.core.config import get_settings
from app.providers.base import BaseProvider, ProviderResult
from app.schemas.chat import ChatCompletionRequest


class GeminiProvider(BaseProvider):
    def __init__(self) -> None:
        settings = get_settings()
        self.client = genai.Client(api_key=settings.gemini_api_key)

    def complete(
        self,
        request: ChatCompletionRequest,
    ) -> ProviderResult:
        started_at = time.perf_counter()

        # Convert our OpenAI-style messages into a single prompt
        prompt = "\n".join(
            f"{message.role}: {message.content}"
            for message in request.messages
        )

        config = types.GenerateContentConfig(
            temperature=request.temperature,
            max_output_tokens=request.max_tokens,
        )

        response = self.client.models.generate_content(
            model=request.model,
            contents=prompt,
            config=config,
        )

        latency_ms = round(
            (time.perf_counter() - started_at) * 1000
        )

        usage = response.usage_metadata

        prompt_tokens = (
            usage.prompt_token_count
            if usage and usage.prompt_token_count
            else 0
        )

        completion_tokens = (
            usage.candidates_token_count
            if usage and usage.candidates_token_count
            else 0
        )

        total_tokens = prompt_tokens + completion_tokens

        return ProviderResult(
            provider="gemini",
            model=request.model,
            content=response.text or "",
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            latency_ms=latency_ms,
            finish_reason="stop",
        )