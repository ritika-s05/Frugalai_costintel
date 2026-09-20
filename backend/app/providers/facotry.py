from app.providers.openai_provider import OpenAIProvider
from app.providers.anthropic_provider import AnthropicProvider
from app.providers.gemini_provider import GeminiProvider
from app.providers.groq_provider import GroqProvider
from app.providers.ollama_provider import OllamaProvider


class ProviderFactory:

    providers = {
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
        "gemini": GeminiProvider,
        "groq": GroqProvider,
        "ollama": OllamaProvider,
    }

    @classmethod
    def get(cls, provider_name):
        provider = cls.providers.get(provider_name)

        if provider is None:
            raise ValueError(f"Unsupported provider: {provider_name}")

        return provider()