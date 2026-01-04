"""
LLM client abstraction for text generation.

This module provides a protocol-based abstraction for LLM interaction,
allowing easy swapping of models and backends.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Message:
    """
    A single message in a conversation.

    Attributes:
        role: The role of the message sender ("system", "user", or "assistant").
        content: The text content of the message.
    """

    role: str
    content: str


@dataclass(frozen=True)
class GenerationConfig:
    """
    Configuration for text generation.

    Attributes:
        temperature: Controls randomness (0.0 = deterministic, 1.0 = creative).
        max_tokens: Maximum tokens to generate (None = model default).
        top_p: Nucleus sampling threshold.
        stop: Stop sequences to end generation.
    """

    temperature: float = 0.7
    max_tokens: int | None = None
    top_p: float = 0.9
    stop: tuple[str, ...] = field(default_factory=tuple)


@runtime_checkable
class TextGenerator(Protocol):
    """
    Protocol for text generation backends.

    Any LLM client can implement this protocol to be used
    interchangeably in the story engine.
    """

    @property
    def model_name(self) -> str:
        """Get the current model name."""
        ...

    def generate(
        self,
        prompt: str,
        system: str = "",
        config: GenerationConfig | None = None,
    ) -> str:
        """
        Generate text from a single prompt.

        Args:
            prompt: The user prompt to respond to.
            system: Optional system prompt for context.
            config: Generation configuration options.

        Returns:
            The generated text response.
        """
        ...

    def chat(
        self,
        messages: list[Message],
        config: GenerationConfig | None = None,
    ) -> str:
        """
        Generate a response in a multi-turn conversation.

        Args:
            messages: List of conversation messages.
            config: Generation configuration options.

        Returns:
            The generated assistant response.
        """
        ...


class OllamaClient:
    """
    Ollama-based implementation of the TextGenerator protocol.

    This client connects to a local Ollama server for LLM inference.
    """

    def __init__(
        self,
        model: str = "phi4",
        host: str = "http://localhost:11434",
    ) -> None:
        """
        Initialize the Ollama client.

        Args:
            model: The model name to use (e.g., "phi4", "llama3.2", "mistral").
            host: The Ollama server URL.
        """
        self._model = model
        self._host = host
        self._client: object | None = None

    @property
    def model_name(self) -> str:
        """Get the current model name."""
        return self._model

    def set_model(self, model: str) -> None:
        """
        Change the model being used.

        Args:
            model: The new model name to use.
        """
        self._model = model
        logger.info("Switched to model: %s", model)

    def _get_client(self) -> object:
        """Get or create the Ollama client."""
        if self._client is None:
            try:
                import ollama

                self._client = ollama.Client(host=self._host)
            except ImportError as e:
                raise ImportError(
                    "ollama package is required. Install with: uv pip install ollama"
                ) from e
        return self._client

    def generate(
        self,
        prompt: str,
        system: str = "",
        config: GenerationConfig | None = None,
    ) -> str:
        """
        Generate text from a single prompt.

        Args:
            prompt: The user prompt to respond to.
            system: Optional system prompt for context.
            config: Generation configuration options.

        Returns:
            The generated text response.
        """
        messages = []
        if system:
            messages.append(Message(role="system", content=system))
        messages.append(Message(role="user", content=prompt))
        return self.chat(messages, config)

    def chat(
        self,
        messages: list[Message],
        config: GenerationConfig | None = None,
    ) -> str:
        """
        Generate a response in a multi-turn conversation.

        Args:
            messages: List of conversation messages.
            config: Generation configuration options.

        Returns:
            The generated assistant response.
        """
        config = config or GenerationConfig()
        client = self._get_client()

        # Convert messages to Ollama format
        ollama_messages = [{"role": m.role, "content": m.content} for m in messages]

        # Build options
        options: dict[str, object] = {
            "temperature": config.temperature,
            "top_p": config.top_p,
        }
        if config.max_tokens:
            options["num_predict"] = config.max_tokens
        if config.stop:
            options["stop"] = list(config.stop)

        logger.debug(
            "Generating with model=%s, messages=%d, options=%s",
            self._model,
            len(messages),
            options,
        )

        # Call Ollama
        response = client.chat(  # type: ignore[attr-defined]
            model=self._model,
            messages=ollama_messages,
            options=options,
        )

        content: str = response["message"]["content"]
        logger.debug("Generated %d characters", len(content))
        return content

    def list_models(self) -> list[str]:
        """
        List available models on the Ollama server.

        Returns:
            List of model names.
        """
        client = self._get_client()
        response = client.list()  # type: ignore[attr-defined]
        return [model["name"] for model in response.get("models", [])]


class MockTextGenerator:
    """
    Mock text generator for testing and development.

    Returns predefined responses or generates simple placeholder text.
    """

    def __init__(
        self,
        model: str = "mock",
        responses: list[str] | None = None,
    ) -> None:
        """
        Initialize the mock generator.

        Args:
            model: A mock model name.
            responses: Optional list of responses to return in order.
                      If exhausted or not provided, generates placeholder text.
        """
        self._model = model
        self._responses = list(responses) if responses else []
        self._call_count = 0

    @property
    def model_name(self) -> str:
        """Get the mock model name."""
        return self._model

    @property
    def call_count(self) -> int:
        """Get the number of times generate/chat was called."""
        return self._call_count

    def generate(
        self,
        prompt: str,
        system: str = "",
        config: GenerationConfig | None = None,
    ) -> str:
        """Generate a mock response."""
        messages = []
        if system:
            messages.append(Message(role="system", content=system))
        messages.append(Message(role="user", content=prompt))
        return self.chat(messages, config)

    def chat(
        self,
        messages: list[Message],
        config: GenerationConfig | None = None,  # noqa: ARG002
    ) -> str:
        """Generate a mock response for a conversation."""
        del config  # Unused but required by protocol
        self._call_count += 1

        # Return predefined response if available
        if self._responses:
            return self._responses.pop(0)

        # Generate placeholder based on last user message
        last_user = next(
            (m.content for m in reversed(messages) if m.role == "user"),
            "Hello",
        )
        return f"[Mock response to: {last_user[:50]}...]"


def create_text_generator(
    backend: str = "ollama",
    model: str = "phi4",
    **kwargs: object,
) -> TextGenerator:
    """
    Factory function to create a text generator.

    Args:
        backend: The backend to use ("ollama" or "mock").
        model: The model name to use.
        **kwargs: Additional arguments passed to the backend constructor.

    Returns:
        A TextGenerator implementation.

    Raises:
        ValueError: If the backend is not recognized.
    """
    if backend == "ollama":
        return OllamaClient(model=model, **kwargs)  # type: ignore[arg-type]
    elif backend == "mock":
        return MockTextGenerator(model=model, **kwargs)  # type: ignore[arg-type]
    else:
        raise ValueError(f"Unknown backend: {backend}")
