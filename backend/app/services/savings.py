from dataclasses import dataclass
from app.core.model_registry import MODEL_REGISTRY

@dataclass
class SavingsMetrics:
    baseline_cost: float
    actual_cost: float
    savings: float
    savings_percentage: float


def calculate_savings(
    requested_model: str,
    executed_model: str,
    prompt_tokens: int,
    completion_tokens: int,
) -> SavingsMetrics:
    requested_config = MODEL_REGISTRY.get(requested_model)
    executed_config = MODEL_REGISTRY.get(executed_model)

    if requested_config is None:
        raise ValueError(
            f"Pricing information not found for requested model: "
            f"{requested_model}"
        )

    if executed_config is None:
        raise ValueError(
            f"Pricing information not found for executed model: "
            f"{executed_model}"
        )

    baseline_cost = (
        (prompt_tokens / 1_000_000)
        * requested_config.input_cost_per_1m_tokens
        +
        (completion_tokens / 1_000_000)
        * requested_config.output_cost_per_1m_tokens
    )

    actual_cost = (
        (prompt_tokens / 1_000_000)
        * executed_config.input_cost_per_1m_tokens
        +
        (completion_tokens / 1_000_000)
        * executed_config.output_cost_per_1m_tokens
    )

    savings = max(
        baseline_cost - actual_cost,
        0.0,
    )

    savings_percentage = (
        (savings / baseline_cost) * 100
        if baseline_cost > 0
        else 0.0
    )

    return SavingsMetrics(
        baseline_cost=baseline_cost,
        actual_cost=actual_cost,
        savings=savings,
        savings_percentage=savings_percentage,
    )