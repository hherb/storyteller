"""
Tests for the image generation module.
"""

from __future__ import annotations

import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from storyteller.generation.image import (
    GenerationResult,
    ImageConfig,
    ImageGenerator,
    MAX_SEED,
    _singleton_lock,
    get_generator,
)


class TestImageConfig:
    """Tests for the ImageConfig class."""

    def test_default_config(self) -> None:
        """Default config uses schnell model with standard settings."""
        config = ImageConfig()
        assert config.model == "schnell"
        assert config.quantize == 4
        assert config.steps == 4
        assert config.width == 1024
        assert config.height == 1024
        assert config.seed is None

    def test_valid_schnell_config(self) -> None:
        """Valid schnell config passes validation."""
        config = ImageConfig(model="schnell", steps=4, quantize=4)
        assert config.model == "schnell"
        assert config.steps == 4

    def test_valid_dev_config(self) -> None:
        """Valid dev config passes validation."""
        config = ImageConfig(model="dev", steps=20, quantize=8)
        assert config.model == "dev"
        assert config.steps == 20

    def test_invalid_model_raises_error(self) -> None:
        """Invalid model name raises ValueError."""
        with pytest.raises(ValueError, match="Invalid model"):
            ImageConfig(model="invalid")

    def test_invalid_quantize_raises_error(self) -> None:
        """Invalid quantization value raises ValueError."""
        with pytest.raises(ValueError, match="Invalid quantize"):
            ImageConfig(quantize=16)

    def test_schnell_invalid_steps_too_low(self) -> None:
        """Schnell model with steps < 2 raises ValueError."""
        with pytest.raises(ValueError, match="Invalid steps for schnell"):
            ImageConfig(model="schnell", steps=1)

    def test_schnell_invalid_steps_too_high(self) -> None:
        """Schnell model with steps > 8 raises ValueError."""
        with pytest.raises(ValueError, match="Invalid steps for schnell"):
            ImageConfig(model="schnell", steps=10)

    def test_dev_invalid_steps_too_low(self) -> None:
        """Dev model with steps < 15 raises ValueError."""
        with pytest.raises(ValueError, match="Invalid steps for dev"):
            ImageConfig(model="dev", steps=10)

    def test_dev_invalid_steps_too_high(self) -> None:
        """Dev model with steps > 30 raises ValueError."""
        with pytest.raises(ValueError, match="Invalid steps for dev"):
            ImageConfig(model="dev", steps=35)

    def test_for_model_schnell(self) -> None:
        """for_model creates appropriate schnell config."""
        config = ImageConfig.for_model("schnell")
        assert config.model == "schnell"
        assert config.steps == 4
        assert config.quantize == 4

    def test_for_model_dev(self) -> None:
        """for_model creates appropriate dev config."""
        config = ImageConfig.for_model("dev", quantize=8)
        assert config.model == "dev"
        assert config.steps == 20
        assert config.quantize == 8


class TestMaxSeedConstant:
    """Tests for the MAX_SEED constant."""

    def test_max_seed_value(self) -> None:
        """MAX_SEED is the expected 32-bit signed integer max."""
        assert MAX_SEED == 2147483647


class TestSingletonThreadSafety:
    """Tests for thread-safe singleton initialization."""

    def setup_method(self) -> None:
        """Reset the singleton before each test."""
        import storyteller.generation.image as image_module
        image_module._default_generator = None

    def test_get_generator_returns_singleton(self) -> None:
        """get_generator returns the same instance."""
        gen1 = get_generator()
        gen2 = get_generator()
        assert gen1 is gen2

    def test_get_generator_with_config(self) -> None:
        """get_generator creates generator with provided config."""
        config = ImageConfig(model="schnell", steps=6)
        gen = get_generator(config)
        assert gen.config.steps == 6

    def test_get_generator_updates_config(self) -> None:
        """get_generator updates existing generator config."""
        config1 = ImageConfig(model="schnell", steps=4)
        gen1 = get_generator(config1)
        assert gen1.config.steps == 4

        config2 = ImageConfig(model="schnell", steps=6)
        gen2 = get_generator(config2)
        assert gen1 is gen2  # Same instance
        assert gen2.config.steps == 6  # Config updated

    def test_concurrent_get_generator_creates_single_instance(self) -> None:
        """Multiple threads calling get_generator create only one instance."""
        import storyteller.generation.image as image_module
        image_module._default_generator = None

        results = []
        barrier = threading.Barrier(10)

        def get_gen():
            barrier.wait()  # Ensure all threads start together
            gen = get_generator()
            results.append(gen)

        threads = [threading.Thread(target=get_gen) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # All threads should get the same instance
        assert len(results) == 10
        assert all(gen is results[0] for gen in results)


class TestPathTraversalSecurity:
    """Tests for path traversal security validation."""

    def test_forbidden_path_etc(self) -> None:
        """Paths to /etc are rejected."""
        generator = ImageGenerator()
        # Mock the platform and mflux checks to pass, plus the mflux config import
        with patch("storyteller.generation.image.check_platform") as mock_platform, \
             patch("storyteller.generation.image.check_mflux_available") as mock_mflux, \
             patch.dict("sys.modules", {"mflux.config.config": MagicMock()}):
            mock_platform.return_value = (True, "OK")
            mock_mflux.return_value = (True, "OK")

            # Create a mock image object with a save method
            mock_image = MagicMock()
            mock_image.save = MagicMock()

            # Mock the flux model and its generate_image method
            mock_flux = MagicMock()
            mock_flux.generate_image = MagicMock(return_value=mock_image)
            generator._flux_model = mock_flux

            result = generator.generate(
                prompt="test",
                output_path=Path("/etc/passwd.png"),
            )

            assert not result.success
            assert "system directory" in result.error.lower()
            # Ensure the image was NOT saved
            mock_image.save.assert_not_called()

    def test_forbidden_path_var(self) -> None:
        """Paths to /var are rejected."""
        generator = ImageGenerator()
        with patch("storyteller.generation.image.check_platform") as mock_platform, \
             patch("storyteller.generation.image.check_mflux_available") as mock_mflux, \
             patch.dict("sys.modules", {"mflux.config.config": MagicMock()}):
            mock_platform.return_value = (True, "OK")
            mock_mflux.return_value = (True, "OK")

            # Create a mock image object with a save method
            mock_image = MagicMock()
            mock_image.save = MagicMock()

            # Mock the flux model and its generate_image method
            mock_flux = MagicMock()
            mock_flux.generate_image = MagicMock(return_value=mock_image)
            generator._flux_model = mock_flux

            result = generator.generate(
                prompt="test",
                output_path=Path("/var/log/test.png"),
            )

            assert not result.success
            assert "system directory" in result.error.lower()
            # Ensure the image was NOT saved
            mock_image.save.assert_not_called()


class TestGenerationResult:
    """Tests for the GenerationResult class."""

    def test_success_result(self) -> None:
        """Successful result has correct attributes."""
        result = GenerationResult(
            success=True,
            image_path=Path("/tmp/test.png"),
            generation_time=45.5,
            seed_used=12345,
        )
        assert result.success is True
        assert result.image_path == Path("/tmp/test.png")
        assert result.generation_time == 45.5
        assert result.seed_used == 12345
        assert result.error is None

    def test_failure_result(self) -> None:
        """Failed result has correct attributes."""
        result = GenerationResult(
            success=False,
            error="Model loading failed",
            generation_time=5.0,
        )
        assert result.success is False
        assert result.error == "Model loading failed"
        assert result.image_path is None


class TestImageGeneratorCancel:
    """Tests for the cancel functionality."""

    def test_cancel_sets_flag(self) -> None:
        """cancel() sets the cancellation flag."""
        generator = ImageGenerator()
        assert generator._cancel_requested is False
        generator.cancel()
        assert generator._cancel_requested is True

    def test_cancel_docstring_documents_limitation(self) -> None:
        """cancel() docstring documents the cooperative cancellation limitation."""
        docstring = ImageGenerator.cancel.__doc__
        assert docstring is not None
        assert "cooperative" in docstring.lower() or "checkpoint" in docstring.lower()
        assert "30-90" in docstring or "2-4 minutes" in docstring
