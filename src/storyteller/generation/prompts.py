"""
Prompt templates for story creation and guidance.

This module contains structured prompts for different stages of story creation.
Templates are designed to be modular and easily adjustable for experimentation.
"""

from __future__ import annotations

from dataclasses import dataclass
from string import Template
from typing import Any


@dataclass(frozen=True)
class PromptTemplate:
    """
    A configurable prompt template.

    Attributes:
        name: Identifier for this template.
        template: The template string with $variable placeholders.
        description: Human-readable description of the template's purpose.
    """

    name: str
    template: str
    description: str = ""

    def render(self, **kwargs: Any) -> str:
        """
        Render the template with the given variables.

        Args:
            **kwargs: Variables to substitute in the template.

        Returns:
            The rendered prompt string.
        """
        return Template(self.template).safe_substitute(**kwargs)


# =============================================================================
# System Prompts - Define the LLM's role and behavior
# =============================================================================

STORY_GUIDE_SYSTEM = PromptTemplate(
    name="story_guide_system",
    description="System prompt for the story guidance assistant",
    template="""You are a friendly and creative story guide helping to create a children's storybook.

Your role is to:
- Ask helpful questions to develop the story collaboratively
- Suggest age-appropriate plot elements, characters, and settings
- Keep stories positive, gentle, and educational
- Use simple vocabulary suitable for young children
- Encourage creativity while maintaining a safe, nurturing tone

Target age group: $target_age years old
Illustration style: $style

Guidelines:
- Stories should have clear beginnings, middles, and endings
- Characters should be relatable and have simple motivations
- Themes should focus on friendship, curiosity, kindness, or growth
- Avoid scary, violent, or complex themes
- Keep each page's text to 2-3 short sentences

Always be encouraging and build upon the user's ideas.""",
)

PAGE_WRITER_SYSTEM = PromptTemplate(
    name="page_writer_system",
    description="System prompt for writing individual page text",
    template="""You are a children's book author writing text for a storybook page.

Write in a style appropriate for $target_age year olds:
- Use simple, clear sentences
- Include gentle rhythm and occasional rhyme if natural
- Keep vocabulary age-appropriate
- Each page should have 2-3 sentences maximum
- Text should complement (not describe) the illustration

Story title: $title
Style: $style""",
)

ILLUSTRATION_PROMPT_SYSTEM = PromptTemplate(
    name="illustration_prompt_system",
    description="System prompt for generating illustration prompts",
    template="""You are an art director for children's book illustrations.

Create detailed illustration prompts that:
- Describe the scene visually (not the text content)
- Maintain character consistency using provided traits
- Specify the art style: $style
- Include mood, lighting, and color palette
- Emphasize child-friendly, warm, inviting imagery

Always include these safety modifiers:
- "children's book illustration"
- "friendly and approachable"
- "gentle and safe feeling"
- "warm colors" """,
)


# =============================================================================
# Story Creation Prompts
# =============================================================================

STORY_START = PromptTemplate(
    name="story_start",
    description="Opening prompt to begin story creation",
    template="""Let's create a wonderful story together!

To get started, tell me about:
1. **Who** is the main character? (a child, an animal, a magical creature?)
2. **Where** does the story take place? (a forest, a cozy home, a magical land?)
3. **What** kind of adventure or lesson? (making friends, being brave, learning something new?)

Share as much or as little as you'd like - I'll help fill in the details!""",
)

STORY_DEVELOPMENT = PromptTemplate(
    name="story_development",
    description="Prompt to develop story details from initial input",
    template="""Based on your ideas, let me help develop the story.

What you've shared:
$user_input

Now let's think about:
- What challenge or goal does $character_name have?
- Who might they meet along the way?
- What will they learn or discover?

What sounds most exciting to you?""",
)

SUGGEST_PLOT_POINTS = PromptTemplate(
    name="suggest_plot_points",
    description="Suggest plot points for a story",
    template="""For a $page_count-page story about $summary:

Here's a suggested story structure:

**Beginning (Pages 1-$beginning_end):**
- Introduce $character_name and their world
- Show their normal life

**Middle (Pages $middle_start-$middle_end):**
- The adventure or challenge begins
- $character_name tries to solve the problem
- They might need help or learn something

**End (Pages $ending_start-$page_count):**
- The challenge is resolved
- $character_name has grown or learned
- A satisfying, happy conclusion

Would you like me to draft text for any of these pages?""",
)


# =============================================================================
# Page Content Prompts
# =============================================================================

WRITE_PAGE_TEXT = PromptTemplate(
    name="write_page_text",
    description="Generate text for a specific page",
    template="""Write the text for page $page_number of $total_pages.

Story context:
- Title: $title
- Main character: $character_name - $character_description
- Setting: $setting

Previous pages:
$previous_text

This page should:
$page_purpose

Write 2-3 sentences that:
- Continue the story naturally
- Are appropriate for $target_age year olds
- Leave room for the illustration to tell part of the story

Respond with ONLY the page text, no other commentary.""",
)

REFINE_PAGE_TEXT = PromptTemplate(
    name="refine_page_text",
    description="Improve or adjust existing page text",
    template="""Here is the current text for page $page_number:

"$current_text"

Please $refinement_request

Keep the text to 2-3 sentences, suitable for $target_age year olds.
Respond with ONLY the revised text, no other commentary.""",
)


# =============================================================================
# Illustration Prompts
# =============================================================================

GENERATE_ILLUSTRATION_PROMPT = PromptTemplate(
    name="generate_illustration_prompt",
    description="Create an image generation prompt from page content",
    template="""Create an illustration prompt for this storybook page:

Page text: "$page_text"

Character details:
$character_details

Scene requirements:
- Setting: $setting
- Mood: $mood
- Time of day: $time_of_day

Art style: $style children's book illustration

Generate a detailed prompt for the illustration. Include:
1. The specific scene composition
2. Character poses and expressions
3. Background elements
4. Color palette suggestions
5. Lighting and atmosphere

End with these required modifiers:
"children's book illustration, friendly and approachable, warm colors, gentle and safe feeling, high quality"

Respond with ONLY the illustration prompt, no other commentary.""",
)

ILLUSTRATION_PROMPT_TEMPLATE = PromptTemplate(
    name="illustration_prompt_template",
    description="Direct template for illustration prompts (no LLM needed)",
    template="""$style children's book illustration.

$scene_description

Characters: $character_descriptions
Setting: $setting
Mood: $mood, $time_of_day lighting

children's book illustration, friendly and approachable, warm colors, gentle and safe feeling, high quality, detailed, professional illustration""",
)


# =============================================================================
# Character Prompts
# =============================================================================

DEFINE_CHARACTER = PromptTemplate(
    name="define_character",
    description="Help define a character's details",
    template="""Let's create a memorable character!

You mentioned: $initial_description

To bring this character to life, let's define:

1. **Name**: What should we call them?
2. **Appearance**: What do they look like? (colors, size, distinguishing features)
3. **Personality**: Are they curious? Shy? Brave? Silly?
4. **Special trait**: What makes them unique?

For consistent illustrations, I'll also need 3-4 visual details that should appear in every picture of them (like "wears a red scarf" or "has big curious eyes").

What details would you like to add?""",
)

EXTRACT_VISUAL_TRAITS = PromptTemplate(
    name="extract_visual_traits",
    description="Extract visual traits from character description",
    template="""From this character description, extract 4-6 key visual traits for illustration consistency:

Character: $name
Description: $description

List only the visual details an illustrator needs to draw this character consistently.
Format as a simple comma-separated list.

Example: "small brown mouse, big curious eyes, pink nose, tiny red scarf, fluffy ears"

Respond with ONLY the comma-separated visual traits.""",
)


# =============================================================================
# Utility Functions
# =============================================================================

def get_all_templates() -> dict[str, PromptTemplate]:
    """
    Get all defined prompt templates.

    Returns:
        Dictionary mapping template names to PromptTemplate objects.
    """
    return {
        "story_guide_system": STORY_GUIDE_SYSTEM,
        "page_writer_system": PAGE_WRITER_SYSTEM,
        "illustration_prompt_system": ILLUSTRATION_PROMPT_SYSTEM,
        "story_start": STORY_START,
        "story_development": STORY_DEVELOPMENT,
        "suggest_plot_points": SUGGEST_PLOT_POINTS,
        "write_page_text": WRITE_PAGE_TEXT,
        "refine_page_text": REFINE_PAGE_TEXT,
        "generate_illustration_prompt": GENERATE_ILLUSTRATION_PROMPT,
        "illustration_prompt_template": ILLUSTRATION_PROMPT_TEMPLATE,
        "define_character": DEFINE_CHARACTER,
        "extract_visual_traits": EXTRACT_VISUAL_TRAITS,
    }


def format_previous_pages(pages: list[tuple[int, str]]) -> str:
    """
    Format previous page texts for inclusion in prompts.

    Args:
        pages: List of (page_number, text) tuples.

    Returns:
        Formatted string summarizing previous pages.
    """
    if not pages:
        return "(This is the first page)"

    lines = []
    for num, text in pages:
        lines.append(f"Page {num}: {text}")
    return "\n".join(lines)


def format_character_details(
    name: str,
    description: str,
    visual_traits: list[str],
) -> str:
    """
    Format character details for prompts.

    Args:
        name: Character name.
        description: Character description.
        visual_traits: List of visual traits.

    Returns:
        Formatted character details string.
    """
    traits_str = ", ".join(visual_traits) if visual_traits else "not specified"
    return f"{name}: {description}\nVisual traits: {traits_str}"


def calculate_story_structure(page_count: int) -> dict[str, int]:
    """
    Calculate story structure based on page count.

    Args:
        page_count: Total number of pages.

    Returns:
        Dictionary with beginning_end, middle_start, middle_end, ending_start.
    """
    if page_count <= 4:
        return {
            "beginning_end": 1,
            "middle_start": 2,
            "middle_end": page_count - 1,
            "ending_start": page_count,
        }
    elif page_count <= 8:
        return {
            "beginning_end": 2,
            "middle_start": 3,
            "middle_end": page_count - 2,
            "ending_start": page_count - 1,
        }
    else:
        beginning = page_count // 4
        ending_start = page_count - (page_count // 4) + 1
        return {
            "beginning_end": beginning,
            "middle_start": beginning + 1,
            "middle_end": ending_start - 1,
            "ending_start": ending_start,
        }
