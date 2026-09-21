import time

from anthropic import Anthropic

from app.core.config import get_settings
from app.providers.base import BaseProvider, ProviderResult
from app.schemas.chat import ChatCompletionRequest


class AnthropicProvider(BaseProvider):
    def __init__(self) -> None:
        settings = get_settings()
        self.client = Anthropic(api_key=settings.anthropic_api_key)

    def complete(
        self,
        request: ChatCompletionRequest,
    ) -> ProviderResult:
        started_at = time.perf_counter()

        system_messages = [
            message.content
            for message in request.messages
            if message.role == "system"
        ]

        messages = [
            {
                "role": message.role,
                "content": message.content,
            }
            for message in request.messages
            if message.role != "system"
        ]

        kwargs = {
            "model": request.model,
            "messages": messages,
            "max_tokens": request.max_tokens or 1024,
        }

        if system_messages:
            kwargs["system"] = "\n".join(system_messages)

        response = self.client.messages.create(**kwargs)

        latency_ms = round(
            (time.perf_counter() - started_at) * 1000
        )

        content = "".join(
            block.text
            for block in response.content
            if getattr(block, "type", None) == "text"
        )

        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens

        return ProviderResult(
            provider="anthropic",
            model=response.model,
            content=content,
            prompt_tokens=input_tokens,
            completion_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens,
            latency_ms=latency_ms,
            finish_reason=response.stop_reason or "stop",
        )