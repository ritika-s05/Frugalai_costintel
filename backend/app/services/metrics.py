from dataclasses import dataclass


@dataclass
class CostMetrics:
    estimated_cost: float
    actual_cost: float


def calculate_cost(
    model: str,
    prompt_tokens: int,
    completion_tokens: int,
) -> CostMetrics:
    """
    Cost calculation will use provider pricing configuration later.

    For Phase 2, the gateway records token usage and latency while
    cost values remain zero until the pricing registry is introduced.
    """
    return CostMetrics(
        estimated_cost=0.0,
        actual_cost=0.0,
    )