"""
Tests for the prompt templates module.
"""

from __future__ import annotations

from storyteller.generation import (
    PromptTemplate,
    get_all_templates,
    format_previous_pages,
    format_character_details,
    calculate_story_structure,
    STORY_GUIDE_SYSTEM,
    PAGE_WRITER_SYSTEM,
    STORY_START,
    WRITE_PAGE_TEXT,
)


class TestPromptTemplate:
    """Tests for the PromptTemplate class."""

    def test_create_template(self) -> None:
        """PromptTemplate can be created with basic attributes."""
        template = PromptTemplate(
            name="test",
            template="Hello $name!",
            description="A test template",
        )
        assert template.name == "test"
        assert template.template == "Hello $name!"
        assert template.description == "A test template"

    def test_render_template(self) -> None:
        """render substitutes variables correctly."""
        template = PromptTemplate(
            name="test",
            template="Hello $name, you are $age years old!",
        )
        result = template.render(name="Alice", age="5")
        assert result == "Hello Alice, you are 5 years old!"

    def test_render_with_missing_variables(self) -> None:
        """render preserves missing variables (safe_substitute)."""
        template = PromptTemplate(
            name="test",
            template="Hello $name, your age is $age!",
        )
        result = template.render(name="Alice")
        assert result == "Hello Alice, your age is $age!"

    def test_render_multiline(self) -> None:
        """render works with multiline templates."""
        template = PromptTemplate(
            name="test",
            template="""First line: $first
Second line: $second""",
        )
        result = template.render(first="A", second="B")
        assert "First line: A" in result
        assert "Second line: B" in result


class TestBuiltInTemplates:
    """Tests for the built-in prompt templates."""

    def test_story_guide_system_renders(self) -> None:
        """STORY_GUIDE_SYSTEM template renders correctly."""
        result = STORY_GUIDE_SYSTEM.render(
            target_age="5-8",
            style="watercolor",
        )
        assert "5-8" in result
        assert "watercolor" in result
        assert "story guide" in result.lower()

    def test_page_writer_system_renders(self) -> None:
        """PAGE_WRITER_SYSTEM template renders correctly."""
        result = PAGE_WRITER_SYSTEM.render(
            target_age="5-8",
            title="Test Story",
            style="cartoon",
        )
        assert "5-8" in result
        assert "Test Story" in result

    def test_story_start_renders(self) -> None:
        """STORY_START template renders (no variables)."""
        result = STORY_START.render()
        assert "main character" in result.lower()
        assert "where" in result.lower()

    def test_write_page_text_renders(self) -> None:
        """WRITE_PAGE_TEXT template renders with all variables."""
        result = WRITE_PAGE_TEXT.render(
            page_number=3,
            total_pages=10,
            title="Luna's Adventure",
            character_name="Luna",
            character_description="a curious mouse",
            setting="the forest",
            previous_text="Page 1: Once upon a time...",
            page_purpose="Luna meets a new friend",
            target_age="5-8",
        )
        assert "page 3" in result.lower() or "3" in result
        assert "Luna" in result
        assert "5-8" in result


class TestGetAllTemplates:
    """Tests for the get_all_templates function."""

    def test_returns_dict(self) -> None:
        """get_all_templates returns a dictionary."""
        templates = get_all_templates()
        assert isinstance(templates, dict)

    def test_contains_required_templates(self) -> None:
        """All required templates are present."""
        templates = get_all_templates()
        required = [
            "story_guide_system",
            "page_writer_system",
            "story_start",
            "write_page_text",
            "generate_illustration_prompt",
        ]
        for name in required:
            assert name in templates, f"Missing template: {name}"

    def test_all_values_are_templates(self) -> None:
        """All values in the dict are PromptTemplate instances."""
        templates = get_all_templates()
        for name, template in templates.items():
            assert isinstance(template, PromptTemplate), f"{name} is not a PromptTemplate"


class TestFormatPreviousPages:
    """Tests for the format_previous_pages function."""

    def test_empty_list(self) -> None:
        """Empty list returns first page indicator."""
        result = format_previous_pages([])
        assert "first page" in result.lower()

    def test_single_page(self) -> None:
        """Single page is formatted correctly."""
        result = format_previous_pages([(1, "Once upon a time...")])
        assert "Page 1" in result
        assert "Once upon a time" in result

    def test_multiple_pages(self) -> None:
        """Multiple pages are formatted in order."""
        pages = [
            (1, "First page text"),
            (2, "Second page text"),
        ]
        result = format_previous_pages(pages)
        assert "Page 1" in result
        assert "Page 2" in result
        assert result.index("Page 1") < result.index("Page 2")


class TestFormatCharacterDetails:
    """Tests for the format_character_details function."""

    def test_basic_formatting(self) -> None:
        """Character details are formatted correctly."""
        result = format_character_details(
            name="Luna",
            description="a curious mouse",
            visual_traits=["brown fur", "big eyes"],
        )
        assert "Luna" in result
        assert "curious mouse" in result
        assert "brown fur" in result
        assert "big eyes" in result

    def test_empty_traits(self) -> None:
        """Empty traits list shows 'not specified'."""
        result = format_character_details(
            name="Luna",
            description="a mouse",
            visual_traits=[],
        )
        assert "not specified" in result


class TestCalculateStoryStructure:
    """Tests for the calculate_story_structure function."""

    def test_short_story_4_pages(self) -> None:
        """4-page story has appropriate structure."""
        structure = calculate_story_structure(4)
        assert structure["beginning_end"] == 1
        assert structure["middle_start"] == 2
        assert structure["middle_end"] == 3
        assert structure["ending_start"] == 4

    def test_medium_story_8_pages(self) -> None:
        """8-page story has appropriate structure."""
        structure = calculate_story_structure(8)
        assert structure["beginning_end"] == 2
        assert structure["middle_start"] == 3
        assert structure["middle_end"] == 6
        assert structure["ending_start"] == 7

    def test_long_story_12_pages(self) -> None:
        """12-page story has appropriate structure."""
        structure = calculate_story_structure(12)
        # Beginning is ~1/4 of pages
        assert structure["beginning_end"] >= 2
        # Ending starts ~3/4 through
        assert structure["ending_start"] <= 12

    def test_structure_covers_all_pages(self) -> None:
        """Structure accounts for all pages without gaps."""
        for page_count in [4, 6, 8, 10, 12]:
            structure = calculate_story_structure(page_count)
            # Beginning leads into middle
            assert structure["middle_start"] == structure["beginning_end"] + 1
            # Middle leads into ending
            assert structure["ending_start"] == structure["middle_end"] + 1
            # Ending includes last page
            assert structure["ending_start"] <= page_count


class TestFindCharactersInPage:
    """Tests for the find_characters_in_page function."""

    def test_finds_character_by_name(self) -> None:
        """Character is found when name appears in text."""
        from storyteller.generation import find_characters_in_page

        characters = [
            ("Luna", "a brave mouse", ("small", "brown")),
        ]
        result = find_characters_in_page("Luna hopped through the garden.", characters)
        assert len(result) == 1
        assert result[0][0] == "Luna"

    def test_case_insensitive_matching(self) -> None:
        """Character matching is case insensitive."""
        from storyteller.generation import find_characters_in_page

        characters = [
            ("Luna", "a brave mouse", ("small",)),
        ]
        result = find_characters_in_page("LUNA was very happy.", characters)
        assert len(result) == 1

    def test_word_boundary_prevents_substring_match(self) -> None:
        """Character name 'Art' should not match 'Arthur' or 'party'."""
        from storyteller.generation import find_characters_in_page

        characters = [
            ("Art", "a painter", ("artistic",)),
        ]
        # Should NOT match Arthur
        result = find_characters_in_page("Arthur went to the castle.", characters)
        assert len(result) == 0

        # Should NOT match party
        result = find_characters_in_page("They had a party.", characters)
        assert len(result) == 0

        # SHOULD match Art as a whole word
        result = find_characters_in_page("Art painted a beautiful picture.", characters)
        assert len(result) == 1
        assert result[0][0] == "Art"

    def test_word_boundary_at_sentence_boundaries(self) -> None:
        """Character is found at start/end of sentences."""
        from storyteller.generation import find_characters_in_page

        characters = [
            ("Max", "a friendly dog", ("golden",)),
        ]
        # At start
        result = find_characters_in_page("Max ran quickly.", characters)
        assert len(result) == 1

        # At end
        result = find_characters_in_page("Everyone cheered for Max.", characters)
        assert len(result) == 1

    def test_multiple_characters_found(self) -> None:
        """Multiple characters are found in the same text."""
        from storyteller.generation import find_characters_in_page

        characters = [
            ("Luna", "a mouse", ("small",)),
            ("Felix", "a cat", ("orange",)),
            ("Mr. Owl", "wise owl", ("feathery",)),
        ]
        result = find_characters_in_page(
            "Luna and Felix visited Mr. Owl in his tree.",
            characters,
        )
        assert len(result) == 3

    def test_special_characters_in_name(self) -> None:
        """Names with special characters are matched correctly."""
        from storyteller.generation import find_characters_in_page

        characters = [
            ("Mr. Fox", "a clever fox", ("red",)),
        ]
        result = find_characters_in_page("Mr. Fox had a plan.", characters)
        assert len(result) == 1
        assert result[0][0] == "Mr. Fox"

    def test_no_characters_found(self) -> None:
        """Empty list returned when no characters match."""
        from storyteller.generation import find_characters_in_page

        characters = [
            ("Luna", "a mouse", ("small",)),
        ]
        result = find_characters_in_page("The garden was peaceful.", characters)
        assert len(result) == 0

    def test_returns_visual_traits_as_list(self) -> None:
        """Visual traits are returned as a list (not tuple)."""
        from storyteller.generation import find_characters_in_page

        characters = [
            ("Luna", "a mouse", ("small", "brown", "curious")),
        ]
        result = find_characters_in_page("Luna explored.", characters)
        assert len(result) == 1
        assert isinstance(result[0][2], list)
        assert result[0][2] == ["small", "brown", "curious"]


class TestBuildIllustrationPromptSimple:
    """Tests for the build_illustration_prompt_simple function."""

    def test_basic_prompt(self) -> None:
        """Basic prompt is created from page text."""
        from storyteller.generation import build_illustration_prompt_simple

        result = build_illustration_prompt_simple(
            page_text="Luna found a magical flower.",
            style="watercolor",
        )
        assert "Luna found a magical flower" in result
        assert "watercolor" in result.lower()

    def test_with_characters(self) -> None:
        """Character traits are included in prompt."""
        from storyteller.generation import build_illustration_prompt_simple

        result = build_illustration_prompt_simple(
            page_text="Test page",
            characters=[("Luna", "a mouse", ["small", "brown"])],
            style="cartoon",
        )
        assert "Luna" in result
        assert "small" in result
        assert "brown" in result

    def test_invalid_style_raises_error(self) -> None:
        """Invalid style name raises KeyError."""
        import pytest
        from storyteller.generation import build_illustration_prompt_simple

        with pytest.raises(KeyError):
            build_illustration_prompt_simple(
                page_text="Test",
                style="invalid_style_name",
            )

    def test_long_text_is_truncated(self) -> None:
        """Text longer than MAX_SCENE_LENGTH is truncated."""
        from storyteller.generation import build_illustration_prompt_simple
        from storyteller.generation.prompts import MAX_SCENE_LENGTH

        long_text = "A" * 500
        result = build_illustration_prompt_simple(
            page_text=long_text,
            style="watercolor",
        )
        # The scene should be truncated
        assert "..." in result
        # The full long text should not appear
        assert long_text not in result

    def test_includes_safety_modifiers(self) -> None:
        """Safety modifiers are included via apply_style."""
        from storyteller.generation import build_illustration_prompt_simple

        result = build_illustration_prompt_simple(
            page_text="A test scene",
            style="watercolor",
        )
        assert "children's book illustration" in result.lower()
        assert "friendly" in result.lower()


class TestMaxSceneLengthConstant:
    """Tests for the MAX_SCENE_LENGTH constant."""

    def test_constant_exists(self) -> None:
        """MAX_SCENE_LENGTH constant is defined."""
        from storyteller.generation.prompts import MAX_SCENE_LENGTH
        assert MAX_SCENE_LENGTH == 200

    def test_constant_is_reasonable(self) -> None:
        """MAX_SCENE_LENGTH is a reasonable value for prompts."""
        from storyteller.generation.prompts import MAX_SCENE_LENGTH
        assert 100 <= MAX_SCENE_LENGTH <= 500
