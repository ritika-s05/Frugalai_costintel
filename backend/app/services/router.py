from dataclasses import dataclass

from app.core.model_registry import MODEL_REGISTRY, ModelConfig
from app.schemas.chat import ChatCompletionRequest
from app.services.complexity import ComplexityClassifier


@dataclass
class RoutingDecision:
    requested_model: str
    selected_model: str
    provider: str
    routed: bool
    complexity_level: int
    reason: str


class SmartRouter:
    def __init__(self) -> None:
        self.classifier = ComplexityClassifier()

    def route(
        self,
        request: ChatCompletionRequest,
    ) -> RoutingDecision:
        complexity = self.classifier.classify(request)

        selected_config = self._find_cheapest_capable_model(
            required_capability=complexity.level
        )

        return RoutingDecision(
            requested_model=request.model,
            selected_model=selected_config.model,
            provider=selected_config.provider,
            routed=selected_config.model != request.model,
            complexity_level=complexity.level,
            reason=(
                f"Request classified as capability level "
                f"{complexity.level} (score={complexity.score}: "
                f"{complexity.reason}). Selected cheapest enabled "
                f"model meeting capability requirement."
            ),
        )

    def _find_cheapest_capable_model(
        self,
        required_capability: int,
    ) -> ModelConfig:
        eligible_models = [
            config
            for config in MODEL_REGISTRY.values()
            if (
                config.enabled
                and config.capability_level >= required_capability
            )
        ]

        if not eligible_models:
            raise RuntimeError(
                "No enabled model satisfies the required capability level."
            )

        return min(
            eligible_models,
            key=lambda config: (
                config.input_cost_per_1m_tokens
                + config.output_cost_per_1m_tokens
            ),
        )

    '''
            Requested model enabled?
                │
            ┌───┴───┐
        yes      no
            │        │
        use it    find cheapest
                enabled model

    '''