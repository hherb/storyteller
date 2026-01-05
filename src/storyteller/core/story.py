"""
Core data models for Storyteller.

This module defines the immutable data structures used throughout the application
for representing stories, pages, and characters.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ConversationMessage:
    """
    A single message in the story creation conversation.

    Attributes:
        role: Who sent the message ('user' or 'assistant').
        content: The text content of the message.
        timestamp: When the message was created.
    """

    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class Character:
    """
    A character in the story with visual consistency traits.

    Attributes:
        name: The character's name as used in the story.
        description: Natural language description of the character.
        visual_traits: Tuple of visual descriptors for image generation consistency.
    """

    name: str
    description: str
    visual_traits: tuple[str, ...] = field(default_factory=tuple)

    def with_updates(self, **kwargs: Any) -> Character:
        """
        Return a new Character with the specified fields updated.

        Args:
            **kwargs: Fields to update (name, description, visual_traits).

        Returns:
            A new Character instance with updated fields.
        """
        return replace(self, **kwargs)

    def to_prompt_fragment(self) -> str:
        """
        Convert visual traits to a prompt fragment for image generation.

        Returns:
            A comma-separated string of visual traits, or an empty string
            if no traits are defined.

        Example:
            >>> char = Character("Luna", "A brave mouse", ("small brown mouse", "red scarf"))
            >>> char.to_prompt_fragment()
            'small brown mouse, red scarf'
        """
        return ", ".join(self.visual_traits) if self.visual_traits else ""

    def appears_in_text(self, text: str) -> bool:
        """
        Check if this character's name appears in the given text.

        Uses case-insensitive matching.

        Args:
            text: The text to search.

        Returns:
            True if the character's name appears in the text.
        """
        return self.name.lower() in text.lower()


@dataclass(frozen=True)
class Page:
    """
    A single page in the storybook.

    Attributes:
        page_number: The 1-indexed page number.
        text: The story text displayed on this page.
        illustration_prompt: Prompt used for generating the illustration.
        illustration_path: Path to the generated illustration, or None if not yet generated.
    """

    page_number: int
    text: str
    illustration_prompt: str = ""
    illustration_path: Path | None = None

    def with_updates(self, **kwargs: Any) -> Page:
        """
        Return a new Page with the specified fields updated.

        Args:
            **kwargs: Fields to update.

        Returns:
            A new Page instance with updated fields.
        """
        return replace(self, **kwargs)

    def has_illustration(self) -> bool:
        """
        Check if this page has a generated illustration.

        Returns:
            True if an illustration path is set and the file exists.
        """
        return self.illustration_path is not None and self.illustration_path.exists()


@dataclass(frozen=True)
class StoryMetadata:
    """
    Metadata about a story project.

    Attributes:
        title: The story's title.
        author: Name of the story creator.
        target_age: Target age range (e.g., "2-5", "5-8", "6-10").
        created_at: When the story was first created.
        modified_at: When the story was last modified.
        style: Illustration style preset (e.g., "watercolor", "cartoon").
    """

    title: str
    author: str = ""
    target_age: str = "5-8"
    created_at: datetime = field(default_factory=datetime.now)
    modified_at: datetime = field(default_factory=datetime.now)
    style: str = "storybook_classic"

    def with_updates(self, **kwargs: Any) -> StoryMetadata:
        """
        Return new StoryMetadata with the specified fields updated.

        Automatically updates modified_at to current time.

        Args:
            **kwargs: Fields to update.

        Returns:
            A new StoryMetadata instance with updated fields.
        """
        if "modified_at" not in kwargs:
            kwargs["modified_at"] = datetime.now()
        return replace(self, **kwargs)


# Valid style presets for illustrations
ILLUSTRATION_STYLES: tuple[str, ...] = (
    "watercolor",
    "cartoon",
    "storybook_classic",
    "modern_digital",
    "pencil_sketch",
)

# Valid target age ranges
TARGET_AGE_RANGES: tuple[str, ...] = (
    "2-5",
    "5-8",
    "6-10",
)


@dataclass(frozen=True)
class Story:
    """
    A complete story with all pages and characters.

    Attributes:
        metadata: Story metadata (title, author, etc.).
        characters: Tuple of characters appearing in the story.
        pages: Tuple of pages in reading order.
        conversation: Tuple of conversation messages from story creation.
        project_path: Directory where the story is saved, or None if unsaved.
    """

    metadata: StoryMetadata
    characters: tuple[Character, ...] = field(default_factory=tuple)
    pages: tuple[Page, ...] = field(default_factory=tuple)
    conversation: tuple[ConversationMessage, ...] = field(default_factory=tuple)
    project_path: Path | None = None

    @property
    def title(self) -> str:
        """Get the story title."""
        return self.metadata.title

    @property
    def page_count(self) -> int:
        """Get the number of pages in the story."""
        return len(self.pages)

    def get_page(self, page_number: int) -> Page | None:
        """
        Get a page by its page number.

        Args:
            page_number: The 1-indexed page number.

        Returns:
            The Page if found, None otherwise.
        """
        for page in self.pages:
            if page.page_number == page_number:
                return page
        return None

    def get_character(self, name: str) -> Character | None:
        """
        Get a character by name (case-insensitive).

        Args:
            name: The character's name.

        Returns:
            The Character if found, None otherwise.
        """
        name_lower = name.lower()
        for character in self.characters:
            if character.name.lower() == name_lower:
                return character
        return None

    def with_metadata(self, **kwargs: Any) -> Story:
        """
        Return a new Story with updated metadata.

        Args:
            **kwargs: Metadata fields to update.

        Returns:
            A new Story with updated metadata.
        """
        return replace(self, metadata=self.metadata.with_updates(**kwargs))

    def with_project_path(self, path: Path) -> Story:
        """
        Return a new Story with the project path set.

        Args:
            path: The directory path for the story project.

        Returns:
            A new Story with the project path set.
        """
        return replace(self, project_path=path)


def create_story(
    title: str,
    author: str = "",
    target_age: str = "5-8",
    style: str = "storybook_classic",
) -> Story:
    """
    Create a new empty story with the given metadata.

    Args:
        title: The story's title.
        author: Name of the story creator.
        target_age: Target age range for the story.
        style: Illustration style preset.

    Returns:
        A new Story instance with empty pages and characters.
    """
    metadata = StoryMetadata(
        title=title,
        author=author,
        target_age=target_age,
        style=style,
    )
    return Story(metadata=metadata)


def add_character(story: Story, character: Character) -> Story:
    """
    Return a new Story with the character added.

    Args:
        story: The original story.
        character: The character to add.

    Returns:
        A new Story with the character added to the characters tuple.
    """
    return replace(
        story,
        characters=story.characters + (character,),
        metadata=story.metadata.with_updates(),
    )


def remove_character(story: Story, name: str) -> Story:
    """
    Return a new Story with the named character removed.

    Args:
        story: The original story.
        name: The name of the character to remove (case-insensitive).

    Returns:
        A new Story with the character removed.
    """
    name_lower = name.lower()
    new_characters = tuple(c for c in story.characters if c.name.lower() != name_lower)
    return replace(
        story,
        characters=new_characters,
        metadata=story.metadata.with_updates(),
    )


def add_page(story: Story, page: Page) -> Story:
    """
    Return a new Story with the page added.

    The page is inserted in order by page_number, or appended if it has
    the highest page number.

    Args:
        story: The original story.
        page: The page to add.

    Returns:
        A new Story with the page added.
    """
    pages = list(story.pages)
    pages.append(page)
    pages.sort(key=lambda p: p.page_number)
    return replace(
        story,
        pages=tuple(pages),
        metadata=story.metadata.with_updates(),
    )


def update_page(story: Story, page_number: int, **kwargs: Any) -> Story:
    """
    Return a new Story with the specified page updated.

    Args:
        story: The original story.
        page_number: The page number to update.
        **kwargs: Page fields to update.

    Returns:
        A new Story with the page updated.

    Raises:
        ValueError: If the page number is not found.
    """
    new_pages: list[Page] = []
    found = False

    for page in story.pages:
        if page.page_number == page_number:
            new_pages.append(page.with_updates(**kwargs))
            found = True
        else:
            new_pages.append(page)

    if not found:
        raise ValueError(f"Page {page_number} not found in story")

    return replace(
        story,
        pages=tuple(new_pages),
        metadata=story.metadata.with_updates(),
    )


def remove_page(story: Story, page_number: int) -> Story:
    """
    Return a new Story with the specified page removed.

    Note: This does not renumber remaining pages.

    Args:
        story: The original story.
        page_number: The page number to remove.

    Returns:
        A new Story with the page removed.
    """
    new_pages = tuple(p for p in story.pages if p.page_number != page_number)
    return replace(
        story,
        pages=new_pages,
        metadata=story.metadata.with_updates(),
    )


def renumber_pages(story: Story) -> Story:
    """
    Return a new Story with pages renumbered sequentially from 1.

    Useful after removing pages to close gaps in numbering.

    Args:
        story: The original story.

    Returns:
        A new Story with pages renumbered 1, 2, 3, etc.
    """
    new_pages = tuple(replace(page, page_number=i + 1) for i, page in enumerate(story.pages))
    return replace(
        story,
        pages=new_pages,
        metadata=story.metadata.with_updates(),
    )


def create_page(
    page_number: int,
    text: str = "",
    illustration_prompt: str = "",
) -> Page:
    """
    Create a new page with the given content.

    Args:
        page_number: The 1-indexed page number.
        text: The story text for this page.
        illustration_prompt: The prompt for generating the illustration.

    Returns:
        A new Page instance.
    """
    return Page(
        page_number=page_number,
        text=text,
        illustration_prompt=illustration_prompt,
    )


def create_character(
    name: str,
    description: str,
    visual_traits: list[str] | None = None,
) -> Character:
    """
    Create a new character.

    Args:
        name: The character's name.
        description: Natural language description.
        visual_traits: List of visual descriptors for image consistency.

    Returns:
        A new Character instance.
    """
    traits = tuple(visual_traits) if visual_traits else ()
    return Character(
        name=name,
        description=description,
        visual_traits=traits,
    )
