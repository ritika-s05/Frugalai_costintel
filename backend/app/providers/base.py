from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.schemas.chat import ChatCompletionRequest


@dataclass
class ProviderResult:
    provider: str
    model: str
    content: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    latency_ms: int
    finish_reason: str


class BaseProvider(ABC):
    @abstractmethod
    def complete(
        self,
        request: ChatCompletionRequest,
    ) -> ProviderResult:
        raise NotImplementedError