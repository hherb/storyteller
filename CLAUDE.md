# Storyteller Development Guidelines

This document provides context and guidelines for AI assistants (Claude) and human contributors working on the Storyteller project.

## Project Overview

Storyteller is a local-only Python application for creating illustrated children's storybooks. It runs on macOS with Apple Silicon and uses AI for both story guidance and illustration generation.

### Target Users
- Parents creating stories for their children
- Older children (10+) creating stories for younger siblings
- Educators creating custom learning materials

### Target Audience (Story Readers)
- Pre-readers (ages 2-5)
- Early readers (ages 5-8)
- Primary school children (ages 6-10)

## Architecture

### Core Components

```
src/storyteller/
├── core/           # Business logic, no UI dependencies
│   ├── story.py    # Story and page data models
│   ├── engine.py   # Story creation engine (LLM interaction)
│   └── export.py   # PDF/print export functionality
├── ui/             # Flet GUI components
│   ├── app.py      # Main application window
│   ├── editor.py   # Story editor view
│   └── gallery.py  # Illustration gallery/selection
└── generation/     # AI generation modules
    ├── text.py     # LLM interface (Ollama)
    └── image.py    # Image generation (MFLUX)
```

### Key Design Decisions

1. **Offline-First**: All AI models run locally. No network calls after installation.
2. **Separation of Concerns**: Core logic is independent of UI framework.
3. **Immutable Data**: Use frozen dataclasses for story data structures.
4. **Pure Functions**: Prefer pure functions over stateful classes where practical.

## Code Style

### Python Standards

- **Python Version**: 3.10+ (for modern type hint syntax)
- **Type Hints**: Required on all function signatures
- **Docstrings**: Required for all public functions and classes (Google style)
- **Line Length**: 100 characters maximum
- **Imports**: Use `from __future__ import annotations` for forward references

### Example Function

```python
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class PageContent:
    """Content for a single storybook page."""

    text: str
    illustration_prompt: str
    illustration_path: Optional[Path] = None


def generate_page_prompt(
    story_context: str,
    page_number: int,
    total_pages: int,
) -> str:
    """
    Generate an illustration prompt for a story page.

    Args:
        story_context: Summary of the story so far.
        page_number: Current page number (1-indexed).
        total_pages: Total number of pages in the book.

    Returns:
        A detailed prompt suitable for image generation.
    """
    # Implementation
    ...
```

### Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Functions | `snake_case` | `generate_image()` |
| Classes | `PascalCase` | `StoryEngine` |
| Constants | `UPPER_SNAKE_CASE` | `MAX_PAGES` |
| Private | Leading underscore | `_internal_helper()` |
| Files | `snake_case.py` | `story_engine.py` |

## Dependencies

### Production Dependencies

| Package | Purpose | Notes |
|---------|---------|-------|
| `flet` | GUI framework | Cross-platform Flutter-based UI |
| `mflux` | Image generation | Apple Silicon only |
| `ollama` | LLM inference | Local model management |
| `Pillow` | Image processing | Resize, format conversion |
| `reportlab` | PDF generation | Print-ready export |

### Development Dependencies

| Package | Purpose |
|---------|---------|
| `pytest` | Testing |
| `ruff` | Linting and formatting |
| `mypy` | Type checking |

## Testing

### Test Structure

```
tests/
├── conftest.py           # Shared fixtures
├── test_core/
│   ├── test_story.py     # Story model tests
│   └── test_engine.py    # Engine logic tests
├── test_generation/
│   └── test_image.py     # Image generation tests
└── test_ui/
    └── test_editor.py    # UI component tests
```

### Testing Guidelines

1. **Unit Tests**: Test pure functions in isolation
2. **Mock AI Calls**: Never call actual LLM/image generation in tests
3. **Fixtures**: Use pytest fixtures for common test data
4. **Naming**: `test_<function>_<scenario>_<expected_result>`

### Example Test

```python
def test_generate_page_prompt_includes_page_number() -> None:
    """Page prompts should indicate position in the story."""
    result = generate_page_prompt(
        story_context="A mouse goes on an adventure",
        page_number=3,
        total_pages=10,
    )

    assert "page 3" in result.lower() or "third" in result.lower()
```

## Content Safety

### Critical Requirements

Since this app creates content for young children:

1. **No Violent Content**: Illustrations must be gentle and non-threatening
2. **Age-Appropriate Language**: Vocabulary suitable for target age group
3. **Positive Themes**: Focus on friendship, curiosity, kindness, growth
4. **No Scary Elements**: Avoid frightening imagery even in "adventure" stories
5. **Inclusive Representation**: Diverse characters and family structures

### Prompt Engineering

Always include safety modifiers in image generation prompts:
- "children's book illustration"
- "friendly and approachable"
- "warm colors"
- "gentle and safe feeling"

## Performance Considerations

### Memory Management

- Target hardware: 32GB RAM Mac
- Image generation uses ~16-24GB during inference
- Keep only current page's image in memory
- Use thumbnails for gallery views

### Generation Times

- Image generation: 30-90 seconds (schnell), 2-4 minutes (dev)
- LLM responses: 1-3 seconds
- Show progress indicators for any operation >1 second

## File Formats

### Story Projects

Stories are saved as directories:

```
my_story/
├── story.json        # Metadata and text content
├── pages/
│   ├── page_01.png   # Generated illustrations
│   ├── page_02.png
│   └── ...
└── exports/
    └── my_story.pdf  # Exported print version
```

### Image Specifications

- Format: PNG (lossless for editing)
- Resolution: 1024x1024 (generation), scaled for print
- Color space: sRGB

## Error Handling

### User-Facing Errors

- Always provide clear, non-technical error messages
- Suggest actionable solutions
- Never show stack traces to users

### Logging

```python
import logging

logger = logging.getLogger(__name__)

# Use appropriate levels
logger.debug("Detailed generation parameters: %s", params)
logger.info("Starting image generation for page %d", page_num)
logger.warning("Generation took longer than expected: %.1fs", duration)
logger.error("Failed to save image: %s", error)
```

## Git Workflow

### Branch Naming

- Features: `feature/description`
- Fixes: `fix/description`
- Prototypes: `prototype/description`

### Commit Messages

Follow conventional commits:

```
feat: add character consistency tracking
fix: resolve memory leak in image gallery
docs: update installation instructions
refactor: extract prompt builder to separate module
test: add tests for story export
```

## Key Files Reference

| File | Purpose |
|------|---------|
| `src/storyteller/__init__.py` | Package version and exports |
| `src/storyteller/core/story.py` | Story and page data models |
| `src/storyteller/generation/image.py` | MFLUX image generation wrapper |
| `prototypes/mflux_test/` | Image quality evaluation scripts |
| `pyproject.toml` | Project configuration and dependencies |

## Resources

- [MFLUX Documentation](https://github.com/filipstrand/mflux)
- [Flet Documentation](https://flet.dev/docs/)
- [Ollama API Reference](https://github.com/ollama/ollama/blob/main/docs/api.md)
- [MLX Documentation](https://ml-explore.github.io/mlx/)
