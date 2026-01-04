"""
Persistence layer for saving and loading stories.

This module handles serialization of Story objects to JSON and manages
the project directory structure on disk.
"""

from __future__ import annotations

import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from .story import (
    Character,
    Page,
    Story,
    StoryMetadata,
)

logger = logging.getLogger(__name__)

# JSON schema version for future compatibility
SCHEMA_VERSION = "1.0"

# Default stories directory
DEFAULT_STORIES_DIR = Path.home() / "Storyteller" / "stories"


def get_stories_directory() -> Path:
    """
    Get the default stories directory, creating it if necessary.

    Returns:
        Path to the stories directory.
    """
    DEFAULT_STORIES_DIR.mkdir(parents=True, exist_ok=True)
    return DEFAULT_STORIES_DIR


def slugify(text: str) -> str:
    """
    Convert text to a filesystem-safe slug.

    Args:
        text: The text to convert.

    Returns:
        A lowercase string with spaces replaced by hyphens and
        special characters removed.
    """
    # Convert to lowercase and replace spaces with hyphens
    slug = text.lower().strip().replace(" ", "-")
    # Remove any character that isn't alphanumeric or hyphen
    slug = re.sub(r"[^a-z0-9\-]", "", slug)
    # Remove multiple consecutive hyphens
    slug = re.sub(r"-+", "-", slug)
    # Remove leading/trailing hyphens
    slug = slug.strip("-")
    return slug or "untitled"


def _datetime_to_iso(dt: datetime) -> str:
    """Convert datetime to ISO format string."""
    return dt.isoformat()


def _iso_to_datetime(iso_str: str) -> datetime:
    """Parse ISO format string to datetime."""
    return datetime.fromisoformat(iso_str)


def _character_to_dict(character: Character) -> dict[str, Any]:
    """Convert a Character to a JSON-serializable dict."""
    return {
        "name": character.name,
        "description": character.description,
        "visual_traits": list(character.visual_traits),
    }


def _dict_to_character(data: dict[str, Any]) -> Character:
    """Convert a dict to a Character."""
    return Character(
        name=data["name"],
        description=data["description"],
        visual_traits=tuple(data.get("visual_traits", [])),
    )


def _page_to_dict(page: Page) -> dict[str, Any]:
    """Convert a Page to a JSON-serializable dict."""
    return {
        "page_number": page.page_number,
        "text": page.text,
        "illustration_prompt": page.illustration_prompt,
        "illustration_path": str(page.illustration_path.name) if page.illustration_path else None,
    }


def _dict_to_page(data: dict[str, Any], pages_dir: Path | None = None) -> Page:
    """Convert a dict to a Page."""
    illustration_path: Path | None = None
    if data.get("illustration_path") and pages_dir:
        illustration_path = pages_dir / data["illustration_path"]

    return Page(
        page_number=data["page_number"],
        text=data["text"],
        illustration_prompt=data.get("illustration_prompt", ""),
        illustration_path=illustration_path,
    )


def _metadata_to_dict(metadata: StoryMetadata) -> dict[str, Any]:
    """Convert StoryMetadata to a JSON-serializable dict."""
    return {
        "title": metadata.title,
        "author": metadata.author,
        "target_age": metadata.target_age,
        "created_at": _datetime_to_iso(metadata.created_at),
        "modified_at": _datetime_to_iso(metadata.modified_at),
        "style": metadata.style,
    }


def _dict_to_metadata(data: dict[str, Any]) -> StoryMetadata:
    """Convert a dict to StoryMetadata."""
    return StoryMetadata(
        title=data["title"],
        author=data.get("author", ""),
        target_age=data.get("target_age", "5-8"),
        created_at=_iso_to_datetime(data["created_at"]),
        modified_at=_iso_to_datetime(data["modified_at"]),
        style=data.get("style", "storybook_classic"),
    )


def story_to_dict(story: Story) -> dict[str, Any]:
    """
    Convert a Story to a JSON-serializable dict.

    Args:
        story: The story to convert.

    Returns:
        A dictionary suitable for JSON serialization.
    """
    return {
        "version": SCHEMA_VERSION,
        "metadata": _metadata_to_dict(story.metadata),
        "characters": [_character_to_dict(c) for c in story.characters],
        "pages": [_page_to_dict(p) for p in story.pages],
    }


def dict_to_story(
    data: dict[str, Any],
    project_path: Path | None = None,
) -> Story:
    """
    Convert a dict to a Story.

    Args:
        data: The dictionary from JSON.
        project_path: The project directory path (for resolving illustration paths).

    Returns:
        A Story instance.
    """
    pages_dir = project_path / "pages" if project_path else None

    return Story(
        metadata=_dict_to_metadata(data["metadata"]),
        characters=tuple(_dict_to_character(c) for c in data.get("characters", [])),
        pages=tuple(_dict_to_page(p, pages_dir) for p in data.get("pages", [])),
        project_path=project_path,
    )


def create_project_directory(
    story: Story,
    base_dir: Path | None = None,
) -> Path:
    """
    Create the project directory structure for a story.

    Creates:
        <base_dir>/<story-slug>/
        ├── story.json
        ├── pages/
        └── exports/

    Args:
        story: The story to create a directory for.
        base_dir: Base directory for stories. Defaults to ~/Storyteller/stories.

    Returns:
        Path to the created project directory.
    """
    if base_dir is None:
        base_dir = get_stories_directory()

    # Create unique directory name
    slug = slugify(story.metadata.title)
    project_dir = base_dir / slug

    # Handle name collisions
    counter = 1
    original_slug = slug
    while project_dir.exists():
        slug = f"{original_slug}-{counter}"
        project_dir = base_dir / slug
        counter += 1

    # Create directory structure
    project_dir.mkdir(parents=True, exist_ok=True)
    (project_dir / "pages").mkdir(exist_ok=True)
    (project_dir / "exports").mkdir(exist_ok=True)

    logger.info("Created project directory: %s", project_dir)
    return project_dir


def save_story(
    story: Story,
    project_path: Path | None = None,
) -> Story:
    """
    Save a story to disk.

    If the story has no project_path and none is provided, a new project
    directory will be created.

    Args:
        story: The story to save.
        project_path: Optional path to save to. Uses story.project_path if not provided.

    Returns:
        The story with its project_path set.

    Raises:
        ValueError: If no project path is available and story has no title.
    """
    # Determine where to save
    save_path = project_path or story.project_path

    if save_path is None:
        if not story.metadata.title:
            raise ValueError("Cannot save story without title or explicit path")
        save_path = create_project_directory(story)

    # Ensure directory exists
    save_path.mkdir(parents=True, exist_ok=True)
    (save_path / "pages").mkdir(exist_ok=True)
    (save_path / "exports").mkdir(exist_ok=True)

    # Update the story with the save path and current modified time
    story = story.with_project_path(save_path).with_metadata()

    # Serialize and write
    story_file = save_path / "story.json"
    data = story_to_dict(story)

    with open(story_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    logger.info("Saved story to: %s", story_file)
    return story


def load_story(project_path: Path) -> Story:
    """
    Load a story from disk.

    Args:
        project_path: Path to the project directory containing story.json.

    Returns:
        The loaded Story.

    Raises:
        FileNotFoundError: If story.json doesn't exist.
        json.JSONDecodeError: If the JSON is invalid.
    """
    story_file = project_path / "story.json"

    if not story_file.exists():
        raise FileNotFoundError(f"No story.json found in {project_path}")

    with open(story_file, encoding="utf-8") as f:
        data = json.load(f)

    story = dict_to_story(data, project_path)
    logger.info("Loaded story from: %s", story_file)
    return story


def list_stories(base_dir: Path | None = None) -> list[tuple[Path, StoryMetadata]]:
    """
    List all stories in the stories directory.

    Args:
        base_dir: Base directory to search. Defaults to ~/Storyteller/stories.

    Returns:
        List of (project_path, metadata) tuples, sorted by modified_at descending.
    """
    if base_dir is None:
        base_dir = get_stories_directory()

    stories: list[tuple[Path, StoryMetadata]] = []

    if not base_dir.exists():
        return stories

    for project_dir in base_dir.iterdir():
        if not project_dir.is_dir():
            continue

        story_file = project_dir / "story.json"
        if not story_file.exists():
            continue

        try:
            with open(story_file, encoding="utf-8") as f:
                data = json.load(f)
            metadata = _dict_to_metadata(data["metadata"])
            stories.append((project_dir, metadata))
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning("Failed to load story from %s: %s", project_dir, e)
            continue

    # Sort by modified date, newest first
    stories.sort(key=lambda x: x[1].modified_at, reverse=True)
    return stories


def delete_story(project_path: Path) -> None:
    """
    Delete a story project from disk.

    This permanently removes the project directory and all its contents.

    Args:
        project_path: Path to the project directory to delete.

    Raises:
        FileNotFoundError: If the project directory doesn't exist.
    """
    if not project_path.exists():
        raise FileNotFoundError(f"Project not found: {project_path}")

    import shutil

    shutil.rmtree(project_path)
    logger.info("Deleted story project: %s", project_path)


def get_page_illustration_path(story: Story, page_number: int) -> Path:
    """
    Get the expected path for a page's illustration.

    Args:
        story: The story containing the page.
        page_number: The page number.

    Returns:
        Path where the illustration should be saved.

    Raises:
        ValueError: If the story has no project path.
    """
    if story.project_path is None:
        raise ValueError("Story must be saved before generating illustrations")

    return story.project_path / "pages" / f"page_{page_number:02d}.png"


def get_export_path(story: Story, filename: str) -> Path:
    """
    Get the path for an export file.

    Args:
        story: The story being exported.
        filename: The export filename (e.g., "my-story.pdf").

    Returns:
        Path in the exports directory.

    Raises:
        ValueError: If the story has no project path.
    """
    if story.project_path is None:
        raise ValueError("Story must be saved before exporting")

    return story.project_path / "exports" / filename
