
from dataclasses import dataclass

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.models.llm_req import LLMRequest


@dataclass
class AnalyticsSummary:
    total_requests: int
    total_actual_cost: float
    total_baseline_cost: float
    total_savings: float
    savings_percentage: float
    cache_hits: int
    cache_hit_rate: float
    routed_requests: int
    routing_rate: float
    average_provider_latency_ms: float


def get_analytics_summary(db: Session) -> AnalyticsSummary:
    result = db.execute(
        select(
            func.count(LLMRequest.id),
            func.coalesce(func.sum(LLMRequest.actual_cost), 0.0),
            func.coalesce(
                func.sum(LLMRequest.baseline_cost).filter(
                    LLMRequest.baseline_cost > 0
                ),
                0.0,
            ),
            func.coalesce(func.sum(LLMRequest.savings), 0.0),
            func.coalesce(
                func.sum(case((LLMRequest.cache_hit.is_(True), 1), else_=0)),
                0,
            ),
            func.coalesce(
                func.sum(case((LLMRequest.routed.is_(True), 1), else_=0)),
                0,
            ),
            func.coalesce(
                func.avg(LLMRequest.latency_ms).filter(
                    LLMRequest.cache_hit.is_(False)
                ),
                0.0,
            ),
        )
    ).one()

    (
        total_requests,
        total_actual_cost,
        total_baseline_cost,
        total_savings,
        cache_hits,
        routed_requests,
        average_provider_latency_ms,
    ) = result

    total_requests = int(total_requests)
    total_baseline_cost = float(total_baseline_cost)

    return AnalyticsSummary(
        total_requests=total_requests,
        total_actual_cost=float(total_actual_cost),
        total_baseline_cost=total_baseline_cost,
        total_savings=float(total_savings),
        savings_percentage=(
            float(total_savings) / total_baseline_cost * 100
            if total_baseline_cost > 0
            else 0.0
        ),
        cache_hits=int(cache_hits),
        cache_hit_rate=(
            int(cache_hits) / total_requests * 100
            if total_requests > 0
            else 0.0
        ),
        routed_requests=int(routed_requests),
        routing_rate=(
            int(routed_requests) / total_requests * 100
            if total_requests > 0
            else 0.0
        ),
        average_provider_latency_ms=float(
            average_provider_latency_ms
        ),
    )