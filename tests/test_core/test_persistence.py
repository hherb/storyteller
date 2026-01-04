"""
Tests for the persistence layer (save/load stories).
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import pytest

from storyteller.core import (
    Story,
    add_page,
    create_page,
    create_story,
    delete_story,
    get_export_path,
    get_page_illustration_path,
    list_stories,
    load_story,
    save_story,
)
from storyteller.core.persistence import (
    SCHEMA_VERSION,
    create_project_directory,
    dict_to_story,
    slugify,
    story_to_dict,
)


class TestSlugify:
    """Tests for the slugify function."""

    def test_basic_slugify(self) -> None:
        """Basic text is converted to slug."""
        assert slugify("Hello World") == "hello-world"

    def test_special_characters_removed(self) -> None:
        """Special characters are removed."""
        assert slugify("Luna's Adventure!") == "lunas-adventure"

    def test_multiple_spaces(self) -> None:
        """Multiple spaces become single hyphens."""
        assert slugify("Hello   World") == "hello-world"

    def test_leading_trailing_spaces(self) -> None:
        """Leading/trailing spaces are removed."""
        assert slugify("  Hello World  ") == "hello-world"

    def test_empty_becomes_untitled(self) -> None:
        """Empty string becomes 'untitled'."""
        assert slugify("") == "untitled"
        assert slugify("!!!") == "untitled"

    def test_numbers_preserved(self) -> None:
        """Numbers are preserved in slugs."""
        assert slugify("Story 123") == "story-123"


class TestStoryToDict:
    """Tests for story serialization."""

    def test_basic_serialization(self, sample_story: Story) -> None:
        """Story is correctly serialized to dict."""
        data = story_to_dict(sample_story)

        assert data["version"] == SCHEMA_VERSION
        assert data["metadata"]["title"] == "Luna's Adventure"
        assert data["metadata"]["author"] == "Test Author"
        assert len(data["characters"]) == 1
        assert len(data["pages"]) == 2

    def test_serialization_is_json_compatible(self, sample_story: Story) -> None:
        """Serialized story can be converted to JSON."""
        data = story_to_dict(sample_story)
        json_str = json.dumps(data)
        assert isinstance(json_str, str)

    def test_pages_serialization(self, sample_story: Story) -> None:
        """Pages are correctly serialized."""
        data = story_to_dict(sample_story)
        page_data = data["pages"][0]

        assert page_data["page_number"] == 1
        assert "Luna" in page_data["text"]
        assert "illustration_prompt" in page_data


class TestDictToStory:
    """Tests for story deserialization."""

    def test_basic_deserialization(self, sample_story: Story) -> None:
        """Story can be round-tripped through dict."""
        data = story_to_dict(sample_story)
        restored = dict_to_story(data)

        assert restored.title == sample_story.title
        assert restored.metadata.author == sample_story.metadata.author
        assert len(restored.characters) == len(sample_story.characters)
        assert len(restored.pages) == len(sample_story.pages)

    def test_character_deserialization(self, sample_story: Story) -> None:
        """Characters are correctly deserialized."""
        data = story_to_dict(sample_story)
        restored = dict_to_story(data)

        character = restored.get_character("Luna")
        assert character is not None
        assert character.description == sample_story.characters[0].description

    def test_page_deserialization(self, sample_story: Story) -> None:
        """Pages are correctly deserialized."""
        data = story_to_dict(sample_story)
        restored = dict_to_story(data)

        page = restored.get_page(1)
        original_page = sample_story.get_page(1)
        assert page is not None
        assert original_page is not None
        assert page.text == original_page.text

    def test_deserialization_with_project_path(
        self, sample_story: Story, tmp_path: Path
    ) -> None:
        """Illustration paths are resolved relative to project path."""
        # Add a page with illustration path
        story = add_page(
            sample_story,
            create_page(
                page_number=3,
                text="Test",
            ).with_updates(illustration_path=tmp_path / "pages" / "page_03.png"),
        )

        data = story_to_dict(story)
        # The path in the dict should be just the filename
        assert data["pages"][2]["illustration_path"] == "page_03.png"

        # When deserializing, path should be resolved
        restored = dict_to_story(data, project_path=tmp_path)
        page = restored.get_page(3)
        assert page is not None
        assert page.illustration_path == tmp_path / "pages" / "page_03.png"


class TestCreateProjectDirectory:
    """Tests for project directory creation."""

    def test_creates_directory_structure(self, empty_story: Story, tmp_path: Path) -> None:
        """Project directory structure is created correctly."""
        project_dir = create_project_directory(empty_story, base_dir=tmp_path)

        assert project_dir.exists()
        assert (project_dir / "pages").exists()
        assert (project_dir / "exports").exists()

    def test_handles_name_collision(self, tmp_path: Path) -> None:
        """Duplicate names get numbered suffixes."""
        story1 = create_story(title="Test Story")
        story2 = create_story(title="Test Story")

        dir1 = create_project_directory(story1, base_dir=tmp_path)
        dir2 = create_project_directory(story2, base_dir=tmp_path)

        assert dir1 != dir2
        assert dir1.name == "test-story"
        assert dir2.name == "test-story-1"


class TestSaveStory:
    """Tests for saving stories."""

    def test_save_creates_json(self, sample_story: Story, tmp_path: Path) -> None:
        """save_story creates story.json file."""
        saved = save_story(sample_story, project_path=tmp_path / "test-story")

        story_file = saved.project_path / "story.json"  # type: ignore[operator]
        assert story_file.exists()

    def test_save_returns_story_with_path(
        self, sample_story: Story, tmp_path: Path
    ) -> None:
        """save_story returns story with project_path set."""
        saved = save_story(sample_story, project_path=tmp_path / "test-story")

        assert saved.project_path is not None
        assert saved.project_path.exists()

    def test_save_without_path_creates_directory(
        self, sample_story: Story, temp_stories_dir: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """save_story creates directory when no path given."""
        # Patch get_stories_directory to use temp dir
        monkeypatch.setattr(
            "storyteller.core.persistence.get_stories_directory",
            lambda: temp_stories_dir,
        )

        saved = save_story(sample_story)

        assert saved.project_path is not None
        assert saved.project_path.parent == temp_stories_dir

    def test_save_updates_modified_at(self, sample_story: Story, tmp_path: Path) -> None:
        """save_story updates the modified_at timestamp."""
        original_modified = sample_story.metadata.modified_at
        saved = save_story(sample_story, project_path=tmp_path / "test-story")

        assert saved.metadata.modified_at >= original_modified

    def test_save_preserves_content(self, sample_story: Story, tmp_path: Path) -> None:
        """Saved story can be loaded with same content."""
        saved = save_story(sample_story, project_path=tmp_path / "test-story")
        loaded = load_story(saved.project_path)  # type: ignore[arg-type]

        assert loaded.title == sample_story.title
        assert len(loaded.pages) == len(sample_story.pages)
        assert len(loaded.characters) == len(sample_story.characters)


class TestLoadStory:
    """Tests for loading stories."""

    def test_load_existing_story(self, sample_story: Story, tmp_path: Path) -> None:
        """load_story loads a saved story correctly."""
        project_path = tmp_path / "test-story"
        save_story(sample_story, project_path=project_path)

        loaded = load_story(project_path)

        assert loaded.title == sample_story.title
        assert loaded.project_path == project_path

    def test_load_nonexistent_raises(self, tmp_path: Path) -> None:
        """load_story raises FileNotFoundError for missing story."""
        with pytest.raises(FileNotFoundError):
            load_story(tmp_path / "nonexistent")

    def test_load_preserves_characters(self, sample_story: Story, tmp_path: Path) -> None:
        """Loaded story has all characters."""
        project_path = tmp_path / "test-story"
        save_story(sample_story, project_path=project_path)

        loaded = load_story(project_path)
        character = loaded.get_character("Luna")

        assert character is not None
        assert character.visual_traits == sample_story.characters[0].visual_traits

    def test_load_preserves_pages(self, sample_story: Story, tmp_path: Path) -> None:
        """Loaded story has all pages with content."""
        project_path = tmp_path / "test-story"
        save_story(sample_story, project_path=project_path)

        loaded = load_story(project_path)

        for i in range(1, sample_story.page_count + 1):
            original = sample_story.get_page(i)
            loaded_page = loaded.get_page(i)
            assert original is not None
            assert loaded_page is not None
            assert loaded_page.text == original.text
            assert loaded_page.illustration_prompt == original.illustration_prompt


class TestListStories:
    """Tests for listing stories."""

    def test_list_empty_directory(self, temp_stories_dir: Path) -> None:
        """list_stories returns empty list for empty directory."""
        stories = list_stories(base_dir=temp_stories_dir)
        assert stories == []

    def test_list_finds_stories(self, temp_stories_dir: Path) -> None:
        """list_stories finds saved stories."""
        story1 = create_story(title="Story One")
        story2 = create_story(title="Story Two")

        save_story(story1, project_path=temp_stories_dir / "story-one")
        save_story(story2, project_path=temp_stories_dir / "story-two")

        stories = list_stories(base_dir=temp_stories_dir)

        assert len(stories) == 2
        titles = [meta.title for _, meta in stories]
        assert "Story One" in titles
        assert "Story Two" in titles

    def test_list_sorted_by_modified(self, temp_stories_dir: Path) -> None:
        """list_stories returns stories sorted by modified_at descending."""
        story1 = create_story(title="Old Story")
        story2 = create_story(title="New Story")

        save_story(story1, project_path=temp_stories_dir / "old-story")
        # Small delay to ensure different modified times
        import time
        time.sleep(0.01)
        save_story(story2, project_path=temp_stories_dir / "new-story")

        stories = list_stories(base_dir=temp_stories_dir)

        # Newest first
        assert stories[0][1].title == "New Story"
        assert stories[1][1].title == "Old Story"

    def test_list_skips_invalid_directories(self, temp_stories_dir: Path) -> None:
        """list_stories skips directories without valid story.json."""
        # Create a valid story
        story = create_story(title="Valid Story")
        save_story(story, project_path=temp_stories_dir / "valid-story")

        # Create an invalid directory
        invalid_dir = temp_stories_dir / "invalid-story"
        invalid_dir.mkdir()
        (invalid_dir / "story.json").write_text("not valid json")

        stories = list_stories(base_dir=temp_stories_dir)

        assert len(stories) == 1
        assert stories[0][1].title == "Valid Story"


class TestDeleteStory:
    """Tests for deleting stories."""

    def test_delete_removes_directory(self, sample_story: Story, tmp_path: Path) -> None:
        """delete_story removes the project directory."""
        project_path = tmp_path / "test-story"
        save_story(sample_story, project_path=project_path)

        assert project_path.exists()
        delete_story(project_path)
        assert not project_path.exists()

    def test_delete_nonexistent_raises(self, tmp_path: Path) -> None:
        """delete_story raises for nonexistent project."""
        with pytest.raises(FileNotFoundError):
            delete_story(tmp_path / "nonexistent")


class TestPathHelpers:
    """Tests for path helper functions."""

    def test_get_page_illustration_path(self, sample_story: Story, tmp_path: Path) -> None:
        """get_page_illustration_path returns correct path."""
        story = sample_story.with_project_path(tmp_path)
        path = get_page_illustration_path(story, 1)

        assert path == tmp_path / "pages" / "page_01.png"

    def test_get_page_illustration_path_padding(
        self, sample_story: Story, tmp_path: Path
    ) -> None:
        """Page numbers are zero-padded."""
        story = sample_story.with_project_path(tmp_path)

        assert get_page_illustration_path(story, 1).name == "page_01.png"
        assert get_page_illustration_path(story, 10).name == "page_10.png"

    def test_get_page_illustration_path_requires_saved(
        self, sample_story: Story
    ) -> None:
        """get_page_illustration_path raises for unsaved story."""
        with pytest.raises(ValueError, match="must be saved"):
            get_page_illustration_path(sample_story, 1)

    def test_get_export_path(self, sample_story: Story, tmp_path: Path) -> None:
        """get_export_path returns correct path."""
        story = sample_story.with_project_path(tmp_path)
        path = get_export_path(story, "my-story.pdf")

        assert path == tmp_path / "exports" / "my-story.pdf"

    def test_get_export_path_requires_saved(self, sample_story: Story) -> None:
        """get_export_path raises for unsaved story."""
        with pytest.raises(ValueError, match="must be saved"):
            get_export_path(sample_story, "export.pdf")
