from app.providers.openai_provider import OpenAIProvider
from app.providers.gemini_provider import GeminiProvider
from app.providers.groq_provider import GroqProvider
from app.providers.anthropic_provider import AnthropicProvider


class ProviderFactory:
    providers = {
        "openai": OpenAIProvider,
        "gemini": GeminiProvider,
        "groq": GroqProvider,
        "anthropic": AnthropicProvider,
    }

    @classmethod
    def get(cls, provider_name: str):
        provider = cls.providers.get(provider_name.lower())

        if provider is None:
            raise ValueError(f"Unsupported provider: {provider_name}")

        return provider()