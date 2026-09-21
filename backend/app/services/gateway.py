from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.core.exceptions import TokenBudgetExceededError
from app.providers.base import ProviderResult
from app.providers.factory import ProviderFactory
from app.schemas.chat import ChatCompletionRequest
from app.services.cache import SemanticCache
from app.services.logger import save_llm_request
from app.services.metrics import calculate_cost
from app.services.router import SmartRouter
from app.services.savings import calculate_savings
from app.services.token_guard import TokenGuard


shared_cache = SemanticCache()


@dataclass
class GatewayResult:
    request_id: int
    provider_result: ProviderResult
    estimated_cost: float
    actual_cost: float
    baseline_cost: float
    savings: float
    savings_percentage: float
    routed: bool
    cache_hit: bool


class GatewayService:
    def __init__(
        self,
        max_request_cost: float = 0.01,
    ) -> None:
        self.router = SmartRouter()
        self.token_guard = TokenGuard(
            max_request_cost=max_request_cost
        )
        self.cache = shared_cache

    def complete(
        self,
        request: ChatCompletionRequest,
        db: Session,
    ) -> GatewayResult:
        routing_decision = self.router.route(request)

        token_guard_result = self.token_guard.check(
            request=request,
            model=routing_decision.selected_model,
        )

        if not token_guard_result.allowed:
            raise TokenBudgetExceededError(
                token_guard_result.reason
            )

        routed_request = request.model_copy(
            update={
                "model": routing_decision.selected_model,
            }
        )

        cache_result = self.cache.lookup(
            request=routed_request,
            model=routing_decision.selected_model,
        )

        if cache_result.hit and cache_result.entry is not None:
            entry = cache_result.entry

            provider_result = ProviderResult(
                provider=routing_decision.provider,
                model=entry.model,
                content=entry.content,
                prompt_tokens=entry.prompt_tokens,
                completion_tokens=entry.completion_tokens,
                total_tokens=entry.total_tokens,
                latency_ms=0,
                finish_reason=entry.finish_reason,
            )

            savings_metrics = calculate_savings(
                requested_model=request.model,
                executed_model=entry.model,
                prompt_tokens=entry.prompt_tokens,
                completion_tokens=entry.completion_tokens,
            )

            record = save_llm_request(
                db=db,
                request=routed_request,
                result=provider_result,
                estimated_cost=0.0,
                actual_cost=0.0,
                requested_model=request.model,
                baseline_cost=savings_metrics.baseline_cost,
                savings=savings_metrics.baseline_cost,
                savings_percentage=(
                    100.0
                    if savings_metrics.baseline_cost > 0
                    else 0.0
                ),
                routed=routing_decision.routed,
                cache_hit=True,
            )

            return GatewayResult(
                request_id=record.id,
                provider_result=provider_result,
                estimated_cost=0.0,
                actual_cost=0.0,
                baseline_cost=savings_metrics.baseline_cost,
                savings=savings_metrics.baseline_cost,
                savings_percentage=(
                    100.0
                    if savings_metrics.baseline_cost > 0
                    else 0.0
                ),
                routed=routing_decision.routed,
                cache_hit=True,
            )

        provider = ProviderFactory.get(
            routing_decision.provider
        )

        provider_result = provider.complete(
            routed_request
        )

        cost_metrics = calculate_cost(
            model=provider_result.model,
            prompt_tokens=provider_result.prompt_tokens,
            completion_tokens=provider_result.completion_tokens,
        )

        savings_metrics = calculate_savings(
            requested_model=request.model,
            executed_model=provider_result.model,
            prompt_tokens=provider_result.prompt_tokens,
            completion_tokens=provider_result.completion_tokens,
        )

        self.cache.store(
            request=routed_request,
            model=provider_result.model,
            content=provider_result.content,
            prompt_tokens=provider_result.prompt_tokens,
            completion_tokens=provider_result.completion_tokens,
            total_tokens=provider_result.total_tokens,
            finish_reason=provider_result.finish_reason,
        )

        record = save_llm_request(
            db=db,
            request=routed_request,
            result=provider_result,
            estimated_cost=cost_metrics.estimated_cost,
            actual_cost=cost_metrics.actual_cost,
            requested_model=request.model,
            baseline_cost=savings_metrics.baseline_cost,
            savings=savings_metrics.savings,
            savings_percentage=savings_metrics.savings_percentage,
            routed=routing_decision.routed,
            cache_hit=False,
        )

        return GatewayResult(
            request_id=record.id,
            provider_result=provider_result,
            estimated_cost=cost_metrics.estimated_cost,
            actual_cost=cost_metrics.actual_cost,
            baseline_cost=savings_metrics.baseline_cost,
            savings=savings_metrics.savings,
            savings_percentage=savings_metrics.savings_percentage,
            routed=routing_decision.routed,
            cache_hit=False,
        )