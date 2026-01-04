"""Core functionality for story creation and management."""

from .engine import (
    ConversationState,
    StoryEngine,
)
from .persistence import (
    delete_story,
    get_export_path,
    get_page_illustration_path,
    get_stories_directory,
    list_stories,
    load_story,
    save_story,
)
from .story import (
    ILLUSTRATION_STYLES,
    TARGET_AGE_RANGES,
    Character,
    Page,
    Story,
    StoryMetadata,
    add_character,
    add_page,
    create_character,
    create_page,
    create_story,
    remove_character,
    remove_page,
    renumber_pages,
    update_page,
)

__all__ = [
    # Data models
    "Character",
    "Page",
    "Story",
    "StoryMetadata",
    # Constants
    "ILLUSTRATION_STYLES",
    "TARGET_AGE_RANGES",
    # Story factory functions
    "create_story",
    "create_page",
    "create_character",
    "add_character",
    "remove_character",
    "add_page",
    "update_page",
    "remove_page",
    "renumber_pages",
    # Persistence functions
    "save_story",
    "load_story",
    "list_stories",
    "delete_story",
    "get_stories_directory",
    "get_page_illustration_path",
    "get_export_path",
    # Engine
    "ConversationState",
    "StoryEngine",
]
