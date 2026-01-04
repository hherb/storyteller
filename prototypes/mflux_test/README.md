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

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Quick Test - Single Image

```bash
# Generate a single test image (fast)
python generate_test_images.py \
    --prompt "A friendly brown bear reading a book under a tree, children's book illustration, warm colors" \
    --output test_bear.png
```

### Run Full Test Suite

```bash
# Run all test prompts with schnell (fast) model
python generate_test_images.py --test-suite

# Run with dev model (slower but higher quality)
python generate_test_images.py --test-suite --model dev

# Test specific style categories only
python generate_test_images.py --test-suite --categories watercolor cartoon
```

### List Available Test Prompts

```bash
python generate_test_images.py --list-prompts
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
| **schnell** | 4 | ~30-60s | Good | Quick previews, iteration |
| **dev** | 20 | ~2-4min | Excellent | Final illustrations |

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

## Troubleshooting

### "mflux not installed"
```bash
pip install mflux
```

### Out of memory
- Close other applications
- Try reducing image size (modify script)
- Use 8-bit quantization (already enabled by default)

### Slow generation
- First run downloads the model (~12-23GB)
- Subsequent runs should be 30-90 seconds per image
- Use `schnell` model for faster iteration

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
