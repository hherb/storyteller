# LLM Context Reference

This document provides quick-reference information for AI assistants working on the Storyteller project.

## Quick Facts

| Aspect | Detail |
|--------|--------|
| Python Version | 3.10+ |
| Package Manager | uv |
| GUI Framework | Flet |
| Image Generation | MFLUX (FLUX on MLX) |
| LLM Runtime | Ollama |
| Target Platform | macOS Apple Silicon |
| Min RAM | 32GB |

## Key Import Paths

```python
# Core models
from storyteller.core.story import Story, Page, Character

# Generation
from storyteller.generation.image import generate_illustration
from storyteller.generation.text import LLMClient

# UI
from storyteller.ui.app import main
```

## MFLUX API Reference

```python
from mflux.models.flux.variants.txt2img.flux import Flux1

flux = Flux1.from_name(
    model_name="schnell",  # or "dev"
    quantize=8,            # 3, 4, 5, 6, or 8
)

image = flux.generate_image(
    seed=42,
    prompt="...",
    num_inference_steps=4,  # 2-4 for schnell, 20-25 for dev
    height=1024,
    width=1024,
)

image.save(path="output.png")
```

## Ollama API Reference

```python
import ollama

# Generate text
response = ollama.generate(
    model="phi4",
    prompt="Your prompt here",
)
print(response["response"])

# Chat format
response = ollama.chat(
    model="phi4",
    messages=[
        {"role": "system", "content": "You are a story guide..."},
        {"role": "user", "content": "I want to write about a mouse"},
    ],
)
```

## File Locations

| What | Where |
|------|-------|
| Main package | `src/storyteller/` |
| Tests | `tests/` |
| Prototypes | `prototypes/` |
| User docs | `docs/user/` |
| Dev docs | `docs/developers/` |
| This file | `docs/llm/` |
| Planning | `docs/planning/` |

## Common Patterns

### Dataclass with Factory

```python
@dataclass(frozen=True)
class GenerationConfig:
    model: str = "schnell"
    steps: int = 4

    @classmethod
    def for_model(cls, model: str) -> GenerationConfig:
        steps = 4 if model == "schnell" else 20
        return cls(model=model, steps=steps)
```

### Result Type Pattern

```python
@dataclass(frozen=True)
class GenerationResult:
    success: bool
    output_path: Optional[Path]
    error_message: Optional[str] = None
    generation_time: float = 0.0
```

### Pure Function with Type Hints

```python
def filter_prompts(
    prompts: dict[str, list[TestPrompt]],
    categories: Optional[list[str]],
) -> dict[str, list[TestPrompt]]:
    """
    Filter prompts to only include specified categories.

    Args:
        prompts: Full dictionary of prompts by category.
        categories: List of category names, or None for all.

    Returns:
        Filtered dictionary of prompts.
    """
    if categories is None:
        return prompts
    return {k: v for k, v in prompts.items() if k in categories}
```

## Testing Patterns

```python
# Fixture for common test data
@pytest.fixture
def sample_story() -> Story:
    return Story(
        title="Test Story",
        pages=[Page(text="Once upon a time...", illustration_prompt="...")],
    )

# Test naming: test_<function>_<scenario>_<expected>
def test_generate_prompt_empty_input_returns_default() -> None:
    result = generate_prompt("")
    assert result == DEFAULT_PROMPT
```

## Safety Keywords for Image Prompts

Always include when generating children's book illustrations:
- "children's book illustration"
- "friendly and approachable"
- "warm colors"
- "gentle"
- "safe"
- "non-threatening"

## Models to Use

| Task | Model | Notes |
|------|-------|-------|
| Story guidance | phi4 (14B) | Good balance of quality and speed |
| Quick suggestions | llama3.1:8b | Faster for simple tasks |
| Image preview | FLUX schnell | 4 steps, ~30-60s |
| Final images | FLUX dev | 20-25 steps, ~2-4min |
