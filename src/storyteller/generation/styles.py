"""Illustration style presets for Storyteller.

This module defines style presets that modify image generation prompts
to achieve consistent illustration styles for children's books.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class StylePreset:
    """An illustration style preset.

    Attributes:
        name: Internal name for the style.
        display_name: Human-readable name for UI display.
        prompt_suffix: Text appended to prompts for this style.
        description: Brief description for UI tooltips.
    """

    name: str
    display_name: str
    prompt_suffix: str
    description: str


# Child-safety modifiers added when apply_style() or build_illustration_prompt() is called.
# IMPORTANT: These modifiers are NOT automatically added to all prompts.
# Callers using ImageGenerator.generate() directly must ensure they call
# apply_style() or build_illustration_prompt() to include these safety modifiers.
SAFETY_MODIFIERS = (
    "children's book illustration, friendly and approachable, "
    "warm colors, gentle and safe feeling, age-appropriate"
)


STYLE_PRESETS: dict[str, StylePreset] = {
    "watercolor": StylePreset(
        name="watercolor",
        display_name="Watercolor",
        prompt_suffix=(
            "watercolor illustration style, soft edges, warm pastel colors, "
            "dreamy atmosphere, gentle brush strokes, children's picture book art"
        ),
        description="Soft, dreamy watercolor with pastel colors",
    ),
    "cartoon": StylePreset(
        name="cartoon",
        display_name="Cartoon",
        prompt_suffix=(
            "cartoon illustration style, bright vibrant colors, simple bold shapes, "
            "clean lines, playful character design, children's picture book art"
        ),
        description="Bright, vibrant cartoon with bold shapes",
    ),
    "storybook_classic": StylePreset(
        name="storybook_classic",
        display_name="Storybook Classic",
        prompt_suffix=(
            "classic children's book illustration style, warm earthy colors, "
            "detailed but soft rendering, cozy inviting atmosphere, "
            "reminiscent of classic picture books, nostalgic feeling"
        ),
        description="Classic picture book style with warm, cozy feeling",
    ),
    "modern_digital": StylePreset(
        name="modern_digital",
        display_name="Modern Digital",
        prompt_suffix=(
            "modern digital illustration style, bold saturated colors, "
            "clean vector-like lines, contemporary character design, "
            "children's picture book art, sense of wonder and adventure"
        ),
        description="Clean, modern digital art with bold colors",
    ),
    "pencil_sketch": StylePreset(
        name="pencil_sketch",
        display_name="Pencil Sketch",
        prompt_suffix=(
            "pencil sketch illustration style, hand-drawn look, "
            "soft graphite shading, gentle lines, expressive strokes, "
            "children's book art, warm and personal feeling"
        ),
        description="Hand-drawn pencil sketch with soft shading",
    ),
}


def get_style(name: str) -> StylePreset:
    """Get a style preset by name.

    Args:
        name: The style name.

    Returns:
        The StylePreset.

    Raises:
        KeyError: If the style name is not found.
    """
    if name not in STYLE_PRESETS:
        available = ", ".join(STYLE_PRESETS.keys())
        raise KeyError(f"Unknown style '{name}'. Available: {available}")
    return STYLE_PRESETS[name]


def list_styles() -> list[StylePreset]:
    """Get all available style presets.

    Returns:
        List of all StylePreset objects.
    """
    return list(STYLE_PRESETS.values())


def apply_style(base_prompt: str, style_name: str) -> str:
    """Apply a style preset to a base prompt.

    This combines the base prompt with the style's prompt suffix
    and adds child-safety modifiers.

    Args:
        base_prompt: The base image description.
        style_name: The style preset name.

    Returns:
        The complete prompt with style applied.

    Example:
        >>> apply_style("A mouse in a garden", "watercolor")
        'A mouse in a garden, watercolor illustration style, ...'
    """
    style = get_style(style_name)

    # Combine base prompt with style and safety modifiers
    full_prompt = f"{base_prompt}, {style.prompt_suffix}, {SAFETY_MODIFIERS}"

    return full_prompt


def build_illustration_prompt(
    scene_description: str,
    character_traits: list[str] | None = None,
    style_name: str = "watercolor",
    additional_context: str | None = None,
) -> str:
    """Build a complete illustration prompt.

    This is the main function for constructing prompts for image generation.
    It combines scene description, character visual traits, style, and
    safety modifiers into a coherent prompt.

    Args:
        scene_description: Description of the scene to illustrate.
        character_traits: Visual traits of characters in the scene.
        style_name: Style preset to apply.
        additional_context: Optional additional context or modifiers.

    Returns:
        Complete prompt ready for image generation.

    Example:
        >>> build_illustration_prompt(
        ...     scene_description="A small mouse exploring a sunny garden",
        ...     character_traits=["small brown mouse", "red scarf", "curious eyes"],
        ...     style_name="watercolor",
        ... )
    """
    parts = [scene_description]

    # Add character traits if present
    if character_traits:
        traits_str = ", ".join(character_traits)
        parts.append(f"featuring {traits_str}")

    # Add additional context if present
    if additional_context:
        parts.append(additional_context)

    # Combine parts
    base_prompt = ", ".join(parts)

    # Apply style and safety modifiers
    return apply_style(base_prompt, style_name)
