"""Application settings, loaded from environment variables (12-factor)."""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

LLMProvider = Literal["anthropic", "openai", "fake"]
Effort = Literal["low", "medium", "high", "xhigh", "max"]


class Settings(BaseSettings):
    """All runtime configuration. Every field can be set via `APP_<FIELD>`."""

    model_config = SettingsConfigDict(
        env_prefix="APP_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    environment: Literal["local", "test", "staging", "production"] = "local"
    log_level: str = "INFO"
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:5173"])
    # Built Vue app; served by FastAPI when the directory exists (container image).
    static_dir: Path = Path("static")

    # --- LLM ---------------------------------------------------------------
    llm_provider: LLMProvider = "fake"
    llm_model: str = "claude-opus-5-5"
    llm_max_tokens: int = Field(default=16_000, ge=1, le=128_000)
    llm_effort: Effort = "medium"
    llm_timeout_seconds: float = Field(default=120.0, gt=0)
    llm_system_prompt: str = "You are a helpful assistant. Answer concisely."
    # Server-side refusal fallback for Claude models (re-runs a declined request on
    # a fallback model inside the same call).
    llm_refusal_fallback: bool = True
    anthropic_api_key: SecretStr | None = None
    # Any OpenAI-compatible server: OpenAI, Ollama, vLLM, LM Studio, LiteLLM, ...
    openai_api_key: SecretStr | None = None
    openai_base_url: str | None = None

    # --- ML ----------------------------------------------------------------
    torch_device: Literal["auto", "cpu", "cuda", "mps"] = "auto"
    torch_seed: int = 42


@lru_cache
def get_settings() -> Settings:
    """Return the process-wide settings (cached; override in tests via DI)."""
    return Settings()
