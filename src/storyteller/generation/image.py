"""MFLUX-based image generation for Storyteller.

This module provides a wrapper around MFLUX for generating
children's book illustrations with progress feedback.

Requirements:
    - macOS with Apple Silicon (M1/M2/M3/M4)
    - At least 16GB RAM (32GB recommended)
    - mflux package installed
"""

from __future__ import annotations

import logging
import sys
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ImageConfig:
    """Configuration for image generation.

    Attributes:
        model: Model variant ("schnell" for fast, "dev" for quality).
        quantize: Quantization level (4 or 8 bit).
        steps: Number of inference steps (2-8 for schnell, 15-30 for dev).
        width: Image width in pixels.
        height: Image height in pixels.
        seed: Random seed for reproducibility, or None for random.
    """

    model: str = "schnell"
    quantize: int = 4
    steps: int = 4
    width: int = 1024
    height: int = 1024
    seed: int | None = None

    def __post_init__(self) -> None:
        """Validate configuration values."""
        if self.model not in ("schnell", "dev"):
            raise ValueError(f"Invalid model: {self.model}. Must be 'schnell' or 'dev'.")
        if self.quantize not in (4, 8):
            raise ValueError(f"Invalid quantize: {self.quantize}. Must be 4 or 8.")
        if self.model == "schnell" and not (2 <= self.steps <= 8):
            raise ValueError(f"Invalid steps for schnell: {self.steps}. Must be 2-8.")
        if self.model == "dev" and not (15 <= self.steps <= 30):
            raise ValueError(f"Invalid steps for dev: {self.steps}. Must be 15-30.")

    @classmethod
    def for_model(cls, model: str, quantize: int = 4) -> ImageConfig:
        """Create a config with appropriate defaults for the given model.

        Args:
            model: Model variant ("schnell" or "dev").
            quantize: Quantization level (4 or 8).

        Returns:
            ImageConfig with appropriate settings.
        """
        steps = 4 if model == "schnell" else 20
        return cls(model=model, steps=steps, quantize=quantize)


@dataclass
class GenerationResult:
    """Result of an image generation attempt.

    Attributes:
        success: Whether generation completed successfully.
        image_path: Path to the generated image, or None on failure.
        generation_time: Time taken in seconds.
        error: Error message if generation failed.
        seed_used: The actual seed that was used.
    """

    success: bool
    image_path: Path | None = None
    generation_time: float = 0.0
    error: str | None = None
    seed_used: int | None = None


@dataclass
class GenerationProgress:
    """Progress information during generation.

    Attributes:
        current_step: Current inference step.
        total_steps: Total number of steps.
        progress: Progress as a fraction (0.0 to 1.0).
        status: Human-readable status message.
    """

    current_step: int = 0
    total_steps: int = 1
    progress: float = 0.0
    status: str = "Initializing..."


ProgressCallback = Callable[[GenerationProgress], None]


def check_platform() -> tuple[bool, str]:
    """Check if running on a supported platform.

    Returns:
        Tuple of (is_supported, message).
    """
    if sys.platform != "darwin":
        return False, "MFLUX requires macOS with Apple Silicon."

    # Check for Apple Silicon
    try:
        import platform

        machine = platform.machine()
        if machine not in ("arm64", "arm64e"):
            return False, f"MFLUX requires Apple Silicon, but found {machine}."
    except Exception:
        pass

    return True, "Platform supported."


def check_mflux_available() -> tuple[bool, str]:
    """Check if MFLUX is installed and available.

    Returns:
        Tuple of (is_available, message).
    """
    try:
        from mflux.config.config import Config as MfluxConfig  # noqa: F401
        from mflux.models.flux.variants.txt2img.flux import Flux1  # noqa: F401

        return True, "MFLUX is available."
    except ImportError as e:
        return False, f"MFLUX not installed. Run: pip install mflux. Error: {e}"


class ImageGenerator:
    """MFLUX-based image generator for Storyteller.

    This class provides a clean interface for generating images using MFLUX
    with support for progress callbacks and proper error handling.

    The model is loaded lazily on first generation to avoid slow startup.

    Example:
        >>> generator = ImageGenerator()
        >>> result = generator.generate(
        ...     prompt="A friendly mouse in a garden",
        ...     output_path=Path("image.png"),
        ... )
        >>> if result.success:
        ...     print(f"Image saved to {result.image_path}")
    """

    def __init__(self, config: ImageConfig | None = None) -> None:
        """Initialize the image generator.

        Args:
            config: Generation configuration. Defaults to schnell with 4 steps.
        """
        self._config = config or ImageConfig()
        self._flux_model = None
        self._model_lock = threading.Lock()
        self._cancel_requested = False

    @property
    def config(self) -> ImageConfig:
        """Get the current configuration."""
        return self._config

    def update_config(self, config: ImageConfig) -> None:
        """Update the configuration.

        If the model type or quantization changes, the model will be
        reloaded on the next generation.

        Args:
            config: New configuration.
        """
        old_config = self._config
        self._config = config

        # Invalidate cached model if model type or quantization changed
        if (
            old_config.model != config.model
            or old_config.quantize != config.quantize
        ):
            with self._model_lock:
                self._flux_model = None
                logger.info("Model cache invalidated due to config change")

    def _load_model(self, progress_callback: ProgressCallback | None = None) -> None:
        """Load the MFLUX model.

        Args:
            progress_callback: Optional callback for progress updates.

        Raises:
            RuntimeError: If model loading fails.
        """
        if progress_callback:
            progress_callback(GenerationProgress(
                status="Loading model...",
                progress=0.05,
            ))

        try:
            from mflux.models.flux.variants.txt2img.flux import Flux1

            logger.info(
                f"Loading FLUX.1-{self._config.model} "
                f"({self._config.quantize}-bit quantization)"
            )

            self._flux_model = Flux1.from_name(
                model_name=self._config.model,
                quantize=self._config.quantize,
            )

            logger.info("Model loaded successfully")

        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise RuntimeError(f"Failed to load MFLUX model: {e}") from e

    def generate(
        self,
        prompt: str,
        output_path: Path,
        progress_callback: ProgressCallback | None = None,
    ) -> GenerationResult:
        """Generate an image from a text prompt.

        This method is synchronous and will block until generation completes.
        For UI applications, consider running in a background thread.

        Args:
            prompt: Text prompt describing the desired image.
            output_path: Path where the generated image will be saved.
            progress_callback: Optional callback for progress updates.

        Returns:
            GenerationResult with success status and metadata.
        """
        self._cancel_requested = False
        start_time = time.time()

        # Platform check
        supported, message = check_platform()
        if not supported:
            return GenerationResult(success=False, error=message)

        # MFLUX availability check
        available, message = check_mflux_available()
        if not available:
            return GenerationResult(success=False, error=message)

        try:
            # Load model if needed
            with self._model_lock:
                if self._flux_model is None:
                    self._load_model(progress_callback)

            if self._cancel_requested:
                return GenerationResult(success=False, error="Generation cancelled")

            # Generate the image
            return self._generate_image(prompt, output_path, progress_callback, start_time)

        except Exception as e:
            logger.error(f"Generation failed: {e}")
            return GenerationResult(
                success=False,
                error=str(e),
                generation_time=time.time() - start_time,
            )

    def _generate_image(
        self,
        prompt: str,
        output_path: Path,
        progress_callback: ProgressCallback | None,
        start_time: float,
    ) -> GenerationResult:
        """Internal method to generate the image.

        Args:
            prompt: Text prompt.
            output_path: Output path.
            progress_callback: Progress callback.
            start_time: Start time for timing.

        Returns:
            GenerationResult.
        """
        from mflux.config.config import Config as MfluxConfig

        # Determine seed
        seed = self._config.seed
        if seed is None:
            seed = int(time.time() * 1000) % 2147483647

        if progress_callback:
            progress_callback(GenerationProgress(
                status="Generating image...",
                progress=0.1,
                current_step=0,
                total_steps=self._config.steps,
            ))

        # Create MFLUX config
        mflux_config = MfluxConfig(
            num_inference_steps=self._config.steps,
            height=self._config.height,
            width=self._config.width,
        )

        logger.info(f"Generating image with seed {seed}")
        logger.debug(f"Prompt: {prompt[:100]}...")

        # Generate
        image = self._flux_model.generate_image(
            seed=seed,
            prompt=prompt,
            config=mflux_config,
        )

        if self._cancel_requested:
            return GenerationResult(
                success=False,
                error="Generation cancelled",
                generation_time=time.time() - start_time,
            )

        if progress_callback:
            progress_callback(GenerationProgress(
                status="Saving image...",
                progress=0.95,
                current_step=self._config.steps,
                total_steps=self._config.steps,
            ))

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Save the image
        image.save(path=str(output_path))

        generation_time = time.time() - start_time
        logger.info(f"Image generated in {generation_time:.1f}s: {output_path}")

        if progress_callback:
            progress_callback(GenerationProgress(
                status="Complete",
                progress=1.0,
                current_step=self._config.steps,
                total_steps=self._config.steps,
            ))

        return GenerationResult(
            success=True,
            image_path=output_path,
            generation_time=generation_time,
            seed_used=seed,
        )

    def cancel(self) -> None:
        """Request cancellation of the current generation.

        Note: Cancellation is best-effort and may not take effect
        immediately during model inference.
        """
        self._cancel_requested = True
        logger.info("Cancellation requested")


# Module-level singleton for convenience
_default_generator: ImageGenerator | None = None


def get_generator(config: ImageConfig | None = None) -> ImageGenerator:
    """Get the default image generator instance.

    This provides a singleton generator to avoid loading the model
    multiple times.

    Args:
        config: Optional configuration. If provided and different from
            the current config, the generator will be updated.

    Returns:
        The default ImageGenerator instance.
    """
    global _default_generator

    if _default_generator is None:
        _default_generator = ImageGenerator(config)
    elif config is not None:
        _default_generator.update_config(config)

    return _default_generator


def generate_image(
    prompt: str,
    output_path: Path,
    config: ImageConfig | None = None,
    progress_callback: ProgressCallback | None = None,
) -> GenerationResult:
    """Convenience function to generate an image.

    Uses the default generator singleton.

    Args:
        prompt: Text prompt describing the desired image.
        output_path: Path where the generated image will be saved.
        config: Optional configuration override.
        progress_callback: Optional callback for progress updates.

    Returns:
        GenerationResult with success status and metadata.
    """
    generator = get_generator(config)
    return generator.generate(prompt, output_path, progress_callback)
