"""
Shared pytest fixtures for Storyteller tests.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Generator

import pytest

from storyteller.core import (
    Character,
    Page,
    Story,
    StoryMetadata,
    create_character,
    create_page,
    create_story,
    add_character,
    add_page,
)


@pytest.fixture
def sample_character() -> Character:
    """A sample character for testing."""
    return create_character(
        name="Luna",
        description="A curious little mouse with big ears",
        visual_traits=["small brown mouse", "big curious eyes", "pink nose", "tiny red scarf"],
    )


@pytest.fixture
def sample_character_2() -> Character:
    """A second sample character for testing."""
    return create_character(
        name="Oliver",
        description="A wise old owl who lives in the oak tree",
        visual_traits=["gray owl", "round spectacles", "fluffy feathers", "kind eyes"],
    )


@pytest.fixture
def sample_page() -> Page:
    """A sample page for testing."""
    return create_page(
        page_number=1,
        text="Once upon a time, there was a little mouse named Luna.",
        illustration_prompt="A cozy mouse hole under a large oak tree, with a small brown mouse peeking out.",
    )


@pytest.fixture
def sample_page_2() -> Page:
    """A second sample page for testing."""
    return create_page(
        page_number=2,
        text="Luna loved to explore the forest near her home.",
        illustration_prompt="A small mouse exploring a sunlit forest path, autumn leaves on the ground.",
    )


@pytest.fixture
def sample_metadata() -> StoryMetadata:
    """Sample story metadata for testing."""
    return StoryMetadata(
        title="Luna's Adventure",
        author="Test Author",
        target_age="5-8",
        created_at=datetime(2024, 1, 1, 10, 0, 0),
        modified_at=datetime(2024, 1, 1, 10, 0, 0),
        style="watercolor",
    )


@pytest.fixture
def empty_story() -> Story:
    """An empty story with just metadata."""
    return create_story(
        title="Test Story",
        author="Test Author",
        target_age="5-8",
        style="watercolor",
    )


@pytest.fixture
def sample_story(
    sample_character: Character,
    sample_page: Page,
    sample_page_2: Page,
) -> Story:
    """A sample story with characters and pages."""
    story = create_story(
        title="Luna's Adventure",
        author="Test Author",
        target_age="5-8",
        style="watercolor",
    )
    story = add_character(story, sample_character)
    story = add_page(story, sample_page)
    story = add_page(story, sample_page_2)
    return story


@pytest.fixture
def temp_stories_dir(tmp_path: Path) -> Generator[Path, None, None]:
    """A temporary directory for storing test stories."""
    stories_dir = tmp_path / "stories"
    stories_dir.mkdir()
    yield stories_dir
