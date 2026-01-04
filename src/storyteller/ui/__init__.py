"""User interface components built with Flet.

This package provides the graphical user interface for Storyteller,
including the main application window, views, components, and dialogs.
"""

from .app import StorytellerApp, main, run
from .state import (
    ActiveTab,
    AppConfig,
    AppState,
    ConversationMessage,
    GenerationStatus,
    StateManager,
    state_manager,
)
from .theme import (
    BorderRadius,
    Colors,
    Dimensions,
    Shadows,
    Spacing,
    Typography,
    apply_theme,
    create_theme,
)

__all__ = [
    # Main app
    "StorytellerApp",
    "main",
    "run",
    # State management
    "ActiveTab",
    "AppConfig",
    "AppState",
    "ConversationMessage",
    "GenerationStatus",
    "StateManager",
    "state_manager",
    # Theme
    "BorderRadius",
    "Colors",
    "Dimensions",
    "Shadows",
    "Spacing",
    "Typography",
    "apply_theme",
    "create_theme",
]
