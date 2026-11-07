from app.core.config import Settings
from app.services.llm.base import LLMClient


def create_llm_client(settings: Settings) -> LLMClient:
    """Build the configured provider. SDK imports stay lazy and provider-local."""
    match settings.llm_provider:
        case "anthropic":
            from app.services.llm.anthropic_client import AnthropicLLM  # noqa: PLC0415

            return AnthropicLLM(settings)
        case "openai":
            from app.services.llm.openai_client import OpenAICompatibleLLM  # noqa: PLC0415

            return OpenAICompatibleLLM(settings)
        case "fake":
            from app.services.llm.fake_client import FakeLLM  # noqa: PLC0415

            return FakeLLM(delay_seconds=0.03 if settings.environment == "local" else 0.0)
