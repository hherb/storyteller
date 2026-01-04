# MFLUX Image Generation Prototype

Test FLUX image generation quality for children's book illustrations on Apple Silicon.

## Requirements

- **macOS with Apple Silicon** (M1/M2/M3/M4)
- **16GB RAM minimum** (32GB recommended)
- **Python 3.10+**
- **~25GB free disk space** (for model download on first run)

## Setup

```bash
# Navigate to the prototype directory
cd prototypes/mflux_test

# Install dependencies (creates venv automatically)
uv sync
```

## Usage

### Quick Test - Single Image

```bash
# Generate a single test image (fast)
uv run python generate_test_images.py \
    --prompt "A friendly brown bear reading a book under a tree, children's book illustration, warm colors" \
    --output test_bear.png
```

### Run Full Test Suite

```bash
# Run all test prompts with schnell (fast) model
uv run python generate_test_images.py --test-suite

# Run with dev model (slower but higher quality)
uv run python generate_test_images.py --test-suite --model dev

# Test specific style categories only
uv run python generate_test_images.py --test-suite --categories watercolor cartoon
```

### List Available Test Prompts

```bash
uv run python generate_test_images.py --list-prompts
```

## Test Categories

The test suite includes prompts across 4 illustration styles:

| Category | Description |
|----------|-------------|
| **watercolor** | Soft edges, pastel colors, dreamy feel |
| **cartoon** | Bright colors, simple shapes, bold lines |
| **storybook_classic** | Traditional picture book style, warm tones |
| **modern_digital** | Clean lines, vibrant colors, contemporary |

## Model Variants

| Model | Steps | Speed | Quality | Best For |
|-------|-------|-------|---------|----------|
| **schnell** | 2-4 | ~30-60s | Good | Quick previews, iteration |
| **dev** | 20-25 | ~2-4min | Excellent | Final illustrations |

## Expected Output

Images are saved to `./generated_images/test_{model}_{timestamp}/`

```
generated_images/
└── test_schnell_20260104_123456/
    ├── watercolor/
    │   ├── mouse_garden.png
    │   └── rainy_day.png
    ├── cartoon/
    │   ├── friendly_dragon.png
    │   └── treehouse.png
    ├── storybook_classic/
    │   ├── bear_forest.png
    │   └── bedtime.png
    └── modern_digital/
        ├── space_adventure.png
        └── underwater.png
```

## Python API

The script uses the MFLUX Python API:

```python
from mflux.models.flux.variants.txt2img.flux import Flux1

# Load model with 8-bit quantization
flux = Flux1.from_name(
    model_name="schnell",  # or "dev"
    quantize=8,
)

# Generate image
image = flux.generate_image(
    seed=42,
    prompt="A friendly mouse in a garden",
    num_inference_steps=4,  # 2-4 for schnell, 20-25 for dev
    height=1024,
    width=1024,
)

image.save(path="output.png")
```

## Troubleshooting

### "mflux not installed"

```bash
uv sync
```

### Out of memory

- Close other applications
- The script uses 8-bit quantization by default to reduce memory
- 32GB RAM is recommended for comfortable usage

### Slow generation

- First run downloads the model (~12-23GB)
- Subsequent runs should be 30-90 seconds per image
- Use `schnell` model for faster iteration

### Import errors

Ensure you're using the correct import path:

```python
from mflux.models.flux.variants.txt2img.flux import Flux1
```

## Evaluation Criteria

When reviewing generated images, consider:

1. **Character Appeal** - Are faces/expressions child-friendly?
2. **Color Palette** - Appropriate for children's books?
3. **Consistency Potential** - Could this style be maintained across pages?
4. **Detail Level** - Suitable for picture book format?
5. **Mood** - Does it evoke the right feeling for young readers?

## Next Steps

After evaluation:

1. Note which styles work best
2. Test character consistency (same character, different poses)
3. Try custom prompts matching your story concepts
4. Compare schnell vs dev quality for final decision
