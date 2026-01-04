"""
Tests for the story data models and factory functions.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import datetime
from pathlib import Path

import pytest

from storyteller.core import (
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


class TestCharacter:
    """Tests for the Character dataclass."""

    def test_create_character_basic(self) -> None:
        """Character can be created with basic attributes."""
        character = create_character(
            name="Luna",
            description="A curious mouse",
        )
        assert character.name == "Luna"
        assert character.description == "A curious mouse"
        assert character.visual_traits == ()

    def test_create_character_with_traits(self) -> None:
        """Character can be created with visual traits."""
        character = create_character(
            name="Luna",
            description="A curious mouse",
            visual_traits=["brown fur", "big eyes"],
        )
        assert character.visual_traits == ("brown fur", "big eyes")

    def test_character_is_immutable(self, sample_character: Character) -> None:
        """Character instances are frozen and cannot be modified."""
        with pytest.raises(FrozenInstanceError):
            sample_character.name = "New Name"  # type: ignore[misc]

    def test_character_with_updates(self, sample_character: Character) -> None:
        """with_updates returns a new Character with modified fields."""
        updated = sample_character.with_updates(name="New Name")
        assert updated.name == "New Name"
        assert updated.description == sample_character.description
        # Original unchanged
        assert sample_character.name == "Luna"


class TestPage:
    """Tests for the Page dataclass."""

    def test_create_page_basic(self) -> None:
        """Page can be created with basic attributes."""
        page = create_page(page_number=1, text="Hello world")
        assert page.page_number == 1
        assert page.text == "Hello world"
        assert page.illustration_prompt == ""
        assert page.illustration_path is None

    def test_create_page_with_prompt(self) -> None:
        """Page can be created with illustration prompt."""
        page = create_page(
            page_number=1,
            text="Hello world",
            illustration_prompt="A sunny day",
        )
        assert page.illustration_prompt == "A sunny day"

    def test_page_is_immutable(self, sample_page: Page) -> None:
        """Page instances are frozen."""
        with pytest.raises(FrozenInstanceError):
            sample_page.text = "New text"  # type: ignore[misc]

    def test_page_with_updates(self, sample_page: Page) -> None:
        """with_updates returns a new Page with modified fields."""
        updated = sample_page.with_updates(text="New text")
        assert updated.text == "New text"
        assert updated.page_number == sample_page.page_number
        # Original unchanged
        assert sample_page.text == "Once upon a time, there was a little mouse named Luna."

    def test_has_illustration_without_path(self, sample_page: Page) -> None:
        """has_illustration returns False when no path is set."""
        assert sample_page.has_illustration() is False

    def test_has_illustration_with_nonexistent_path(self, sample_page: Page) -> None:
        """has_illustration returns False when path doesn't exist."""
        page = sample_page.with_updates(illustration_path=Path("/nonexistent/image.png"))
        assert page.has_illustration() is False

    def test_has_illustration_with_existing_path(
        self, sample_page: Page, tmp_path: Path
    ) -> None:
        """has_illustration returns True when path exists."""
        image_path = tmp_path / "test.png"
        image_path.touch()
        page = sample_page.with_updates(illustration_path=image_path)
        assert page.has_illustration() is True


class TestStoryMetadata:
    """Tests for the StoryMetadata dataclass."""

    def test_create_metadata_defaults(self) -> None:
        """Metadata has sensible defaults."""
        metadata = StoryMetadata(title="Test")
        assert metadata.title == "Test"
        assert metadata.author == ""
        assert metadata.target_age == "5-8"
        assert metadata.style == "storybook_classic"
        assert isinstance(metadata.created_at, datetime)
        assert isinstance(metadata.modified_at, datetime)

    def test_metadata_is_immutable(self, sample_metadata: StoryMetadata) -> None:
        """Metadata instances are frozen."""
        with pytest.raises(FrozenInstanceError):
            sample_metadata.title = "New Title"  # type: ignore[misc]

    def test_metadata_with_updates_sets_modified_at(
        self, sample_metadata: StoryMetadata
    ) -> None:
        """with_updates automatically updates modified_at."""
        original_modified = sample_metadata.modified_at
        updated = sample_metadata.with_updates(title="New Title")
        assert updated.title == "New Title"
        assert updated.modified_at > original_modified


class TestStory:
    """Tests for the Story dataclass."""

    def test_create_story_empty(self) -> None:
        """Create an empty story."""
        story = create_story(title="Test Story")
        assert story.title == "Test Story"
        assert story.page_count == 0
        assert len(story.characters) == 0
        assert story.project_path is None

    def test_story_title_property(self, sample_story: Story) -> None:
        """title property returns metadata title."""
        assert sample_story.title == "Luna's Adventure"

    def test_story_page_count(self, sample_story: Story) -> None:
        """page_count returns correct count."""
        assert sample_story.page_count == 2

    def test_get_page_found(self, sample_story: Story) -> None:
        """get_page returns the correct page."""
        page = sample_story.get_page(1)
        assert page is not None
        assert page.page_number == 1

    def test_get_page_not_found(self, sample_story: Story) -> None:
        """get_page returns None for nonexistent page."""
        assert sample_story.get_page(999) is None

    def test_get_character_found(self, sample_story: Story) -> None:
        """get_character returns the correct character."""
        character = sample_story.get_character("Luna")
        assert character is not None
        assert character.name == "Luna"

    def test_get_character_case_insensitive(self, sample_story: Story) -> None:
        """get_character is case-insensitive."""
        assert sample_story.get_character("luna") is not None
        assert sample_story.get_character("LUNA") is not None

    def test_get_character_not_found(self, sample_story: Story) -> None:
        """get_character returns None for unknown character."""
        assert sample_story.get_character("Unknown") is None

    def test_with_metadata(self, sample_story: Story) -> None:
        """with_metadata creates new story with updated metadata."""
        updated = sample_story.with_metadata(title="New Title")
        assert updated.title == "New Title"
        assert sample_story.title == "Luna's Adventure"  # Original unchanged

    def test_with_project_path(self, sample_story: Story, tmp_path: Path) -> None:
        """with_project_path sets the project path."""
        updated = sample_story.with_project_path(tmp_path)
        assert updated.project_path == tmp_path
        assert sample_story.project_path is None  # Original unchanged


class TestStoryFactoryFunctions:
    """Tests for story manipulation factory functions."""

    def test_add_character(
        self, empty_story: Story, sample_character: Character
    ) -> None:
        """add_character adds a character to the story."""
        updated = add_character(empty_story, sample_character)
        assert len(updated.characters) == 1
        assert updated.characters[0].name == "Luna"
        assert len(empty_story.characters) == 0  # Original unchanged

    def test_remove_character(
        self, sample_story: Story
    ) -> None:
        """remove_character removes a character by name."""
        assert sample_story.get_character("Luna") is not None
        updated = remove_character(sample_story, "Luna")
        assert updated.get_character("Luna") is None
        assert sample_story.get_character("Luna") is not None  # Original unchanged

    def test_remove_character_case_insensitive(self, sample_story: Story) -> None:
        """remove_character is case-insensitive."""
        updated = remove_character(sample_story, "luna")
        assert updated.get_character("Luna") is None

    def test_add_page(self, empty_story: Story, sample_page: Page) -> None:
        """add_page adds a page to the story."""
        updated = add_page(empty_story, sample_page)
        assert updated.page_count == 1
        assert updated.pages[0].page_number == 1
        assert empty_story.page_count == 0  # Original unchanged

    def test_add_page_maintains_order(self, empty_story: Story) -> None:
        """add_page inserts pages in order by page_number."""
        story = add_page(empty_story, create_page(page_number=3, text="Third"))
        story = add_page(story, create_page(page_number=1, text="First"))
        story = add_page(story, create_page(page_number=2, text="Second"))

        assert story.pages[0].page_number == 1
        assert story.pages[1].page_number == 2
        assert story.pages[2].page_number == 3

    def test_update_page(self, sample_story: Story) -> None:
        """update_page updates a specific page."""
        updated = update_page(sample_story, 1, text="Updated text")
        page = updated.get_page(1)
        assert page is not None
        assert page.text == "Updated text"
        # Original unchanged
        original_page = sample_story.get_page(1)
        assert original_page is not None
        assert original_page.text != "Updated text"

    def test_update_page_not_found(self, sample_story: Story) -> None:
        """update_page raises ValueError for nonexistent page."""
        with pytest.raises(ValueError, match="Page 999 not found"):
            update_page(sample_story, 999, text="Updated")

    def test_remove_page(self, sample_story: Story) -> None:
        """remove_page removes a page by number."""
        assert sample_story.page_count == 2
        updated = remove_page(sample_story, 1)
        assert updated.page_count == 1
        assert updated.get_page(1) is None
        assert updated.get_page(2) is not None
        assert sample_story.page_count == 2  # Original unchanged

    def test_renumber_pages(self, sample_story: Story) -> None:
        """renumber_pages creates sequential numbering."""
        # Remove page 1, leaving gap
        story = remove_page(sample_story, 1)
        assert story.pages[0].page_number == 2

        # Renumber
        renumbered = renumber_pages(story)
        assert renumbered.pages[0].page_number == 1


class TestConstants:
    """Tests for module constants."""

    def test_illustration_styles_not_empty(self) -> None:
        """ILLUSTRATION_STYLES contains values."""
        assert len(ILLUSTRATION_STYLES) > 0
        assert "watercolor" in ILLUSTRATION_STYLES
        assert "cartoon" in ILLUSTRATION_STYLES

    def test_target_age_ranges_not_empty(self) -> None:
        """TARGET_AGE_RANGES contains values."""
        assert len(TARGET_AGE_RANGES) > 0
        assert "5-8" in TARGET_AGE_RANGES
