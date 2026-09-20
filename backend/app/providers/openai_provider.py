import time
from typing import Any

from openai import OpenAI

from app.core.config import get_settings
from app.providers.base import BaseProvider, ProviderResult
from app.schemas.chat import ChatCompletionRequest


class OpenAIProvider(BaseProvider):
    def __init__(self) -> None:
        settings = get_settings()
        self.client = OpenAI(api_key=settings.openai_api_key)

    def complete(
        self,
        request: ChatCompletionRequest,
    ) -> ProviderResult:
        started_at = time.perf_counter()

        request_kwargs: dict[str, Any] = {
            "model": request.model,
            "messages": [
                message.model_dump()
                for message in request.messages
            ],
            "temperature": request.temperature,
        }

        if request.max_tokens is not None:
            request_kwargs["max_tokens"] = request.max_tokens

        completion = self.client.chat.completions.create(
            **request_kwargs
        )

        latency_ms = round(
            (time.perf_counter() - started_at) * 1000
        )

        choice = completion.choices[0]
        usage = completion.usage

        return ProviderResult(
            provider="openai",
            model=completion.model,
            content=choice.message.content or "",
            prompt_tokens=usage.prompt_tokens if usage else 0,
            completion_tokens=usage.completion_tokens if usage else 0,
            total_tokens=usage.total_tokens if usage else 0,
            latency_ms=latency_ms,
            finish_reason=choice.finish_reason or "stop",
        )