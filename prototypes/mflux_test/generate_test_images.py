#!/usr/bin/env python3
"""
MFLUX Image Generation Prototype for Storyteller.

This script tests MFLUX image generation quality with various
children's book illustration styles and prompts.

Requirements:
    - macOS with Apple Silicon (M1/M2/M3/M4)
    - At least 16GB RAM (32GB recommended)
    - Python 3.10+

First run will download the model (~6GB for 4-bit quantized).
Uses pre-quantized community models - no Hugging Face token required.
"""

from __future__ import annotations

import argparse
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Data Structures
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class TestPrompt:
    """A single test prompt for image generation."""

    name: str
    prompt: str
    description: str


@dataclass(frozen=True)
class GenerationResult:
    """Result of a single image generation attempt."""

    category: str
    name: str
    success: bool
    generation_time: float
    output_path: Optional[Path]
    error_message: Optional[str] = None


@dataclass(frozen=True)
class GenerationConfig:
    """Configuration for image generation."""

    model: str = "schnell"
    steps: int = 4
    width: int = 1024
    height: int = 1024
    quantize: int = 4  # 4-bit uses community models, no HF token required

    @classmethod
    def for_model(cls, model: str, quantize: int = 4) -> GenerationConfig:
        """
        Create a config with appropriate defaults for the given model.

        Args:
            model: Model variant ("schnell" or "dev").
            quantize: Quantization level (4 or 8).

        Returns:
            GenerationConfig with appropriate settings.
        """
        steps = 4 if model == "schnell" else 20
        return cls(model=model, steps=steps, quantize=quantize)


# ---------------------------------------------------------------------------
# Test Prompts
# ---------------------------------------------------------------------------


def get_test_prompts() -> dict[str, list[TestPrompt]]:
    """
    Return test prompts organized by illustration style category.

    Returns:
        Dictionary mapping category names to lists of TestPrompt objects.
        Categories: watercolor, cartoon, storybook_classic, modern_digital.
    """
    return {
        "watercolor": [
            TestPrompt(
                name="mouse_garden",
                prompt=(
                    "A small brown mouse with big curious eyes sitting in a "
                    "colorful garden, surrounded by tall sunflowers and daisies, "
                    "watercolor illustration style, soft edges, warm pastel colors, "
                    "children's picture book art, gentle and friendly"
                ),
                description="Test watercolor style with animal character",
            ),
            TestPrompt(
                name="rainy_day",
                prompt=(
                    "A little girl in a yellow raincoat and red boots jumping "
                    "in puddles, watercolor painting style, soft dreamy colors, "
                    "children's book illustration, playful and joyful mood, "
                    "gentle rain falling"
                ),
                description="Test watercolor with human character and weather",
            ),
        ],
        "cartoon": [
            TestPrompt(
                name="friendly_dragon",
                prompt=(
                    "A cute baby dragon with small wings and a big smile, "
                    "sitting on a hill, cartoon illustration style, bright "
                    "vibrant colors, simple shapes, children's picture book, "
                    "friendly and approachable character design"
                ),
                description="Test cartoon style with fantasy creature",
            ),
            TestPrompt(
                name="treehouse",
                prompt=(
                    "A magical treehouse in a big oak tree with rope ladder "
                    "and colorful flags, cartoon illustration style, bright "
                    "colors, whimsical design, children's book art, fun and "
                    "adventurous setting"
                ),
                description="Test cartoon style with environment/setting",
            ),
        ],
        "storybook_classic": [
            TestPrompt(
                name="bear_forest",
                prompt=(
                    "A friendly brown bear wearing a red scarf walking through "
                    "an autumn forest, classic children's book illustration style, "
                    "warm earthy colors, detailed but soft rendering, cozy and "
                    "inviting atmosphere, reminiscent of classic picture books"
                ),
                description="Test classic storybook style",
            ),
            TestPrompt(
                name="bedtime",
                prompt=(
                    "A child's cozy bedroom at night with a nightlight glowing "
                    "softly, stuffed animals on the bed, moon visible through "
                    "the window, classic children's book illustration, warm and "
                    "safe feeling, soft lighting, peaceful bedtime scene"
                ),
                description="Test interior scene with mood lighting",
            ),
        ],
        "modern_digital": [
            TestPrompt(
                name="space_adventure",
                prompt=(
                    "A young astronaut floating in space near a colorful planet, "
                    "modern digital illustration style, bold colors, clean lines, "
                    "children's book art, sense of wonder and exploration, "
                    "friendly character design, stars in background"
                ),
                description="Test modern digital style with adventure theme",
            ),
            TestPrompt(
                name="underwater",
                prompt=(
                    "Colorful fish and a smiling octopus in a coral reef, "
                    "modern digital illustration, vibrant colors, playful "
                    "characters, children's picture book style, underwater "
                    "scene, friendly sea creatures, bubbles floating up"
                ),
                description="Test underwater scene with multiple characters",
            ),
        ],
    }


# ---------------------------------------------------------------------------
# Image Generation
# ---------------------------------------------------------------------------


def check_platform() -> bool:
    """
    Check if running on a supported platform (macOS with Apple Silicon).

    Returns:
        True if platform is supported, False otherwise.
    """
    if sys.platform != "darwin":
        print("Warning: MFLUX is optimized for macOS with Apple Silicon.")
        print("This prototype may not work correctly on other platforms.")
        return False
    return True


def generate_image(
    prompt: str,
    output_path: Path,
    config: GenerationConfig,
    seed: int,
) -> tuple[bool, float, Optional[str]]:
    """
    Generate a single image using MFLUX.

    Args:
        prompt: The text prompt for image generation.
        output_path: Path where the generated image will be saved.
        config: Generation configuration (model, steps, dimensions).
        seed: Random seed for reproducibility.

    Returns:
        Tuple of (success, generation_time_seconds, error_message).
        error_message is None on success.
    """
    try:
        from mflux.config.config import Config as MfluxConfig
        from mflux.models.flux.variants.txt2img.flux import Flux1
    except ImportError as e:
        return False, 0.0, f"mflux not installed. Run: pip install mflux. Details: {e}"

    try:
        # Load the model
        flux = Flux1.from_name(
            model_name=config.model,
            quantize=config.quantize,
        )

        # Create MFLUX config for generation
        mflux_config = MfluxConfig(
            num_inference_steps=config.steps,
            height=config.height,
            width=config.width,
        )

        # Generate the image
        start_time = time.time()

        image = flux.generate_image(
            seed=seed,
            prompt=prompt,
            config=mflux_config,
        )

        generation_time = time.time() - start_time

        # Save the image
        image.save(path=str(output_path))

        return True, generation_time, None

    except Exception as e:
        return False, 0.0, str(e)


def generate_with_result(
    test_prompt: TestPrompt,
    category: str,
    output_path: Path,
    config: GenerationConfig,
    seed: int,
) -> GenerationResult:
    """
    Generate an image and return a structured result.

    Args:
        test_prompt: The test prompt to use.
        category: Category name for the result.
        output_path: Path where the image will be saved.
        config: Generation configuration.
        seed: Random seed for reproducibility.

    Returns:
        GenerationResult with success status and metadata.
    """
    success, gen_time, error = generate_image(
        prompt=test_prompt.prompt,
        output_path=output_path,
        config=config,
        seed=seed,
    )

    return GenerationResult(
        category=category,
        name=test_prompt.name,
        success=success,
        generation_time=gen_time,
        output_path=output_path if success else None,
        error_message=error,
    )


# ---------------------------------------------------------------------------
# Test Suite
# ---------------------------------------------------------------------------


def filter_prompts(
    prompts: dict[str, list[TestPrompt]],
    categories: Optional[list[str]],
) -> dict[str, list[TestPrompt]]:
    """
    Filter prompts to only include specified categories.

    Args:
        prompts: Full dictionary of prompts by category.
        categories: List of category names to include, or None for all.

    Returns:
        Filtered dictionary of prompts.
    """
    if categories is None:
        return prompts
    return {k: v for k, v in prompts.items() if k in categories}


def count_total_prompts(prompts: dict[str, list[TestPrompt]]) -> int:
    """Count total number of prompts across all categories."""
    return sum(len(p) for p in prompts.values())


def print_suite_header(model: str, output_dir: Path, total_images: int) -> None:
    """Print the test suite header."""
    separator = "=" * 60
    print(f"\n{separator}")
    print("MFLUX Image Generation Test Suite")
    print(separator)
    print(f"Model: {model}")
    print(f"Output directory: {output_dir}")
    print(f"Total images to generate: {total_images}")
    print(f"{separator}\n")


def print_suite_summary(results: list[GenerationResult], total: int) -> None:
    """Print the test suite summary."""
    separator = "=" * 60
    successful = [r for r in results if r.success]
    failed = [r for r in results if not r.success]

    print(f"\n{separator}")
    print("SUMMARY")
    print(separator)
    print(f"Successful: {len(successful)}/{total}")

    if successful:
        avg_time = sum(r.generation_time for r in successful) / len(successful)
        print(f"Average generation time: {avg_time:.1f}s")

    if failed:
        print("\nFailed generations:")
        for r in failed:
            print(f"  - {r.category}/{r.name}: {r.error_message}")

    print(separator + "\n")


def run_test_suite(
    output_dir: Path,
    model: str = "schnell",
    categories: Optional[list[str]] = None,
    seed: int = 42,
    quantize: int = 4,
) -> list[GenerationResult]:
    """
    Run the full test suite generating images for all prompts.

    Args:
        output_dir: Directory to save generated images.
        model: Model variant ("schnell" or "dev").
        categories: List of categories to test, or None for all.
        seed: Base seed for reproducibility.
        quantize: Quantization level (4 or 8).

    Returns:
        List of GenerationResult objects for each image.
    """
    prompts = filter_prompts(get_test_prompts(), categories)
    total_images = count_total_prompts(prompts)

    output_dir.mkdir(parents=True, exist_ok=True)
    config = GenerationConfig.for_model(model, quantize=quantize)

    print_suite_header(model, output_dir, total_images)

    results: list[GenerationResult] = []
    current = 0

    for category, category_prompts in prompts.items():
        category_dir = output_dir / category
        category_dir.mkdir(exist_ok=True)

        print(f"\n[{category.upper()}]")

        for test_prompt in category_prompts:
            current += 1
            output_path = category_dir / f"{test_prompt.name}.png"
            image_seed = seed + current

            print(f"  [{current}/{total_images}] Generating: {test_prompt.name}")
            print(f"      Description: {test_prompt.description}")

            result = generate_with_result(
                test_prompt=test_prompt,
                category=category,
                output_path=output_path,
                config=config,
                seed=image_seed,
            )

            results.append(result)

            if result.success:
                print(f"      ✓ Generated in {result.generation_time:.1f}s -> {output_path}")
            else:
                print(f"      ✗ Failed: {result.error_message}")

    print_suite_summary(results, total_images)
    print(f"Images saved to: {output_dir}")

    return results


# ---------------------------------------------------------------------------
# Single Image Generation
# ---------------------------------------------------------------------------


def generate_single(
    prompt: str,
    output_path: str,
    model: str = "schnell",
    seed: Optional[int] = None,
    quantize: int = 4,
) -> None:
    """
    Generate a single image from a custom prompt.

    Args:
        prompt: Text prompt for image generation.
        output_path: Path to save the generated image.
        model: Model variant ("schnell" or "dev").
        seed: Random seed, or None for time-based seed.
        quantize: Quantization level (4 or 8).
    """
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    config = GenerationConfig.for_model(model, quantize=quantize)
    actual_seed = seed if seed is not None else int(time.time()) % 100000

    print("Generating image...")
    print(f"  Prompt: {prompt[:100]}{'...' if len(prompt) > 100 else ''}")
    print(f"  Model: {model} ({quantize}-bit)")
    print(f"  Seed: {actual_seed}")

    success, gen_time, error = generate_image(
        prompt=prompt,
        output_path=output,
        config=config,
        seed=actual_seed,
    )

    if success:
        print(f"  ✓ Generated in {gen_time:.1f}s")
        print(f"  Saved to: {output}")
    else:
        print(f"  ✗ Generation failed: {error}")
        sys.exit(1)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def list_prompts() -> None:
    """Print all available test prompts."""
    prompts = get_test_prompts()
    separator = "=" * 60

    print("\nAvailable test prompts:")
    print(separator)

    for category, category_prompts in prompts.items():
        print(f"\n[{category.upper()}]")
        for p in category_prompts:
            print(f"  • {p.name}: {p.description}")
            truncated = p.prompt[:80] + "..." if len(p.prompt) > 80 else p.prompt
            print(f"    Prompt: {truncated}")

    print()


def create_argument_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
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
  python generate_test_images.py --prompt "A castle in clouds" --output castle.png --seed 12345
        """,
    )

    parser.add_argument(
        "--test-suite",
        action="store_true",
        help="Run the full test suite with various prompts",
    )
    parser.add_argument(
        "--model",
        choices=["schnell", "dev"],
        default="schnell",
        help="Model variant: schnell (fast, 4 steps) or dev (quality, 20 steps)",
    )
    parser.add_argument(
        "--categories",
        nargs="+",
        choices=["watercolor", "cartoon", "storybook_classic", "modern_digital"],
        help="Specific categories to test (test-suite mode only)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="./generated_images",
        help="Output directory for test suite (default: ./generated_images)",
    )
    parser.add_argument(
        "--prompt",
        type=str,
        help="Custom prompt for single image generation",
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output path for single image generation",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducibility",
    )
    parser.add_argument(
        "--quantize",
        type=int,
        choices=[4, 8],
        default=4,
        help="Quantization level: 4 (smaller, no HF token) or 8 (better quality, requires HF token)",
    )
    parser.add_argument(
        "--list-prompts",
        action="store_true",
        help="List all test prompts without generating",
    )

    return parser


def main() -> None:
    """Main entry point for the CLI."""
    check_platform()

    parser = create_argument_parser()
    args = parser.parse_args()

    if args.list_prompts:
        list_prompts()
        return

    if args.test_suite:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path(args.output_dir) / f"test_{args.model}_{timestamp}"

        run_test_suite(
            output_dir=output_dir,
            model=args.model,
            categories=args.categories,
            seed=args.seed or 42,
            quantize=args.quantize,
        )
    elif args.prompt:
        if not args.output:
            print("Error: --output is required when using --prompt")
            sys.exit(1)

        generate_single(
            prompt=args.prompt,
            output_path=args.output,
            model=args.model,
            seed=args.seed,
            quantize=args.quantize,
        )
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
