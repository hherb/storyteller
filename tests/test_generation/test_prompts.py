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
