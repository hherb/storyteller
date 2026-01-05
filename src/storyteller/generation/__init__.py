"""AI generation modules for text and images."""

from .image import (
    GenerationProgress,
    GenerationResult,
    ImageConfig,
    ImageGenerator,
    ProgressCallback,
    check_mflux_available,
    check_platform,
    generate_image,
    get_generator,
)
from .prompts import (
    EXTRACT_CHARACTERS_FROM_TEXT,
    EXTRACT_VISUAL_TRAITS,
    GENERATE_ILLUSTRATION_PROMPT,
    PAGE_WRITER_SYSTEM,
    # Key templates
    STORY_GUIDE_SYSTEM,
    STORY_START,
    WRITE_PAGE_TEXT,
    PromptTemplate,
    build_illustration_prompt_for_page,
    build_illustration_prompt_simple,
    calculate_story_structure,
    find_characters_in_page,
    format_character_details,
    format_previous_pages,
    get_all_templates,
)
from .styles import (
    SAFETY_MODIFIERS,
    STYLE_PRESETS,
    StylePreset,
    apply_style,
    build_illustration_prompt,
    get_style,
    list_styles,
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
    # Image generation
    "ImageConfig",
    "ImageGenerator",
    "GenerationResult",
    "GenerationProgress",
    "ProgressCallback",
    "generate_image",
    "get_generator",
    "check_platform",
    "check_mflux_available",
    # Styles
    "StylePreset",
    "STYLE_PRESETS",
    "SAFETY_MODIFIERS",
    "get_style",
    "list_styles",
    "apply_style",
    "build_illustration_prompt",
    # Prompts
    "PromptTemplate",
    "get_all_templates",
    "format_previous_pages",
    "format_character_details",
    "calculate_story_structure",
    "build_illustration_prompt_simple",
    "build_illustration_prompt_for_page",
    "find_characters_in_page",
    "STORY_GUIDE_SYSTEM",
    "PAGE_WRITER_SYSTEM",
    "STORY_START",
    "WRITE_PAGE_TEXT",
    "GENERATE_ILLUSTRATION_PROMPT",
    "EXTRACT_VISUAL_TRAITS",
    "EXTRACT_CHARACTERS_FROM_TEXT",
]
