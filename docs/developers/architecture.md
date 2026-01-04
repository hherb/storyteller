# Architecture Overview

## Package Structure

```
src/storyteller/
├── __init__.py              # Package version and public exports
├── core/                    # Core business logic (no UI dependencies)
│   ├── __init__.py
│   ├── story.py            # Story and Page dataclasses
│   ├── engine.py           # Story creation engine
│   ├── export.py           # PDF export functionality
│   └── persistence.py      # Save/load story projects
├── ui/                      # Flet-based user interface
│   ├── __init__.py
│   ├── app.py              # Main application entry point
│   ├── views/              # Application views/screens
│   │   ├── home.py         # Home/project selection
│   │   ├── editor.py       # Story editor
│   │   └── gallery.py      # Illustration gallery
│   └── components/         # Reusable UI components
│       ├── page_preview.py # Page thumbnail preview
│       └── text_editor.py  # Rich text editor
└── generation/              # AI generation modules
    ├── __init__.py
    ├── text.py             # LLM interface (Ollama)
    ├── image.py            # Image generation (MFLUX)
    └── prompts.py          # Prompt templates and builders
```

## Design Principles

### 1. Core Independence

The `core` package has no dependencies on `ui` or `generation`. This allows:
- Testing business logic without UI
- Swapping UI frameworks if needed
- Clear separation of concerns

### 2. Immutable Data Structures

All data models use frozen dataclasses:

```python
@dataclass(frozen=True)
class Page:
    text: str
    illustration_prompt: str
    illustration_path: Optional[Path] = None
```

This prevents accidental mutation and makes the code easier to reason about.

### 3. Pure Functions

Prefer pure functions over stateful classes:

```python
# Good: Pure function
def generate_illustration_prompt(
    character: str,
    setting: str,
    action: str,
) -> str:
    ...

# Avoid: Stateful class with side effects
class PromptGenerator:
    def __init__(self):
        self.last_prompt = None  # State!

    def generate(self, ...):
        self.last_prompt = result  # Side effect!
        return result
```

### 4. Dependency Injection

Pass dependencies explicitly rather than importing globals:

```python
# Good: Explicit dependency
def create_story(
    llm_client: LLMClient,
    prompt: str,
) -> Story:
    ...

# Avoid: Hidden dependency
def create_story(prompt: str) -> Story:
    from .globals import llm_client  # Hidden!
    ...
```

## Data Flow

```
User Input
    │
    ▼
┌─────────────────┐
│   UI Layer      │  Flet components handle user interaction
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Story Engine   │  Orchestrates story creation workflow
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌───────┐ ┌───────┐
│  LLM  │ │ Image │  AI generation modules
└───┬───┘ └───┬───┘
    │         │
    ▼         ▼
┌─────────────────┐
│   Core Models   │  Story, Page, Character dataclasses
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Persistence    │  Save/load to filesystem
└─────────────────┘
```

## Module Responsibilities

### core/story.py
- `Story` dataclass: metadata, list of pages
- `Page` dataclass: text, illustration info
- `Character` dataclass: name, description, visual traits

### core/engine.py
- `StoryEngine`: orchestrates the story creation flow
- Manages conversation state with LLM
- Coordinates text and image generation

### generation/text.py
- `LLMClient`: wrapper around Ollama API
- `generate_story_guidance()`: get next question/suggestion
- `refine_text()`: improve page text

### generation/image.py
- `ImageGenerator`: wrapper around MFLUX
- `generate_illustration()`: create image from prompt
- Handles model loading, caching, error recovery

### ui/app.py
- Application initialization
- View routing
- Global state management
