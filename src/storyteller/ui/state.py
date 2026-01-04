"""Application state management for the Storyteller GUI.

This module provides centralized state management using dataclasses
for the entire application, including story data, UI state, and
user configuration.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from storyteller.core import Story, StoryEngine


class ActiveTab(Enum):
    """Enumeration of available application tabs."""

    SETTINGS = "settings"
    CREATE = "create"
    PREVIEW = "preview"


class GenerationStatus(Enum):
    """Status of AI generation operations."""

    IDLE = "idle"
    GENERATING_TEXT = "generating_text"
    GENERATING_IMAGE = "generating_image"
    ERROR = "error"


@dataclass
class ConversationMessage:
    """A single message in the story creation conversation.

    Attributes:
        role: Who sent the message ('user' or 'assistant').
        content: The text content of the message.
        timestamp: When the message was created.
    """

    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class AppConfig:
    """User configuration persisted between sessions.

    Attributes:
        llm_model: Name of the Ollama model to use for text generation.
        llm_temperature: Temperature setting for text generation (0.0-1.0).
        llm_max_tokens: Maximum tokens for generation, None for auto.
        image_model: FLUX model variant ('schnell' or 'dev').
        image_quantization: Model quantization level ('4-bit' or '8-bit').
        image_steps: Number of inference steps for image generation.
        auto_generate_images: Whether to auto-generate images after page text.
    """

    # LLM settings
    llm_model: str = "phi4"
    llm_temperature: float = 0.7
    llm_max_tokens: int | None = None

    # Image settings
    image_model: str = "schnell"
    image_quantization: str = "4-bit"
    image_steps: int = 4
    auto_generate_images: bool = False


@dataclass
class AppState:
    """Global application state.

    This dataclass holds all the state for the Storyteller application,
    including the current story, UI state, and configuration.

    Attributes:
        current_story: The story currently being edited, if any.
        is_modified: Whether the story has unsaved changes.
        project_path: Path to the current story project directory.
        engine: The StoryEngine instance for AI interactions.
        conversation_messages: History of conversation with the AI.
        active_tab: Currently selected tab in the UI.
        current_page_number: Currently selected page (1-indexed).
        generation_status: Current status of AI generation.
        generation_progress: Progress of current generation (0.0-1.0).
        error_message: Current error message, if any.
        available_models: List of available Ollama models.
        config: User configuration settings.
    """

    # Current story
    current_story: Story | None = None
    is_modified: bool = False
    project_path: Path | None = None

    # Engine and conversation
    engine: StoryEngine | None = None
    conversation_messages: list[ConversationMessage] = field(default_factory=list)

    # UI state
    active_tab: ActiveTab = ActiveTab.CREATE
    current_page_number: int = 1
    generation_status: GenerationStatus = GenerationStatus.IDLE
    generation_progress: float = 0.0
    error_message: str | None = None

    # Available models (populated at runtime)
    available_models: list[str] = field(default_factory=list)

    # Configuration
    config: AppConfig = field(default_factory=AppConfig)


class StateManager:
    """Manages application state and notifies listeners of changes.

    This class provides a centralized way to manage state and notify
    UI components when state changes occur.

    Attributes:
        state: The current application state.
    """

    def __init__(self) -> None:
        """Initialize the state manager with default state."""
        self._state = AppState()
        self._listeners: list[Callable[[], None]] = []

    @property
    def state(self) -> AppState:
        """Get the current application state."""
        return self._state

    def add_listener(self, callback: Callable[[], None]) -> None:
        """Add a listener to be notified when state changes.

        Args:
            callback: Function to call when state changes.
        """
        self._listeners.append(callback)

    def remove_listener(self, callback: Callable[[], None]) -> None:
        """Remove a state change listener.

        Args:
            callback: The callback to remove.
        """
        if callback in self._listeners:
            self._listeners.remove(callback)

    def notify_listeners(self) -> None:
        """Notify all listeners that state has changed."""
        for callback in self._listeners:
            callback()

    def set_story(self, story: Story | None) -> None:
        """Set the current story.

        Args:
            story: The story to set, or None to clear.
        """
        self._state.current_story = story
        self._state.is_modified = False
        if story and story.project_path:
            self._state.project_path = story.project_path
        self.notify_listeners()

    def mark_modified(self) -> None:
        """Mark the current story as having unsaved changes."""
        self._state.is_modified = True
        self.notify_listeners()

    def mark_saved(self) -> None:
        """Mark the current story as saved."""
        self._state.is_modified = False
        self.notify_listeners()

    def set_active_tab(self, tab: ActiveTab) -> None:
        """Set the active tab.

        Args:
            tab: The tab to make active.
        """
        self._state.active_tab = tab
        self.notify_listeners()

    def set_current_page(self, page_number: int) -> None:
        """Set the current page number.

        Args:
            page_number: The page number to select (1-indexed).
        """
        self._state.current_page_number = page_number
        self.notify_listeners()

    def add_conversation_message(self, role: str, content: str) -> None:
        """Add a message to the conversation history.

        Args:
            role: Who sent the message ('user' or 'assistant').
            content: The message content.
        """
        message = ConversationMessage(role=role, content=content)
        self._state.conversation_messages.append(message)
        self.notify_listeners()

    def clear_conversation(self) -> None:
        """Clear the conversation history."""
        self._state.conversation_messages.clear()
        self.notify_listeners()

    def set_generation_status(
        self,
        status: GenerationStatus,
        progress: float = 0.0,
    ) -> None:
        """Set the generation status.

        Args:
            status: The new generation status.
            progress: Progress value (0.0-1.0) for ongoing generation.
        """
        self._state.generation_status = status
        self._state.generation_progress = progress
        self.notify_listeners()

    def set_error(self, message: str | None) -> None:
        """Set or clear an error message.

        Args:
            message: The error message, or None to clear.
        """
        self._state.error_message = message
        if message:
            self._state.generation_status = GenerationStatus.ERROR
        self.notify_listeners()

    def set_available_models(self, models: list[str]) -> None:
        """Set the list of available LLM models.

        Args:
            models: List of model names.
        """
        self._state.available_models = models
        self.notify_listeners()

    def update_config(self, **kwargs: object) -> None:
        """Update configuration values.

        Args:
            **kwargs: Configuration fields to update.
        """
        for key, value in kwargs.items():
            if hasattr(self._state.config, key):
                setattr(self._state.config, key, value)
        self.notify_listeners()


# Global state manager instance
state_manager = StateManager()
