"""AI generation modules for text and images."""

from .prompts import (
    GENERATE_ILLUSTRATION_PROMPT,
    PAGE_WRITER_SYSTEM,
    # Key templates
    STORY_GUIDE_SYSTEM,
    STORY_START,
    WRITE_PAGE_TEXT,
    PromptTemplate,
    calculate_story_structure,
    format_character_details,
    format_previous_pages,
    get_all_templates,
)
from .text import (
    GenerationConfig,
    Message,
    MockTextGenerator,
    OllamaClient,
    TextGenerator,
    create_text_generator,
)

__all__ = [
    # Text generation
    "GenerationConfig",
    "Message",
    "TextGenerator",
    "OllamaClient",
    "MockTextGenerator",
    "create_text_generator",
    # Prompts
    "PromptTemplate",
    "get_all_templates",
    "format_previous_pages",
    "format_character_details",
    "calculate_story_structure",
    "STORY_GUIDE_SYSTEM",
    "PAGE_WRITER_SYSTEM",
    "STORY_START",
    "WRITE_PAGE_TEXT",
    "GENERATE_ILLUSTRATION_PROMPT",
]
