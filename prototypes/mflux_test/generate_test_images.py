#!/usr/bin/env python3
"""
MFLUX Image Generation Prototype for Storyteller

This script tests MFLUX image generation quality with various
children's book illustration styles and prompts.

Requirements:
- macOS with Apple Silicon (M1/M2/M3/M4)
- At least 16GB RAM (32GB recommended)
- Python 3.10+

First run will download the model (~12-23GB depending on variant).
"""

import argparse
import os
import sys
import time
from pathlib import Path
from datetime import datetime

# Check platform before importing mflux
if sys.platform != "darwin":
    print("Warning: MFLUX is optimized for macOS with Apple Silicon.")
    print("This prototype may not work correctly on other platforms.")
    print("For testing on non-Mac systems, consider using the Diffusers library instead.")


def get_test_prompts():
    """
    Returns a collection of test prompts organized by style category.
    These are designed to evaluate quality for children's book illustrations.
    """
    return {
        "watercolor": [
            {
                "name": "mouse_garden",
                "prompt": "A small brown mouse with big curious eyes sitting in a colorful garden, "
                         "surrounded by tall sunflowers and daisies, watercolor illustration style, "
                         "soft edges, warm pastel colors, children's picture book art, gentle and friendly",
                "description": "Test watercolor style with animal character"
            },
            {
                "name": "rainy_day",
                "prompt": "A little girl in a yellow raincoat and red boots jumping in puddles, "
                         "watercolor painting style, soft dreamy colors, children's book illustration, "
                         "playful and joyful mood, gentle rain falling",
                "description": "Test watercolor with human character and weather"
            },
        ],
        "cartoon": [
            {
                "name": "friendly_dragon",
                "prompt": "A cute baby dragon with small wings and a big smile, sitting on a hill, "
                         "cartoon illustration style, bright vibrant colors, simple shapes, "
                         "children's picture book, friendly and approachable character design",
                "description": "Test cartoon style with fantasy creature"
            },
            {
                "name": "treehouse",
                "prompt": "A magical treehouse in a big oak tree with rope ladder and colorful flags, "
                         "cartoon illustration style, bright colors, whimsical design, "
                         "children's book art, fun and adventurous setting",
                "description": "Test cartoon style with environment/setting"
            },
        ],
        "storybook_classic": [
            {
                "name": "bear_forest",
                "prompt": "A friendly brown bear wearing a red scarf walking through an autumn forest, "
                         "classic children's book illustration style, warm earthy colors, "
                         "detailed but soft rendering, cozy and inviting atmosphere, "
                         "reminiscent of classic picture books",
                "description": "Test classic storybook style"
            },
            {
                "name": "bedtime",
                "prompt": "A child's cozy bedroom at night with a nightlight glowing softly, "
                         "stuffed animals on the bed, moon visible through the window, "
                         "classic children's book illustration, warm and safe feeling, "
                         "soft lighting, peaceful bedtime scene",
                "description": "Test interior scene with mood lighting"
            },
        ],
        "modern_digital": [
            {
                "name": "space_adventure",
                "prompt": "A young astronaut floating in space near a colorful planet, "
                         "modern digital illustration style, bold colors, clean lines, "
                         "children's book art, sense of wonder and exploration, "
                         "friendly character design, stars in background",
                "description": "Test modern digital style with adventure theme"
            },
            {
                "name": "underwater",
                "prompt": "Colorful fish and a smiling octopus in a coral reef, "
                         "modern digital illustration, vibrant colors, playful characters, "
                         "children's picture book style, underwater scene, "
                         "friendly sea creatures, bubbles floating up",
                "description": "Test underwater scene with multiple characters"
            },
        ],
    }


def generate_image(prompt: str, output_path: Path, model: str = "schnell",
                   steps: int = 4, seed: int = None, width: int = 1024, height: int = 1024):
    """
    Generate a single image using MFLUX.

    Args:
        prompt: The text prompt for image generation
        output_path: Where to save the generated image
        model: MFLUX model variant ("schnell" for fast, "dev" for quality)
        steps: Number of inference steps (schnell: 4, dev: 20-50)
        seed: Random seed for reproducibility (None for random)
        width: Image width in pixels
        height: Image height in pixels

    Returns:
        Tuple of (success: bool, generation_time: float)
    """
    try:
        from mflux import Flux, Config

        # Configure the model
        flux = Flux.from_alias(
            alias=model,  # "schnell" or "dev"
            quantize=8,   # 8-bit quantization for memory efficiency
        )

        # Generate the image
        start_time = time.time()

        image = flux.generate_image(
            seed=seed if seed is not None else int(time.time()) % 100000,
            prompt=prompt,
            config=Config(
                num_inference_steps=steps,
                height=height,
                width=width,
            )
        )

        generation_time = time.time() - start_time

        # Save the image
        image.save(output_path)

        return True, generation_time

    except ImportError as e:
        print(f"Error: mflux not installed. Run: pip install mflux")
        print(f"Details: {e}")
        return False, 0
    except Exception as e:
        print(f"Error generating image: {e}")
        return False, 0


def run_test_suite(output_dir: Path, model: str = "schnell",
                   categories: list = None, seed: int = 42):
    """
    Run the full test suite generating images for all prompts.

    Args:
        output_dir: Directory to save generated images
        model: Model variant to use
        categories: List of categories to test (None for all)
        seed: Base seed for reproducibility
    """
    prompts = get_test_prompts()

    if categories:
        prompts = {k: v for k, v in prompts.items() if k in categories}

    output_dir.mkdir(parents=True, exist_ok=True)

    # Create a results log
    results = []
    total_images = sum(len(p) for p in prompts.values())
    current = 0

    print(f"\n{'='*60}")
    print(f"MFLUX Image Generation Test Suite")
    print(f"{'='*60}")
    print(f"Model: {model}")
    print(f"Output directory: {output_dir}")
    print(f"Total images to generate: {total_images}")
    print(f"{'='*60}\n")

    for category, category_prompts in prompts.items():
        category_dir = output_dir / category
        category_dir.mkdir(exist_ok=True)

        print(f"\n[{category.upper()}]")

        for i, prompt_data in enumerate(category_prompts):
            current += 1
            name = prompt_data["name"]
            prompt = prompt_data["prompt"]
            description = prompt_data["description"]

            output_path = category_dir / f"{name}.png"

            print(f"  [{current}/{total_images}] Generating: {name}")
            print(f"      Description: {description}")

            # Use incrementing seed for variety but reproducibility
            image_seed = seed + current

            success, gen_time = generate_image(
                prompt=prompt,
                output_path=output_path,
                model=model,
                steps=4 if model == "schnell" else 20,
                seed=image_seed,
            )

            if success:
                print(f"      ✓ Generated in {gen_time:.1f}s -> {output_path}")
                results.append({
                    "category": category,
                    "name": name,
                    "time": gen_time,
                    "path": str(output_path),
                    "success": True
                })
            else:
                print(f"      ✗ Failed to generate")
                results.append({
                    "category": category,
                    "name": name,
                    "time": 0,
                    "path": None,
                    "success": False
                })

    # Print summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")

    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]

    print(f"Successful: {len(successful)}/{total_images}")
    if successful:
        avg_time = sum(r["time"] for r in successful) / len(successful)
        print(f"Average generation time: {avg_time:.1f}s")

    if failed:
        print(f"\nFailed generations:")
        for r in failed:
            print(f"  - {r['category']}/{r['name']}")

    print(f"\nImages saved to: {output_dir}")
    print(f"{'='*60}\n")

    return results


def generate_single(prompt: str, output_path: str, model: str = "schnell", seed: int = None):
    """Generate a single image from command line."""
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    print(f"Generating image...")
    print(f"  Prompt: {prompt[:100]}...")
    print(f"  Model: {model}")

    success, gen_time = generate_image(
        prompt=prompt,
        output_path=output,
        model=model,
        steps=4 if model == "schnell" else 20,
        seed=seed,
    )

    if success:
        print(f"  ✓ Generated in {gen_time:.1f}s")
        print(f"  Saved to: {output}")
    else:
        print(f"  ✗ Generation failed")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="MFLUX Image Generation Prototype for Storyteller",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run full test suite with schnell model
  python generate_test_images.py --test-suite

  # Run test suite with dev model (slower but higher quality)
  python generate_test_images.py --test-suite --model dev

  # Test only specific categories
  python generate_test_images.py --test-suite --categories watercolor cartoon

  # Generate a single custom image
  python generate_test_images.py --prompt "A happy bunny in a meadow" --output bunny.png

  # Generate with specific seed for reproducibility
  python generate_test_images.py --prompt "A castle in the clouds" --output castle.png --seed 12345
        """
    )

    parser.add_argument("--test-suite", action="store_true",
                        help="Run the full test suite with various prompts")
    parser.add_argument("--model", choices=["schnell", "dev"], default="schnell",
                        help="Model variant: schnell (fast, 4 steps) or dev (quality, 20 steps)")
    parser.add_argument("--categories", nargs="+",
                        choices=["watercolor", "cartoon", "storybook_classic", "modern_digital"],
                        help="Specific categories to test (test-suite mode)")
    parser.add_argument("--output-dir", type=str, default="./generated_images",
                        help="Output directory for test suite")
    parser.add_argument("--prompt", type=str,
                        help="Custom prompt for single image generation")
    parser.add_argument("--output", type=str,
                        help="Output path for single image generation")
    parser.add_argument("--seed", type=int, default=None,
                        help="Random seed for reproducibility")
    parser.add_argument("--list-prompts", action="store_true",
                        help="List all test prompts without generating")

    args = parser.parse_args()

    if args.list_prompts:
        prompts = get_test_prompts()
        print("\nAvailable test prompts:")
        print("=" * 60)
        for category, category_prompts in prompts.items():
            print(f"\n[{category.upper()}]")
            for p in category_prompts:
                print(f"  • {p['name']}: {p['description']}")
                print(f"    Prompt: {p['prompt'][:80]}...")
        print()
        return

    if args.test_suite:
        output_dir = Path(args.output_dir)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = output_dir / f"test_{args.model}_{timestamp}"

        run_test_suite(
            output_dir=output_dir,
            model=args.model,
            categories=args.categories,
            seed=args.seed or 42
        )
    elif args.prompt:
        if not args.output:
            print("Error: --output is required when using --prompt")
            sys.exit(1)
        generate_single(
            prompt=args.prompt,
            output_path=args.output,
            model=args.model,
            seed=args.seed
        )
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
