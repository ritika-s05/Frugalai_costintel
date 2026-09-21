from dataclasses import dataclass

from app.core.model_registry import MODEL_REGISTRY
from app.schemas.chat import ChatCompletionRequest


@dataclass
class TokenGuardResult:
    estimated_input_tokens: int
    max_output_tokens: int
    estimated_max_cost: float
    allowed: bool
    reason: str


class TokenGuard:
    DEFAULT_MAX_OUTPUT_TOKENS = 500

    def __init__(
        self,
        max_request_cost: float = 0.01,
    ) -> None:
        self.max_request_cost = max_request_cost

    def check(
        self,
        request: ChatCompletionRequest,
        model: str,
    ) -> TokenGuardResult:
        model_config = MODEL_REGISTRY.get(model)

        if model_config is None:
            raise ValueError(
                f"Pricing information not found for model: {model}"
            )

        estimated_input_tokens = self._estimate_input_tokens(
            request
        )

        max_output_tokens = (
            request.max_tokens
            if request.max_tokens is not None
            else self.DEFAULT_MAX_OUTPUT_TOKENS
        )

        estimated_input_cost = (
            estimated_input_tokens / 1_000_000
        ) * model_config.input_cost_per_1m_tokens

        estimated_output_cost = (
            max_output_tokens / 1_000_000
        ) * model_config.output_cost_per_1m_tokens

        estimated_max_cost = (
            estimated_input_cost + estimated_output_cost
        )

        allowed = (
            estimated_max_cost <= self.max_request_cost
        )

        if allowed:
            reason = (
                f"Estimated maximum cost "
                f"${estimated_max_cost:.8f} is within "
                f"the request budget of "
                f"${self.max_request_cost:.8f}."
            )
        else:
            reason = (
                f"Estimated maximum cost "
                f"${estimated_max_cost:.8f} exceeds "
                f"the request budget of "
                f"${self.max_request_cost:.8f}."
            )

        return TokenGuardResult(
            estimated_input_tokens=estimated_input_tokens,
            max_output_tokens=max_output_tokens,
            estimated_max_cost=estimated_max_cost,
            allowed=allowed,
            reason=reason,
        )

    @staticmethod
    def _estimate_input_tokens(
        request: ChatCompletionRequest,
    ) -> int:
        text = " ".join(
            message.content
            for message in request.messages
        )

        # Lightweight provider-independent approximation:
        # roughly 4 characters per token.
        estimated_tokens = max(
            1,
            (len(text) + 3) // 4,
        )

        return estimated_tokens