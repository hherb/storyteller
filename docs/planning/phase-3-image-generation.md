# Phase 3: Image Generation Integration Plan

This document outlines the implementation plan for integrating MFLUX image generation into Storyteller.

## Current State

- **Prototype exists**: `prototypes/mflux_test/generate_test_images.py` has working MFLUX code
- **UI is ready**: The GUI has buttons for image generation but only stub implementations
- **Style presets defined**: Settings view already has style selection (watercolor, cartoon, etc.)

## Goals

1. Create production-ready MFLUX wrapper module
2. Generate illustration prompts from story context
3. Implement character consistency tracking
4. Connect image generation to the UI with progress feedback

---

## Implementation Tasks

### 1. Create Core Image Generation Module

**File**: `src/storyteller/generation/image.py`

```python
# Key components needed:

@dataclass(frozen=True)
class ImageConfig:
    """Configuration for image generation."""
    model: str = "schnell"           # "schnell" or "dev"
    quantize: int = 4                # 4-bit or 8-bit
    steps: int = 4                   # 2-8 for schnell, 15-30 for dev
    width: int = 1024
    height: int = 1024
    seed: int | None = None          # None for random

@dataclass(frozen=True)
class GenerationResult:
    """Result of image generation."""
    success: bool
    image_path: Path | None
    generation_time: float
    error: str | None = None

class ImageGenerator:
    """MFLUX-based image generator for Storyteller."""

    def __init__(self, config: ImageConfig | None = None) -> None: ...

    def generate(
        self,
        prompt: str,
        output_path: Path,
        progress_callback: Callable[[float], None] | None = None,
    ) -> GenerationResult: ...

    def generate_async(
        self,
        prompt: str,
        output_path: Path,
        progress_callback: Callable[[float], None] | None = None,
    ) -> GenerationResult: ...
```

**Key Features**:
- Lazy model loading (only load when first generation requested)
- Thread-safe for UI integration
- Progress callback support for progress bars
- Graceful error handling with user-friendly messages
- Platform check (macOS with Apple Silicon required)

### 2. Create Style Preset System

**File**: `src/storyteller/generation/styles.py`

```python
@dataclass(frozen=True)
class StylePreset:
    """An illustration style preset."""
    name: str
    display_name: str
    prompt_suffix: str
    negative_prompt: str | None = None

STYLE_PRESETS: dict[str, StylePreset] = {
    "watercolor": StylePreset(
        name="watercolor",
        display_name="Watercolor",
        prompt_suffix=(
            "watercolor illustration style, soft edges, warm pastel colors, "
            "children's picture book art, gentle and friendly"
        ),
    ),
    "cartoon": StylePreset(
        name="cartoon",
        display_name="Cartoon",
        prompt_suffix=(
            "cartoon illustration style, bright vibrant colors, simple shapes, "
            "children's picture book, friendly and approachable character design"
        ),
    ),
    "storybook_classic": StylePreset(
        name="storybook_classic",
        display_name="Storybook Classic",
        prompt_suffix=(
            "classic children's book illustration style, warm earthy colors, "
            "detailed but soft rendering, cozy and inviting atmosphere"
        ),
    ),
    "modern_digital": StylePreset(
        name="modern_digital",
        display_name="Modern Digital",
        prompt_suffix=(
            "modern digital illustration style, bold colors, clean lines, "
            "children's book art, sense of wonder"
        ),
    ),
    "pencil_sketch": StylePreset(
        name="pencil_sketch",
        display_name="Pencil Sketch",
        prompt_suffix=(
            "pencil sketch illustration, hand-drawn look, soft shading, "
            "children's book art, gentle lines, warm feeling"
        ),
    ),
}

def apply_style(base_prompt: str, style_name: str) -> str:
    """Apply a style preset to a base prompt."""
    ...
```

### 3. Create Illustration Prompt Generator

**File**: `src/storyteller/generation/prompts.py` (extend existing)

```python
def generate_illustration_prompt(
    page_text: str,
    story_context: str,
    characters: list[Character],
    style: str,
    target_age: str,
) -> str:
    """
    Generate an illustration prompt from story content.

    Uses LLM to extract visual elements from the page text
    and combines with character descriptions and style.
    """
    ...
```

**Process**:
1. Extract scene description from page text using LLM
2. Identify which characters appear on this page
3. Inject character visual traits for consistency
4. Apply style preset suffix
5. Add child-safety modifiers

### 4. Implement Character Consistency

**Update**: `src/storyteller/core/story.py`

```python
@dataclass(frozen=True)
class Character:
    """A story character with visual traits for consistency."""
    name: str
    description: str
    visual_traits: list[str]  # e.g., ["small brown mouse", "red scarf", "curious eyes"]

    def to_prompt_fragment(self) -> str:
        """Convert to a prompt fragment for image generation."""
        return ", ".join(self.visual_traits)
```

**Features**:
- Store visual traits extracted from character description
- LLM-assisted trait extraction from free-form description
- Inject traits into every prompt where character appears

### 5. UI Integration

**Update**: `src/storyteller/ui/app.py`

Replace the stub `_handle_generate_image` with real implementation:

```python
def _handle_generate_image(self) -> None:
    """Handle generate illustration request."""
    state = state_manager.state

    if not state.current_story:
        self._show_error("Please create a story first.")
        return

    # Get current page
    page = state.current_story.get_page(state.current_page_number)
    if not page or not page.text:
        self._show_error("Please add text to this page first.")
        return

    # Show progress
    self._progress_overlay.show("Generating illustration...")
    state_manager.set_generation_status(GenerationStatus.GENERATING_IMAGE)

    # Run generation in background thread
    def generate():
        try:
            # Build prompt
            prompt = generate_illustration_prompt(
                page_text=page.text,
                story_context=state.current_story.summary,
                characters=state.current_story.characters,
                style=state.config.illustration_style,
                target_age=state.current_story.metadata.target_age,
            )

            # Generate image
            generator = ImageGenerator(
                ImageConfig(
                    model=state.config.image_model,
                    steps=state.config.image_steps,
                    quantize=4,
                )
            )

            output_path = state.project_path / "pages" / f"page_{page.page_number:02d}.png"

            result = generator.generate(
                prompt=prompt,
                output_path=output_path,
                progress_callback=lambda p: self._progress_overlay.update_progress(p),
            )

            if result.success:
                # Update story with new illustration
                # Update preview
                self._preview_view.set_image(output_path)
            else:
                self._show_error(f"Generation failed: {result.error}")

        finally:
            self._progress_overlay.hide()
            state_manager.set_generation_status(GenerationStatus.IDLE)

    threading.Thread(target=generate, daemon=True).start()
```

### 6. Add Character Dialog

**File**: `src/storyteller/ui/dialogs/character.py`

Implement the character definition dialog as shown in `gui-layout.md`:
- Character name input
- Free-form description text area
- "Extract Visual Traits with AI" button
- Visual traits tag list (editable)
- Save/Cancel buttons

---

## File Changes Summary

| File | Action | Description |
|------|--------|-------------|
| `src/storyteller/generation/image.py` | CREATE | MFLUX wrapper class |
| `src/storyteller/generation/styles.py` | CREATE | Style presets |
| `src/storyteller/generation/prompts.py` | UPDATE | Add illustration prompt generation |
| `src/storyteller/generation/__init__.py` | UPDATE | Export new components |
| `src/storyteller/core/story.py` | UPDATE | Add Character dataclass |
| `src/storyteller/ui/app.py` | UPDATE | Real image generation |
| `src/storyteller/ui/dialogs/character.py` | CREATE | Character dialog |
| `src/storyteller/ui/dialogs/__init__.py` | UPDATE | Export CharacterDialog |
| `src/storyteller/ui/state.py` | UPDATE | Add character state |

---

## Implementation Order

1. **`generation/image.py`** - Core MFLUX wrapper (can test independently)
2. **`generation/styles.py`** - Style presets (simple, no dependencies)
3. **`core/story.py`** - Character dataclass (needed for prompts)
4. **`generation/prompts.py`** - Illustration prompt generation
5. **`ui/dialogs/character.py`** - Character dialog UI
6. **`ui/app.py`** - Integration and wiring
7. **Testing and refinement**

---

## Dependencies

- `mflux` - Already in pyproject.toml
- `Pillow` - Already in pyproject.toml (for image processing)
- macOS with Apple Silicon required for MFLUX

---

## Testing Strategy

### Unit Tests
- `test_image_generator_config` - Config validation
- `test_style_presets` - All styles have valid prompts
- `test_apply_style` - Style application works correctly
- `test_character_to_prompt` - Character trait conversion

### Integration Tests (with mocking)
- `test_generate_image_success` - Mock MFLUX, verify flow
- `test_generate_image_error` - Error handling
- `test_progress_callback` - Progress updates work

### Manual Testing
- Generate images with each style preset
- Verify character consistency across pages
- Test cancellation during generation
- Test on low-memory systems

---

## Estimated Complexity

| Component | Lines of Code | Complexity |
|-----------|---------------|------------|
| image.py | ~150 | Medium (threading, error handling) |
| styles.py | ~80 | Low (data definitions) |
| prompts.py additions | ~100 | Medium (LLM interaction) |
| character.py | ~200 | Medium (dialog layout) |
| app.py changes | ~100 | Medium (async integration) |
| story.py additions | ~50 | Low (dataclass) |
| **Total** | ~680 | Medium |

---

## Success Criteria

1. [ ] User can click "Generate Illustration" and get an image
2. [ ] Progress bar shows during generation
3. [ ] All 5 style presets produce appropriate images
4. [ ] Characters maintain visual consistency across pages
5. [ ] Errors display user-friendly messages
6. [ ] Generation can be cancelled
7. [ ] Images are saved to the project directory
8. [ ] Preview tab shows generated images

---

## Next Phase Preview

After Phase 3, we should complete the remaining UI features (Phase 4 items):
- Export dialog implementation
- Fullscreen preview mode
- Keyboard shortcuts

Then proceed to Phase 5: Export and Polish
- PDF export with ReportLab
- Print-ready output
- Application packaging
