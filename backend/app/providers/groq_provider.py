import time

from groq import Groq

from app.core.config import get_settings
from app.providers.base import BaseProvider, ProviderResult
from app.schemas.chat import ChatCompletionRequest


class GroqProvider(BaseProvider):
    def __init__(self) -> None:
        settings = get_settings()
        self.client = Groq(api_key=settings.groq_api_key)

    def complete(
        self,
        request: ChatCompletionRequest,
    ) -> ProviderResult:
        started_at = time.perf_counter()

        completion = self.client.chat.completions.create(
            model=request.model,
            messages=[
                message.model_dump()
                for message in request.messages
            ],
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )

        latency_ms = round(
            (time.perf_counter() - started_at) * 1000
        )

        choice = completion.choices[0]
        usage = completion.usage

        return ProviderResult(
            provider="groq",
            model=completion.model,
            content=choice.message.content or "",
            prompt_tokens=usage.prompt_tokens if usage else 0,
            completion_tokens=usage.completion_tokens if usage else 0,
            total_tokens=usage.total_tokens if usage else 0,
            latency_ms=latency_ms,
            finish_reason=choice.finish_reason or "stop",
        )