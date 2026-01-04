"""
Tests for the text generation module.
"""

from __future__ import annotations

import pytest

from storyteller.generation import (
    GenerationConfig,
    Message,
    MockTextGenerator,
    TextGenerator,
    create_text_generator,
)


class TestMessage:
    """Tests for the Message dataclass."""

    def test_create_message(self) -> None:
        """Message can be created with role and content."""
        msg = Message(role="user", content="Hello")
        assert msg.role == "user"
        assert msg.content == "Hello"

    def test_message_is_frozen(self) -> None:
        """Message is immutable."""
        msg = Message(role="user", content="Hello")
        with pytest.raises(AttributeError):
            msg.content = "World"  # type: ignore[misc]


class TestGenerationConfig:
    """Tests for the GenerationConfig dataclass."""

    def test_default_values(self) -> None:
        """GenerationConfig has sensible defaults."""
        config = GenerationConfig()
        assert config.temperature == 0.7
        assert config.max_tokens is None
        assert config.top_p == 0.9
        assert config.stop == ()

    def test_custom_values(self) -> None:
        """GenerationConfig accepts custom values."""
        config = GenerationConfig(
            temperature=0.5,
            max_tokens=100,
            top_p=0.8,
            stop=("END",),
        )
        assert config.temperature == 0.5
        assert config.max_tokens == 100
        assert config.stop == ("END",)


class TestMockTextGenerator:
    """Tests for the MockTextGenerator."""

    def test_implements_protocol(self) -> None:
        """MockTextGenerator implements TextGenerator protocol."""
        mock = MockTextGenerator()
        assert isinstance(mock, TextGenerator)

    def test_model_name(self) -> None:
        """model_name returns the mock model name."""
        mock = MockTextGenerator(model="test-model")
        assert mock.model_name == "test-model"

    def test_generate_returns_mock_response(self) -> None:
        """generate returns a mock response."""
        mock = MockTextGenerator()
        response = mock.generate("Hello world")
        assert "Mock response" in response
        assert "Hello world" in response

    def test_generate_with_predefined_responses(self) -> None:
        """generate returns predefined responses in order."""
        responses = ["First response", "Second response"]
        mock = MockTextGenerator(responses=responses)

        assert mock.generate("prompt 1") == "First response"
        assert mock.generate("prompt 2") == "Second response"
        # After exhausted, returns generic mock
        assert "Mock response" in mock.generate("prompt 3")

    def test_chat_returns_mock_response(self) -> None:
        """chat returns a mock response."""
        mock = MockTextGenerator()
        messages = [
            Message(role="user", content="Hello"),
        ]
        response = mock.chat(messages)
        assert "Mock response" in response

    def test_call_count_tracking(self) -> None:
        """call_count tracks number of calls."""
        mock = MockTextGenerator()
        assert mock.call_count == 0

        mock.generate("test")
        assert mock.call_count == 1

        mock.chat([Message(role="user", content="test")])
        assert mock.call_count == 2


class TestCreateTextGenerator:
    """Tests for the create_text_generator factory."""

    def test_create_mock_generator(self) -> None:
        """Factory creates MockTextGenerator."""
        gen = create_text_generator(backend="mock", model="test")
        assert isinstance(gen, MockTextGenerator)
        assert gen.model_name == "test"

    def test_unknown_backend_raises(self) -> None:
        """Factory raises for unknown backend."""
        with pytest.raises(ValueError, match="Unknown backend"):
            create_text_generator(backend="unknown")

    def test_create_ollama_generator(self) -> None:
        """Factory creates OllamaClient (may fail if ollama not installed)."""
        try:
            from storyteller.generation import OllamaClient

            gen = create_text_generator(backend="ollama", model="phi4")
            assert isinstance(gen, OllamaClient)
            assert gen.model_name == "phi4"
        except ImportError:
            pytest.skip("ollama package not installed")
