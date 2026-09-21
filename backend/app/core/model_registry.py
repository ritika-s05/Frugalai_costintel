from dataclasses import dataclass


@dataclass(frozen=True)
class ModelConfig:
    provider: str
    model: str
    input_cost_per_1m_tokens: float
    output_cost_per_1m_tokens: float
    capability_level: int
    enabled: bool = True


MODEL_REGISTRY: dict[str, ModelConfig] = {
    "gemini-3.6-flash": ModelConfig(
        provider="gemini",
        model="gemini-3.6-flash",
        input_cost_per_1m_tokens=0.75,
        output_cost_per_1m_tokens=3.75,
        capability_level=3,
        enabled=True,
    ),
    "openai/gpt-oss-20b": ModelConfig(
        provider="groq",
        model="openai/gpt-oss-20b",
        input_cost_per_1m_tokens=0.075,
        output_cost_per_1m_tokens=0.30,
        capability_level=2,
    ),

    "claude-haiku-4-5-20251001": ModelConfig(
        provider="anthropic",
        model="claude-haiku-4-5-20251001",
        input_cost_per_1m_tokens=1.00,
        output_cost_per_1m_tokens=5.00,
        capability_level=3,
        enabled=False,
    ),
}