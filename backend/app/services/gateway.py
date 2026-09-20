from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.providers.base import ProviderResult
from app.providers.openai_provider import OpenAIProvider
from app.schemas.chat import ChatCompletionRequest
from app.services.logger import save_llm_request
from app.services.metrics import calculate_cost


@dataclass
class GatewayResult:
    request_id: int
    provider_result: ProviderResult
    estimated_cost: float
    actual_cost: float


class GatewayService:
    def __init__(self) -> None:
        self.openai_provider = OpenAIProvider()

    def complete(
        self,
        request: ChatCompletionRequest,
        db: Session,
    ) -> GatewayResult:
        provider_result = self.openai_provider.complete(request)

        cost_metrics = calculate_cost(
            model=provider_result.model,
            prompt_tokens=provider_result.prompt_tokens,
            completion_tokens=provider_result.completion_tokens,
        )

        record = save_llm_request(
            db=db,
            request=request,
            result=provider_result,
            estimated_cost=cost_metrics.estimated_cost,
            actual_cost=cost_metrics.actual_cost,
        )

        return GatewayResult(
            request_id=record.id,
            provider_result=provider_result,
            estimated_cost=cost_metrics.estimated_cost,
            actual_cost=cost_metrics.actual_cost,
        )