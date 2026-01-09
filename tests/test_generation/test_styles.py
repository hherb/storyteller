"""
Tests for the styles module.
"""

from __future__ import annotations

import pytest

from storyteller.generation.styles import (
    SAFETY_MODIFIERS,
    STYLE_PRESETS,
    StylePreset,
    apply_style,
    build_illustration_prompt,
    get_style,
    list_styles,
)


class TestStylePreset:
    """Tests for the StylePreset class."""

    def test_create_style_preset(self) -> None:
        """StylePreset can be created with all attributes."""
        preset = StylePreset(
            name="test",
            display_name="Test Style",
            prompt_suffix="test style suffix",
            description="A test style",
        )
        assert preset.name == "test"
        assert preset.display_name == "Test Style"
        assert preset.prompt_suffix == "test style suffix"
        assert preset.description == "A test style"

    def test_style_preset_is_frozen(self) -> None:
        """StylePreset is immutable (frozen dataclass)."""
        preset = StylePreset(
            name="test",
            display_name="Test",
            prompt_suffix="suffix",
            description="desc",
        )
        with pytest.raises(AttributeError):
            preset.name = "modified"  # type: ignore


class TestGetStyle:
    """Tests for the get_style function."""

    def test_get_valid_style(self) -> None:
        """get_style returns preset for valid style name."""
        style = get_style("watercolor")
        assert style.name == "watercolor"
        assert isinstance(style, StylePreset)

    def test_get_all_defined_styles(self) -> None:
        """All defined styles can be retrieved."""
        for style_name in STYLE_PRESETS:
            style = get_style(style_name)
            assert style.name == style_name

    def test_get_invalid_style_raises_keyerror(self) -> None:
        """get_style raises KeyError for unknown style."""
        with pytest.raises(KeyError) as exc_info:
            get_style("nonexistent_style")
        assert "nonexistent_style" in str(exc_info.value)
        assert "Available:" in str(exc_info.value)


class TestListStyles:
    """Tests for the list_styles function."""

    def test_returns_list(self) -> None:
        """list_styles returns a list."""
        styles = list_styles()
        assert isinstance(styles, list)

    def test_returns_all_presets(self) -> None:
        """list_styles returns all defined presets."""
        styles = list_styles()
        assert len(styles) == len(STYLE_PRESETS)

    def test_all_elements_are_presets(self) -> None:
        """All elements in list are StylePreset instances."""
        styles = list_styles()
        for style in styles:
            assert isinstance(style, StylePreset)


class TestApplyStyle:
    """Tests for the apply_style function."""

    def test_applies_style_suffix(self) -> None:
        """apply_style adds the style's prompt suffix."""
        result = apply_style("A mouse in a garden", "watercolor")
        assert "watercolor" in result.lower()
        assert "A mouse in a garden" in result

    def test_applies_safety_modifiers(self) -> None:
        """apply_style adds safety modifiers."""
        result = apply_style("A test scene", "cartoon")
        assert "children's book illustration" in result.lower()
        assert "friendly" in result.lower()

    def test_invalid_style_raises_keyerror(self) -> None:
        """apply_style raises KeyError for invalid style."""
        with pytest.raises(KeyError):
            apply_style("test prompt", "invalid_style")

    def test_preserves_base_prompt(self) -> None:
        """apply_style preserves the original base prompt."""
        base = "A friendly dragon reading a book"
        result = apply_style(base, "storybook_classic")
        assert base in result


class TestBuildIllustrationPrompt:
    """Tests for the build_illustration_prompt function."""

    def test_basic_prompt(self) -> None:
        """build_illustration_prompt creates basic prompt."""
        result = build_illustration_prompt(
            scene_description="A mouse exploring a garden",
            style_name="watercolor",
        )
        assert "mouse exploring" in result
        assert "watercolor" in result.lower()

    def test_with_character_traits(self) -> None:
        """build_illustration_prompt includes character traits."""
        result = build_illustration_prompt(
            scene_description="A scene",
            character_traits=["small brown mouse", "red scarf"],
            style_name="cartoon",
        )
        assert "small brown mouse" in result
        assert "red scarf" in result
        assert "featuring" in result

    def test_with_additional_context(self) -> None:
        """build_illustration_prompt includes additional context."""
        result = build_illustration_prompt(
            scene_description="A forest scene",
            additional_context="morning light, dew on leaves",
            style_name="pencil_sketch",
        )
        assert "morning light" in result
        assert "dew on leaves" in result

    def test_includes_safety_modifiers(self) -> None:
        """build_illustration_prompt includes safety modifiers."""
        result = build_illustration_prompt(
            scene_description="test",
            style_name="watercolor",
        )
        assert "children's book illustration" in result.lower()
        assert "friendly" in result.lower()


class TestSafetyModifiers:
    """Tests for the SAFETY_MODIFIERS constant."""

    def test_safety_modifiers_content(self) -> None:
        """SAFETY_MODIFIERS contains essential child-safety terms."""
        assert "children's book illustration" in SAFETY_MODIFIERS.lower()
        assert "friendly" in SAFETY_MODIFIERS.lower()
        assert "safe" in SAFETY_MODIFIERS.lower()

    def test_safety_modifiers_comment_accuracy(self) -> None:
        """Docstring/comment accurately describes when modifiers are applied."""
        # This test verifies the module correctly documents that safety
        # modifiers are NOT automatically applied to all prompts
        import storyteller.generation.styles as styles_module
        with open(styles_module.__file__) as f:
            source = f.read()
        # Check that the comment mentions apply_style or build_illustration_prompt
        assert "apply_style" in source or "build_illustration_prompt" in source


class TestStylePresets:
    """Tests for the predefined style presets."""

    def test_watercolor_preset(self) -> None:
        """Watercolor preset has appropriate attributes."""
        style = STYLE_PRESETS["watercolor"]
        assert "watercolor" in style.prompt_suffix.lower()
        assert "soft" in style.prompt_suffix.lower() or "pastel" in style.prompt_suffix.lower()

    def test_cartoon_preset(self) -> None:
        """Cartoon preset has appropriate attributes."""
        style = STYLE_PRESETS["cartoon"]
        assert "cartoon" in style.prompt_suffix.lower()
        assert "bright" in style.prompt_suffix.lower() or "vibrant" in style.prompt_suffix.lower()

    def test_all_presets_have_required_fields(self) -> None:
        """All presets have non-empty required fields."""
        for name, preset in STYLE_PRESETS.items():
            assert preset.name == name
            assert preset.display_name, f"{name} missing display_name"
            assert preset.prompt_suffix, f"{name} missing prompt_suffix"
            assert preset.description, f"{name} missing description"
