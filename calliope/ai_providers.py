"""Abstractions around AI providers used by Calliope."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict, Optional

from .utils import get_console


class ProviderError(RuntimeError):
    """Raised when AI provider operations fail."""


@dataclass
class ProviderSettings:
    """Configuration for provider selection."""

    provider: str
    model: str = "gpt-4"
    temperature: float = 0.7
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None


class AIProvider:
    """Base provider interface."""

    def generate(self, prompt: str, **kwargs: Any) -> str:  # pragma: no cover - interface
        raise NotImplementedError


class OpenAIProvider(AIProvider):
    """OpenAI completions implementation."""

    def __init__(self, settings: ProviderSettings) -> None:
        try:
            from openai import OpenAI
        except ImportError as exc:  # pragma: no cover - runtime guard
            raise ProviderError("openai package is not installed.") from exc

        api_key = settings.openai_api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ProviderError("OpenAI API key is not configured.")
        self._client = OpenAI(api_key=api_key)
        self.settings = settings

    def generate(self, prompt: str, **kwargs: Any) -> str:
        parameters = {
            "model": self.settings.model,
            "messages": [
                {"role": "system", "content": kwargs.get("system_prompt", "You are a helpful writing assistant.")},
                {"role": "user", "content": prompt},
            ],
            "temperature": kwargs.get("temperature", self.settings.temperature),
        }
        try:
            response = self._client.chat.completions.create(**parameters)
        except Exception as exc:  # pragma: no cover - API failure
            raise ProviderError(f"OpenAI generation failed: {exc}") from exc
        message = response.choices[0].message.content if response.choices else ""
        return message.strip()


class ClaudeProvider(AIProvider):
    """Anthropic Claude integration."""

    def __init__(self, settings: ProviderSettings) -> None:
        try:
            import anthropic  # noqa: F401  # pylint: disable=import-error,unused-import
        except ImportError as exc:  # pragma: no cover - runtime guard
            raise ProviderError("anthropic package is not installed.") from exc

        api_key = settings.anthropic_api_key or os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ProviderError("Anthropic API key is not configured.")
        self.settings = settings
        self._client = anthropic.Anthropic(api_key=api_key)

    def generate(self, prompt: str, **kwargs: Any) -> str:
        try:
            message = self._client.messages.create(
                model=self.settings.model,
                max_tokens=kwargs.get("max_tokens", 800),
                temperature=kwargs.get("temperature", self.settings.temperature),
                system=kwargs.get(
                    "system_prompt",
                    "You are a fiction writing assistant ensuring character consistency.",
                ),
                messages=[{"role": "user", "content": prompt}],
            )
        except Exception as exc:  # pragma: no cover - API failure
            raise ProviderError(f"Claude generation failed: {exc}") from exc
        return message.content[0].text.strip()


class LocalProvider(AIProvider):
    """Simplistic wrapper around local model integrations (stub for MVP)."""

    def __init__(self, settings: ProviderSettings) -> None:
        self.settings = settings
        self.console = get_console()

    def generate(self, prompt: str, **kwargs: Any) -> str:
        self.console.print(
            "[yellow]Local provider is not yet implemented. Returning prompt as placeholder.[/yellow]"
        )
        return f"[LOCAL MODEL PLACEHOLDER]\n{prompt}"


def provider_from_config(config: Dict[str, Any]) -> AIProvider:
    """Instantiate provider based on configuration dictionary."""
    ai_config = config.get("ai", {})
    settings = ProviderSettings(
        provider=str(ai_config.get("default_provider", "openai")),
        model=str(ai_config.get("model", "gpt-4")),
        temperature=float(ai_config.get("temperature", 0.7)),
        openai_api_key=ai_config.get("openai_api_key"),
        anthropic_api_key=ai_config.get("anthropic_api_key"),
    )
    provider = settings.provider.lower()
    if provider == "openai":
        return OpenAIProvider(settings)
    if provider in {"claude", "anthropic"}:
        return ClaudeProvider(settings)
    if provider == "local":
        return LocalProvider(settings)
    raise ProviderError(f"Unsupported provider '{settings.provider}'.")
