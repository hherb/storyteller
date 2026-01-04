"""
Tests for the story engine module.
"""

from __future__ import annotations

import pytest

from storyteller.core import (
    ConversationState,
    Story,
    StoryEngine,
    create_story,
)
from storyteller.generation import MockTextGenerator


@pytest.fixture
def mock_generator() -> MockTextGenerator:
    """Create a mock text generator for testing."""
    return MockTextGenerator(model="test-model")


@pytest.fixture
def engine(mock_generator: MockTextGenerator) -> StoryEngine:
    """Create a story engine with mock generator."""
    return StoryEngine(text_generator=mock_generator)


class TestConversationState:
    """Tests for the ConversationState class."""

    def test_initial_state(self) -> None:
        """Initial state has empty messages and initial phase."""
        state = ConversationState()
        assert state.messages == []
        assert state.current_phase == "initial"
        assert state.story is None

    def test_add_message(self) -> None:
        """add_message adds messages to history."""
        state = ConversationState()
        state.add_message("user", "Hello")
        state.add_message("assistant", "Hi there!")

        assert len(state.messages) == 2
        assert state.messages[0].role == "user"
        assert state.messages[0].content == "Hello"
        assert state.messages[1].role == "assistant"

    def test_get_messages_returns_copy(self) -> None:
        """get_messages returns a copy of the messages list."""
        state = ConversationState()
        state.add_message("user", "Hello")

        messages = state.get_messages()
        messages.append(state.messages[0])  # Modify the copy

        assert len(state.messages) == 1  # Original unchanged

    def test_clear(self) -> None:
        """clear resets all state."""
        state = ConversationState()
        state.add_message("user", "Hello")
        state.current_phase = "editing"
        state.story = create_story(title="Test")

        state.clear()

        assert state.messages == []
        assert state.current_phase == "initial"
        assert state.story is None


class TestStoryEngine:
    """Tests for the StoryEngine class."""

    def test_model_name(self, engine: StoryEngine) -> None:
        """model_name returns the generator's model name."""
        assert engine.model_name == "test-model"

    def test_start_new_story(self, engine: StoryEngine) -> None:
        """start_new_story creates a story and returns opening prompt."""
        result = engine.start_new_story(title="Test Story", author="Test Author")

        assert isinstance(result, str)
        assert len(result) > 0
        assert engine.current_story is not None
        assert engine.current_story.title == "Test Story"

    def test_start_new_story_clears_previous(self, engine: StoryEngine) -> None:
        """start_new_story clears any previous conversation."""
        engine.start_new_story(title="Story 1")
        engine.conversation_state.add_message("user", "test message")

        engine.start_new_story(title="Story 2")

        # Should have system and assistant messages, but not the old user message
        messages = engine.conversation_state.get_messages()
        user_messages = [m for m in messages if m.role == "user"]
        assert len(user_messages) == 0

    def test_start_new_story_with_defaults(self, engine: StoryEngine) -> None:
        """start_new_story uses default values when not specified."""
        engine.start_new_story()

        story = engine.current_story
        assert story is not None
        assert story.metadata.target_age == "5-8"  # Default
        assert story.metadata.style == "storybook_classic"  # Default

    def test_process_user_input(self, engine: StoryEngine) -> None:
        """process_user_input generates a response."""
        engine.start_new_story()
        response = engine.process_user_input("I want a story about a mouse")

        assert isinstance(response, str)
        assert len(response) > 0
        # Check that user message was added
        messages = engine.conversation_state.get_messages()
        user_messages = [m for m in messages if m.role == "user"]
        assert len(user_messages) == 1

    def test_process_user_input_without_story(self, engine: StoryEngine) -> None:
        """process_user_input starts a new story if none exists."""
        response = engine.process_user_input("Hello")

        assert engine.current_story is not None
        assert isinstance(response, str)

    def test_generate_page_text(self, engine: StoryEngine) -> None:
        """generate_page_text creates page text."""
        # Setup with predefined response
        mock = MockTextGenerator(responses=["Luna found a shiny acorn."])
        engine = StoryEngine(text_generator=mock)
        engine.start_new_story(title="Luna's Adventure")

        text = engine.generate_page_text(
            page_number=1,
            page_purpose="Introduce Luna in her home",
            total_pages=5,
        )

        assert text == "Luna found a shiny acorn."

    def test_generate_page_text_strips_quotes(self, engine: StoryEngine) -> None:
        """generate_page_text removes surrounding quotes."""
        mock = MockTextGenerator(responses=['"Luna found a shiny acorn."'])
        engine = StoryEngine(text_generator=mock)
        engine.start_new_story()

        text = engine.generate_page_text(
            page_number=1,
            page_purpose="Test",
        )

        assert text == "Luna found a shiny acorn."

    def test_generate_page_text_requires_story(self, engine: StoryEngine) -> None:
        """generate_page_text raises without active story."""
        with pytest.raises(ValueError, match="No active story"):
            engine.generate_page_text(page_number=1, page_purpose="Test")

    def test_generate_illustration_prompt(self, engine: StoryEngine) -> None:
        """generate_illustration_prompt creates a prompt."""
        mock = MockTextGenerator(responses=["A cozy mouse hole under an oak tree"])
        engine = StoryEngine(text_generator=mock)
        engine.start_new_story()

        prompt = engine.generate_illustration_prompt(
            page_text="Luna lived in a cozy hole.",
            mood="warm and cozy",
        )

        assert "cozy mouse hole" in prompt

    def test_add_character_to_story(self, engine: StoryEngine) -> None:
        """add_character_to_story adds a character."""
        engine.start_new_story()
        story = engine.add_character_to_story(
            name="Luna",
            description="A curious mouse",
            visual_traits=["brown fur", "big eyes"],
        )

        assert len(story.characters) == 1
        assert story.characters[0].name == "Luna"
        assert "brown fur" in story.characters[0].visual_traits

    def test_extract_visual_traits(self, engine: StoryEngine) -> None:
        """extract_visual_traits parses LLM response into list."""
        mock = MockTextGenerator(responses=["brown fur, big eyes, pink nose"])
        engine = StoryEngine(text_generator=mock)

        traits = engine.extract_visual_traits(
            name="Luna",
            description="A curious little mouse",
        )

        assert traits == ["brown fur", "big eyes", "pink nose"]

    def test_add_page_to_story(self, engine: StoryEngine) -> None:
        """add_page_to_story adds a page."""
        engine.start_new_story()
        story = engine.add_page_to_story(
            page_number=1,
            text="Once upon a time...",
            illustration_prompt="A sunny day",
        )

        assert story.page_count == 1
        page = story.get_page(1)
        assert page is not None
        assert page.text == "Once upon a time..."

    def test_update_story_page(self, engine: StoryEngine) -> None:
        """update_story_page modifies an existing page."""
        engine.start_new_story()
        engine.add_page_to_story(page_number=1, text="Original text")

        story = engine.update_story_page(page_number=1, text="Updated text")

        page = story.get_page(1)
        assert page is not None
        assert page.text == "Updated text"

    def test_update_story_metadata(self, engine: StoryEngine) -> None:
        """update_story_metadata updates metadata fields."""
        engine.start_new_story(title="Old Title")
        story = engine.update_story_metadata(title="New Title")

        assert story.title == "New Title"

    def test_set_story(self, engine: StoryEngine) -> None:
        """set_story loads an existing story."""
        existing_story = create_story(title="Existing Story")

        engine.set_story(existing_story)

        assert engine.current_story is existing_story
        assert engine.conversation_state.current_phase == "editing"

    def test_get_story(self, engine: StoryEngine) -> None:
        """get_story returns the current story."""
        assert engine.get_story() is None

        engine.start_new_story(title="Test")
        story = engine.get_story()

        assert story is not None
        assert story.title == "Test"


class TestEngineWithMockResponses:
    """Integration-style tests using mock responses."""

    def test_full_story_creation_flow(self) -> None:
        """Test a complete story creation workflow."""
        responses = [
            "That sounds wonderful! A curious mouse named Luna in a forest. "
            "What kind of adventure should Luna have?",
            "Luna found a shiny acorn under the old oak tree.",
            "A cozy mouse hole under a large oak tree, watercolor style",
        ]
        mock = MockTextGenerator(responses=responses)
        engine = StoryEngine(text_generator=mock)

        # Start story
        start_prompt = engine.start_new_story(
            title="Luna's Adventure",
            author="Test Author",
        )
        assert "main character" in start_prompt.lower()

        # User describes their idea
        response = engine.process_user_input(
            "I want a story about a mouse named Luna who lives in a forest"
        )
        assert "Luna" in response

        # Generate first page
        page_text = engine.generate_page_text(
            page_number=1,
            page_purpose="Introduce Luna",
        )
        assert "Luna" in page_text or "acorn" in page_text

        # Add the page
        engine.add_page_to_story(page_number=1, text=page_text)

        # Generate illustration prompt
        ill_prompt = engine.generate_illustration_prompt(page_text)
        assert "oak tree" in ill_prompt.lower()

        # Verify final story state
        story = engine.get_story()
        assert story is not None
        assert story.title == "Luna's Adventure"
        assert story.page_count == 1
