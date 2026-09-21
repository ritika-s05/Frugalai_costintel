from dataclasses import dataclass
from app.core.model_registry import MODEL_REGISTRY

@dataclass
class CostMetrics:
    estimated_cost: float
    actual_cost: float


def calculate_cost(
    model: str,
    prompt_tokens: int,
    completion_tokens: int,
) -> CostMetrics:
    model_config = MODEL_REGISTRY.get(model)

    if model_config is None:
        raise ValueError(
            f"Pricing information not found for model: {model}"
        )

    input_cost = (
        prompt_tokens / 1_000_000
    ) * model_config.input_cost_per_1m_tokens

    output_cost = (
        completion_tokens / 1_000_000
    ) * model_config.output_cost_per_1m_tokens

    total_cost = input_cost + output_cost

    return CostMetrics(
        estimated_cost=total_cost,
        actual_cost=total_cost,
    )