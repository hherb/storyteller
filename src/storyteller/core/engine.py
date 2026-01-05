"""
Story creation engine.

This module orchestrates the story creation workflow, coordinating
between the LLM, data models, and user interaction.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

from .story import (
    Story,
    add_character,
    add_page,
    create_character,
    create_page,
    create_story,
    update_page,
)

logger = logging.getLogger(__name__)


# =============================================================================
# Protocols - Define interfaces for dependency injection
# =============================================================================


@dataclass(frozen=True)
class Message:
    """A message in the conversation history."""

    role: str
    content: str


@runtime_checkable
class TextGenerator(Protocol):
    """Protocol for text generation backends."""

    @property
    def model_name(self) -> str:
        """Get the current model name."""
        ...

    def generate(
        self,
        prompt: str,
        system: str = "",
        config: object | None = None,
    ) -> str:
        """Generate text from a single prompt."""
        ...

    def chat(
        self,
        messages: list[Message],
        config: object | None = None,
    ) -> str:
        """Generate a response in a multi-turn conversation."""
        ...


# =============================================================================
# Conversation State
# =============================================================================


@dataclass
class ConversationState:
    """
    Tracks the state of a story creation conversation.

    Attributes:
        messages: The full conversation history.
        current_phase: Current phase of story creation.
        story: The story being created.
    """

    messages: list[Message] = field(default_factory=list)
    current_phase: str = "initial"
    story: Story | None = None

    def add_message(self, role: str, content: str) -> None:
        """Add a message to the conversation history."""
        self.messages.append(Message(role=role, content=content))

    def get_messages(self) -> list[Message]:
        """Get the conversation history."""
        return list(self.messages)

    def clear(self) -> None:
        """Clear the conversation state."""
        self.messages.clear()
        self.current_phase = "initial"
        self.story = None


# =============================================================================
# Story Engine
# =============================================================================


class StoryEngine:
    """
    Orchestrates the story creation workflow.

    The engine manages the conversation with the LLM, builds the story
    incrementally, and provides methods for each stage of creation.
    """

    def __init__(
        self,
        text_generator: TextGenerator,
        default_target_age: str = "5-8",
        default_style: str = "storybook_classic",
    ) -> None:
        """
        Initialize the story engine.

        Args:
            text_generator: The LLM backend to use for text generation.
            default_target_age: Default target age range for stories.
            default_style: Default illustration style.
        """
        self._text_gen = text_generator
        self._default_target_age = default_target_age
        self._default_style = default_style
        self._state = ConversationState()

        # Import prompts here to avoid circular imports
        from storyteller.generation.prompts import (
            STORY_GUIDE_SYSTEM,
            STORY_START,
        )

        self._prompts = {
            "system": STORY_GUIDE_SYSTEM,
            "start": STORY_START,
        }

    @property
    def text_generator(self) -> TextGenerator:
        """Get the text generator instance."""
        return self._text_gen

    @property
    def model_name(self) -> str:
        """Get the current LLM model name."""
        return self._text_gen.model_name

    @property
    def conversation_state(self) -> ConversationState:
        """Get the current conversation state."""
        return self._state

    @property
    def current_story(self) -> Story | None:
        """Get the story being created."""
        return self._state.story

    def start_new_story(
        self,
        title: str = "",
        author: str = "",
        target_age: str | None = None,
        style: str | None = None,
    ) -> str:
        """
        Begin a new story creation session.

        Args:
            title: Initial story title (can be changed later).
            author: Story author name.
            target_age: Target age range (uses default if not specified).
            style: Illustration style (uses default if not specified).

        Returns:
            The opening prompt to present to the user.
        """
        self._state.clear()

        target_age = target_age or self._default_target_age
        style = style or self._default_style

        # Create initial story
        self._state.story = create_story(
            title=title or "Untitled Story",
            author=author,
            target_age=target_age,
            style=style,
        )
        self._state.current_phase = "ideation"

        # Build system prompt
        system_content = self._prompts["system"].render(
            target_age=target_age,
            style=style,
        )
        self._state.add_message("system", system_content)

        # Get the start prompt
        start_prompt = self._prompts["start"].render()
        self._state.add_message("assistant", start_prompt)

        logger.info("Started new story session with model %s", self.model_name)
        return start_prompt

    def process_user_input(self, user_input: str) -> str:
        """
        Process user input and generate a response.

        Args:
            user_input: The user's message.

        Returns:
            The LLM's response.
        """
        if not self._state.story:
            return self.start_new_story()

        self._state.add_message("user", user_input)

        # Convert to the format expected by the text generator
        from storyteller.generation.text import Message as GenMessage

        gen_messages = [
            GenMessage(role=m.role, content=m.content)
            for m in self._state.get_messages()
        ]

        response = self._text_gen.chat(gen_messages)  # type: ignore[arg-type]
        self._state.add_message("assistant", response)

        logger.debug("Processed user input, response length: %d", len(response))
        return response

    def generate_page_text(
        self,
        page_number: int,
        page_purpose: str,
        total_pages: int = 10,
    ) -> str:
        """
        Generate text for a specific page.

        Args:
            page_number: The page number (1-indexed).
            page_purpose: Description of what should happen on this page.
            total_pages: Total number of pages in the story.

        Returns:
            Generated page text.
        """
        if not self._state.story:
            raise ValueError("No active story. Call start_new_story() first.")

        from storyteller.generation.prompts import (
            PAGE_WRITER_SYSTEM,
            WRITE_PAGE_TEXT,
            format_previous_pages,
        )

        story = self._state.story

        # Get previous pages text
        previous = [
            (p.page_number, p.text)
            for p in story.pages
            if p.page_number < page_number and p.text
        ]

        # Get main character info
        character_name = "the main character"
        character_description = ""
        if story.characters:
            char = story.characters[0]
            character_name = char.name
            character_description = char.description

        # Build the prompt
        system = PAGE_WRITER_SYSTEM.render(
            target_age=story.metadata.target_age,
            title=story.metadata.title,
            style=story.metadata.style,
        )

        prompt = WRITE_PAGE_TEXT.render(
            page_number=page_number,
            total_pages=total_pages,
            title=story.metadata.title,
            character_name=character_name,
            character_description=character_description,
            setting="the story world",
            previous_text=format_previous_pages(previous),
            page_purpose=page_purpose,
            target_age=story.metadata.target_age,
        )

        response = self._text_gen.generate(prompt, system=system)

        # Clean up the response (remove quotes if present)
        text = response.strip().strip('"').strip("'")

        logger.info("Generated text for page %d: %s", page_number, text[:50])
        return text

    def generate_illustration_prompt(
        self,
        page_text: str,
        mood: str = "warm and friendly",
        time_of_day: str = "daytime",
    ) -> str:
        """
        Generate an illustration prompt for a page.

        Args:
            page_text: The text content of the page.
            mood: The mood/atmosphere for the illustration.
            time_of_day: Time of day for lighting.

        Returns:
            An illustration prompt for image generation.
        """
        if not self._state.story:
            raise ValueError("No active story. Call start_new_story() first.")

        from storyteller.generation.prompts import (
            GENERATE_ILLUSTRATION_PROMPT,
            ILLUSTRATION_PROMPT_SYSTEM,
            format_character_details,
        )

        story = self._state.story

        # Format character details
        if story.characters:
            char = story.characters[0]
            character_details = format_character_details(
                char.name,
                char.description,
                list(char.visual_traits),
            )
        else:
            character_details = "Main character to be illustrated"

        system = ILLUSTRATION_PROMPT_SYSTEM.render(style=story.metadata.style)

        prompt = GENERATE_ILLUSTRATION_PROMPT.render(
            page_text=page_text,
            character_details=character_details,
            setting="the story world",
            mood=mood,
            time_of_day=time_of_day,
            style=story.metadata.style,
        )

        response = self._text_gen.generate(prompt, system=system)
        logger.info("Generated illustration prompt: %s", response[:100])
        return response.strip()

    def add_character_to_story(
        self,
        name: str,
        description: str,
        visual_traits: list[str] | None = None,
    ) -> Story:
        """
        Add a character to the current story.

        Args:
            name: Character name.
            description: Character description.
            visual_traits: Visual traits for illustration consistency.

        Returns:
            The updated story.
        """
        if not self._state.story:
            raise ValueError("No active story. Call start_new_story() first.")

        character = create_character(name, description, visual_traits)
        self._state.story = add_character(self._state.story, character)

        logger.info("Added character: %s", name)
        return self._state.story

    def extract_visual_traits(self, name: str, description: str) -> list[str]:
        """
        Use the LLM to extract visual traits from a character description.

        Args:
            name: Character name.
            description: Character description.

        Returns:
            List of visual traits.
        """
        from storyteller.generation.prompts import EXTRACT_VISUAL_TRAITS

        prompt = EXTRACT_VISUAL_TRAITS.render(name=name, description=description)
        response = self._text_gen.generate(prompt)

        # Parse comma-separated traits
        traits = [t.strip() for t in response.split(",")]
        traits = [t for t in traits if t]  # Remove empty strings

        logger.info("Extracted %d visual traits for %s", len(traits), name)
        return traits

    def extract_characters_from_text(
        self,
        story_text: str,
    ) -> list[tuple[str, str, list[str]]]:
        """
        Use the LLM to extract character information from story text.

        Analyzes the provided text and identifies all characters, their
        descriptions, and visual traits for illustration consistency.

        Args:
            story_text: The story text to analyze.

        Returns:
            List of (name, description, visual_traits) tuples for each character.
        """
        from storyteller.generation.prompts import EXTRACT_CHARACTERS_FROM_TEXT

        prompt = EXTRACT_CHARACTERS_FROM_TEXT.render(story_text=story_text)
        response = self._text_gen.generate(prompt)

        characters: list[tuple[str, str, list[str]]] = []

        # Parse the response - one character per line
        for line in response.strip().split("\n"):
            line = line.strip()
            if not line or line.upper() == "NONE":
                continue

            # Parse: NAME | DESCRIPTION | VISUAL_TRAITS
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 3:
                name = parts[0]
                description = parts[1]
                traits = [t.strip() for t in parts[2].split(",") if t.strip()]
                characters.append((name, description, traits))
            elif len(parts) == 2:
                # No traits provided
                name = parts[0]
                description = parts[1]
                characters.append((name, description, []))

        logger.info("Extracted %d characters from text", len(characters))
        return characters

    def add_page_to_story(
        self,
        page_number: int,
        text: str,
        illustration_prompt: str = "",
    ) -> Story:
        """
        Add a page to the current story.

        Args:
            page_number: The page number.
            text: The page text.
            illustration_prompt: Optional illustration prompt.

        Returns:
            The updated story.
        """
        if not self._state.story:
            raise ValueError("No active story. Call start_new_story() first.")

        page = create_page(page_number, text, illustration_prompt)
        self._state.story = add_page(self._state.story, page)

        logger.info("Added page %d to story", page_number)
        return self._state.story

    def update_story_page(
        self,
        page_number: int,
        text: str | None = None,
        illustration_prompt: str | None = None,
    ) -> Story:
        """
        Update an existing page in the story.

        Args:
            page_number: The page number to update.
            text: New text (or None to keep existing).
            illustration_prompt: New illustration prompt (or None to keep existing).

        Returns:
            The updated story.
        """
        if not self._state.story:
            raise ValueError("No active story. Call start_new_story() first.")

        updates = {}
        if text is not None:
            updates["text"] = text
        if illustration_prompt is not None:
            updates["illustration_prompt"] = illustration_prompt

        if updates:
            self._state.story = update_page(self._state.story, page_number, **updates)
            logger.info("Updated page %d", page_number)

        return self._state.story

    def update_story_metadata(self, **kwargs: str) -> Story:
        """
        Update story metadata.

        Args:
            **kwargs: Metadata fields to update (title, author, target_age, style).

        Returns:
            The updated story.
        """
        if not self._state.story:
            raise ValueError("No active story. Call start_new_story() first.")

        self._state.story = self._state.story.with_metadata(**kwargs)
        logger.info("Updated story metadata: %s", list(kwargs.keys()))
        return self._state.story

    def set_story(self, story: Story) -> None:
        """
        Set the current story (for loading existing stories).

        Args:
            story: The story to work with.
        """
        self._state.story = story
        self._state.current_phase = "editing"
        logger.info("Set story: %s", story.title)

    def get_story(self) -> Story | None:
        """
        Get the current story.

        Returns:
            The current story, or None if no story is active.
        """
        return self._state.story
