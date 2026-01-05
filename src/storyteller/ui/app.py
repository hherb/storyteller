"""Main application entry point for the Storyteller GUI.

This module provides the main application window with tabbed
navigation and coordinates all UI components.
"""

from __future__ import annotations

import logging
import threading
from pathlib import Path
from typing import TYPE_CHECKING

import flet as ft

from storyteller.core import (
    Story,
    StoryEngine,
    add_character,
    add_page,
    create_character,
    create_page,
    create_story,
    list_stories,
    load_story,
    save_story,
    update_page,
)
from storyteller.generation import (
    GenerationProgress,
    ImageConfig,
    ImageGenerator,
    OllamaClient,
    build_illustration_prompt_for_page,
    check_mflux_available,
    check_platform,
    create_text_generator,
)
from storyteller.ui.components import StatusBar, StorytellerAppBar
from storyteller.ui.dialogs import CharacterDialog, NewStoryDialog, ProgressOverlay
from storyteller.ui.state import ActiveTab, AppConfig, GenerationStatus, state_manager
from storyteller.ui.theme import Colors, apply_theme
from storyteller.ui.views import CreateView, PreviewView, SettingsView

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class StorytellerApp:
    """Main application controller.

    Coordinates all UI components and manages the application lifecycle.

    Attributes:
        page: The Flet page instance.
    """

    def __init__(self, page: ft.Page) -> None:
        """Initialize the application.

        Args:
            page: The Flet page to build the UI on.
        """
        self.page = page
        self._ui_lock = threading.Lock()  # Lock for thread-safe UI updates
        self._setup_page()
        self._create_components()
        self._build_layout()
        self._setup_callbacks()
        self._initialize_state()

    def _setup_page(self) -> None:
        """Configure the page settings."""
        self.page.title = "Storyteller"
        self.page.window.width = 1200
        self.page.window.height = 800
        self.page.window.min_width = 900
        self.page.window.min_height = 600
        apply_theme(self.page)

    def _create_components(self) -> None:
        """Create all UI components."""
        # App bar
        self._app_bar = StorytellerAppBar(
            on_new=self._handle_new_story,
            on_open=self._handle_open_story,
            on_save=self._handle_save_story,
            on_export=self._handle_export,
        )

        # Status bar
        self._status_bar = StatusBar()

        # Views
        self._settings_view = SettingsView(
            on_refresh_models=self._refresh_models,
        )

        self._create_view = CreateView(
            on_send=self._handle_send_message,
            on_generate_page=self._handle_generate_page,
            on_generate_image=self._handle_generate_image,
            on_add_character=self._handle_add_character,
            on_page_select=self._handle_page_select,
            on_add_page=self._handle_add_page,
        )

        self._preview_view = PreviewView(
            on_regenerate=self._handle_generate_image,
            on_edit=self._handle_edit_from_preview,
            on_fullscreen=self._handle_fullscreen,
            on_export=self._handle_export,
            on_page_change=self._handle_page_select,
        )

        # Dialogs
        self._new_story_dialog = NewStoryDialog(
            on_create=self._create_new_story,
        )
        self.page.overlay.append(self._new_story_dialog)

        self._character_dialog = CharacterDialog(
            on_save=self._save_character,
            on_extract_traits=self._extract_character_traits,
        )
        self.page.overlay.append(self._character_dialog)

        self._progress_overlay = ProgressOverlay(
            on_cancel=self._handle_cancel_generation,
        )
        self.page.overlay.append(self._progress_overlay)

        # Image generator (lazy loaded)
        self._image_generator: ImageGenerator | None = None
        self._generation_cancel_requested = False

        # Tabs - using new Flet 0.80+ API with TabBar + TabBarView
        self._tabs = ft.Tabs(
            length=3,
            selected_index=1,  # Start on Create tab
            animation_duration=300,
            on_change=self._handle_tab_change,
            expand=True,
            content=ft.Column(
                expand=True,
                spacing=0,
                controls=[
                    ft.TabBar(
                        tabs=[
                            ft.Tab(label="Settings", icon=ft.Icons.SETTINGS),
                            ft.Tab(label="Create Story", icon=ft.Icons.EDIT),
                            ft.Tab(label="Preview", icon=ft.Icons.VISIBILITY),
                        ],
                    ),
                    ft.TabBarView(
                        expand=True,
                        controls=[
                            self._settings_view,
                            self._create_view,
                            self._preview_view,
                        ],
                    ),
                ],
            ),
        )

    def _build_layout(self) -> None:
        """Build the main application layout."""
        self.page.add(
            ft.Column(
                controls=[
                    self._app_bar,
                    ft.Container(
                        content=self._tabs,
                        expand=True,
                    ),
                    self._status_bar,
                ],
                spacing=0,
                expand=True,
            )
        )

    def _setup_callbacks(self) -> None:
        """Set up state change callbacks."""
        state_manager.add_listener(self._on_state_change)

    def _initialize_state(self) -> None:
        """Initialize application state."""
        # Load saved configuration
        state_manager.load_config()
        print(f"DEBUG: Loaded config: {state_manager.state.config}")

        # Apply loaded config to settings view
        config = state_manager.state.config
        self._settings_view.set_image_settings(
            model=config.image_model,
            steps=config.image_steps,
            quantization=config.image_quantization,
        )
        self._settings_view.set_llm_settings(
            model=config.llm_model,
            temperature=config.llm_temperature,
        )

        # Try to fetch available models
        self._refresh_models()

        # Set initial page count
        self._preview_view.set_page_count(10, 1)

        # Update UI with initial state
        self._on_state_change()

    def _on_state_change(self) -> None:
        """Handle state changes and update UI accordingly."""
        state = state_manager.state

        # Update app bar title
        if state.current_story:
            self._app_bar.update_title(
                state.current_story.metadata.title,
                state.is_modified,
            )
        else:
            self._app_bar.update_title(None)

        # Update status bar
        self._status_bar.update_save_status(not state.is_modified)
        self._status_bar.update_model(state.config.llm_model)

        if state.current_story:
            page_count = len(state.current_story.pages) or 1
            self._status_bar.update_page(state.current_page_number, page_count)
        else:
            self._status_bar.update_page(1, 1)

        self._status_bar.update_generation_status(state.generation_status)

    def _handle_tab_change(self, e: ft.ControlEvent) -> None:
        """Handle tab selection change."""
        tab_map = {0: ActiveTab.SETTINGS, 1: ActiveTab.CREATE, 2: ActiveTab.PREVIEW}
        state_manager.set_active_tab(tab_map.get(e.control.selected_index, ActiveTab.CREATE))

    def _handle_new_story(self) -> None:
        """Handle New Story button click."""
        self._new_story_dialog.reset()
        self._new_story_dialog.open = True
        self.page.update()

    def _create_new_story(self, settings: dict) -> None:
        """Create a new story with the given settings.

        Args:
            settings: Dictionary with story settings.
        """
        # Create the story
        story = create_story(
            title=settings["title"],
            author=settings["author"],
            target_age=settings["target_age"],
            style=settings["style"],
        )

        # Set up the engine
        try:
            generator = create_text_generator(
                backend="ollama",
                model=state_manager.state.config.llm_model,
            )
            engine = StoryEngine(text_generator=generator)
            engine.set_story(story)
            state_manager.state.engine = engine
        except Exception as e:
            logger.warning(f"Failed to create text generator: {e}")

        # Update state
        state_manager.set_story(story)
        state_manager.clear_conversation()

        # Update views
        self._settings_view.set_story_settings(
            title=settings["title"],
            author=settings["author"],
            target_age=settings["target_age"],
            style=settings["style"],
        )

        page_count = settings.get("page_count", 10)
        self._preview_view.set_page_count(page_count, 1)
        self._update_page_list()

        # Switch to Create tab
        self._tabs.selected_index = 1
        self.page.update()

    def _handle_open_story(self) -> None:
        """Handle Open Story button click."""
        # For now, show a simple file picker or list recent stories
        stories = list_stories()
        if stories:
            # Load the most recent story
            path, metadata = stories[0]
            story = load_story(path)
            state_manager.set_story(story)
            self._update_ui_from_story(story)
        else:
            # Show a snackbar
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("No saved stories found."),
            )
            self.page.snack_bar.open = True
            self.page.update()

    def _handle_save_story(self) -> None:
        """Handle Save Story button click."""
        state = state_manager.state
        if state.current_story:
            try:
                saved_story = save_story(state.current_story)
                state_manager.set_story(saved_story)
                state_manager.mark_saved()

                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("Story saved successfully!"),
                    bgcolor=Colors.SUCCESS,
                )
                self.page.snack_bar.open = True
                self.page.update()
            except Exception as e:
                logger.error(f"Failed to save story: {e}")
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Failed to save: {e}"),
                    bgcolor=Colors.ERROR,
                )
                self.page.snack_bar.open = True
                self.page.update()

    def _handle_export(self) -> None:
        """Handle Export button click."""
        # TODO: Implement export dialog
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text("Export feature coming soon!"),
        )
        self.page.snack_bar.open = True
        self.page.update()

    def _refresh_models(self) -> None:
        """Refresh the list of available LLM models."""
        try:
            client = OllamaClient()
            models = client.list_models()
            state_manager.set_available_models(models)
            self._settings_view.update_available_models(models)
        except Exception as e:
            logger.warning(f"Failed to fetch models: {e}")
            # Use default
            state_manager.set_available_models(["phi4"])
            self._settings_view.update_available_models(["phi4"])

    def _handle_send_message(self, message: str) -> None:
        """Handle sending a message in the conversation.

        Args:
            message: The user's message.
        """
        state = state_manager.state

        # Show typing indicator
        self._create_view.set_typing(True)
        state_manager.set_generation_status(GenerationStatus.GENERATING_TEXT)

        # Process with engine if available
        if state.engine:
            try:
                response = state.engine.process_user_input(message)
                self._create_view.add_assistant_message(response)
                state_manager.add_conversation_message("user", message)
                state_manager.add_conversation_message("assistant", response)
            except Exception as e:
                logger.error(f"Failed to process message: {e}")
                self._create_view.add_assistant_message(
                    f"Sorry, I encountered an error: {e}"
                )
        else:
            # No engine, provide a placeholder response
            self._create_view.add_assistant_message(
                "I'm ready to help you create your story! "
                "Please create a new story first using the New button."
            )

        self._create_view.set_typing(False)
        state_manager.set_generation_status(GenerationStatus.IDLE)
        self.page.update()

    def _handle_generate_page(self) -> None:
        """Handle generate page text request."""
        state = state_manager.state

        if not state.engine or not state.current_story:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("Please create a story first."),
            )
            self.page.snack_bar.open = True
            self.page.update()
            return

        state_manager.set_generation_status(GenerationStatus.GENERATING_TEXT)
        self._progress_overlay.show("Generating page text...")

        try:
            page_number = state.current_page_number
            page_text = state.engine.generate_page_text(
                page_number=page_number,
                page_purpose="story",
                total_pages=len(state.current_story.pages) or 10,
            )

            # Check if page already exists in story
            existing_page = state.current_story.get_page(page_number)
            if existing_page:
                # Update existing page
                updated_story = update_page(
                    state.current_story,
                    page_number,
                    text=page_text,
                )
            else:
                # Create new page and add to story
                new_page = create_page(
                    page_number=page_number,
                    text=page_text,
                )
                updated_story = add_page(state.current_story, new_page)

            # Update state with the new story
            state_manager.set_story(updated_story)
            state_manager.mark_modified()

            # Update UI display
            self._create_view.update_current_page(page_text, "")
            self._update_page_list()

            logger.info(f"Generated and saved text for page {page_number}")
        except Exception as e:
            logger.error(f"Failed to generate page: {e}")
            state_manager.set_error(str(e))
        finally:
            self._progress_overlay.hide()
            state_manager.set_generation_status(GenerationStatus.IDLE)
            self.page.update()

    def _create_image_config(self, app_config: "AppConfig") -> ImageConfig:
        """Create an ImageConfig from app configuration.

        Handles conversion of UI-friendly settings to ImageConfig,
        including validation and fallback to safe defaults.

        Args:
            app_config: The AppConfig from state.

        Returns:
            A valid ImageConfig instance.
        """
        # Parse quantization from string (e.g., "4-bit" -> 4)
        quantize_str = app_config.image_quantization
        quantize = 4 if "4" in quantize_str else 8

        # Get model and steps
        model = app_config.image_model
        steps = app_config.image_steps

        # Validate steps for the model, use safe defaults if invalid
        if model == "schnell":
            if not (2 <= steps <= 8):
                logger.warning(
                    f"Steps {steps} invalid for schnell model, using default 4"
                )
                steps = 4
        elif model == "dev":
            if not (15 <= steps <= 30):
                logger.warning(
                    f"Steps {steps} invalid for dev model, using default 20"
                )
                steps = 20

        return ImageConfig(
            model=model,
            steps=steps,
            quantize=quantize,
        )

    def _handle_generate_image(self) -> None:
        """Handle generate illustration request."""
        print("DEBUG: _handle_generate_image called")
        state = state_manager.state

        # Check if we have a story
        if not state.current_story:
            print("DEBUG: No story exists - cannot generate image")
            self._show_snackbar("Please create a story first.", Colors.WARNING)
            return

        # Check if current page has text
        page = state.current_story.get_page(state.current_page_number)
        print(f"DEBUG: Current page: {state.current_page_number}, page object: {page}")
        if not page or not page.text:
            print(f"DEBUG: Page has no text - page={page}, text={page.text if page else None}")
            self._show_snackbar(
                "Please add text to this page before generating an illustration.",
                Colors.WARNING,
            )
            return

        # Check platform and MFLUX availability
        platform_ok, platform_msg = check_platform()
        print(f"DEBUG: Platform check: ok={platform_ok}, msg={platform_msg}")
        if not platform_ok:
            self._show_snackbar(platform_msg, Colors.ERROR)
            return

        mflux_ok, mflux_msg = check_mflux_available()
        print(f"DEBUG: MFLUX check: ok={mflux_ok}, msg={mflux_msg}")
        if not mflux_ok:
            self._show_snackbar(mflux_msg, Colors.ERROR)
            return

        print("DEBUG: All checks passed, starting image generation")

        # Show progress overlay
        self._progress_overlay.show(
            "Generating illustration...",
            icon=ft.Icons.BRUSH,
        )
        state_manager.set_generation_status(GenerationStatus.GENERATING_IMAGE)
        self._generation_cancel_requested = False

        # Run generation in background thread
        def generate_in_background() -> None:
            try:
                self._run_image_generation(state, page)
            except Exception as e:
                logger.error(f"Image generation failed: {e}")
                self._on_generation_complete(success=False, error=str(e))

        thread = threading.Thread(target=generate_in_background, daemon=True)
        thread.start()

    def _run_image_generation(self, state, page) -> None:
        """Run image generation in background.

        Args:
            state: Current app state.
            page: The page to generate an image for.
        """
        # Build the illustration prompt
        characters = [
            (c.name, c.description, c.visual_traits)
            for c in state.current_story.characters
        ]

        prompt = build_illustration_prompt_for_page(
            page_text=page.text,
            all_characters=characters,
            style=state.current_story.metadata.style,
        )

        logger.info(f"Generated prompt: {prompt[:100]}...")

        # Set up output path
        if state.current_story.project_path:
            output_dir = state.current_story.project_path / "pages"
        else:
            # Use temp directory for unsaved stories
            import tempfile
            output_dir = Path(tempfile.gettempdir()) / "storyteller" / "temp_story"

        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"page_{page.page_number:02d}.png"

        # Create or get image generator with safe config
        config = self._create_image_config(state.config)

        if self._image_generator is None:
            self._image_generator = ImageGenerator(config)
        else:
            # Update config if needed
            self._image_generator.update_config(config)

        # Progress callback (thread-safe)
        def on_progress(progress: GenerationProgress) -> None:
            if self._generation_cancel_requested:
                return
            with self._ui_lock:
                self._progress_overlay.update_progress(
                    progress.progress,
                    time_remaining=progress.status,
                )
                self.page.update()

        # Generate the image
        result = self._image_generator.generate(
            prompt=prompt,
            output_path=output_path,
            progress_callback=on_progress,
        )

        if result.success:
            # Update the story with the new illustration path
            self._on_generation_complete(
                success=True,
                image_path=result.image_path,
                page_number=page.page_number,
                prompt=prompt,
            )
        else:
            self._on_generation_complete(
                success=False,
                error=result.error or "Unknown error",
            )

    def _on_generation_complete(
        self,
        success: bool,
        error: str | None = None,
        image_path: Path | None = None,
        page_number: int | None = None,
        prompt: str | None = None,
    ) -> None:
        """Handle generation completion (called from background thread).

        Args:
            success: Whether generation succeeded.
            error: Error message if failed.
            image_path: Path to generated image.
            page_number: Page number that was generated.
            prompt: The prompt that was used.
        """
        logger.info(f"Generation complete: success={success}, page={page_number}")

        # Use lock for thread-safe UI updates
        with self._ui_lock:
            # Hide progress overlay
            self._progress_overlay.hide()
            state_manager.set_generation_status(GenerationStatus.IDLE)

            if success and image_path and page_number:
                # Update story with new illustration
                state = state_manager.state
                if state.current_story:
                    try:
                        updated_story = update_page(
                            state.current_story,
                            page_number,
                            illustration_path=image_path,
                            illustration_prompt=prompt or "",
                        )
                        state_manager.set_story(updated_story)
                        state_manager.mark_modified()

                        # Update preview and current page display
                        self._preview_view.set_image(image_path)
                        self._update_page_list()
                        self._update_current_page_display()

                        self._show_snackbar(
                            f"Illustration generated for page {page_number}!",
                            Colors.SUCCESS,
                        )
                    except Exception as e:
                        logger.error(f"Failed to update story: {e}")
                        self._show_snackbar(
                            f"Failed to save illustration: {e}", Colors.ERROR
                        )
            else:
                self._show_snackbar(
                    f"Generation failed: {error or 'Unknown error'}",
                    Colors.ERROR,
                )

            self.page.update()

    def _show_snackbar(self, message: str, bgcolor: str | None = None) -> None:
        """Show a snackbar message.

        Args:
            message: The message to show.
            bgcolor: Optional background color.
        """
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=bgcolor,
        )
        self.page.snack_bar.open = True
        self.page.update()

    def _handle_add_character(self) -> None:
        """Handle add character request."""
        if not state_manager.state.current_story:
            self._show_snackbar("Please create a story first.", Colors.WARNING)
            return

        self._character_dialog.reset()
        self._character_dialog.open = True
        self.page.update()

    def _save_character(self, char_data: dict) -> None:
        """Save a new character from the dialog.

        Args:
            char_data: Dictionary with name, description, visual_traits.
        """
        state = state_manager.state
        if not state.current_story:
            return

        # Create the character
        character = create_character(
            name=char_data["name"],
            description=char_data["description"],
            visual_traits=char_data.get("visual_traits", []),
        )

        # Add to story
        updated_story = add_character(state.current_story, character)
        state_manager.set_story(updated_story)
        state_manager.mark_modified()

        # Update character list in create view
        self._update_character_list()

        self._show_snackbar(f"Character '{character.name}' added!", Colors.SUCCESS)

    def _extract_character_traits(self, name: str, description: str) -> list[str]:
        """Extract visual traits from character description using LLM.

        Args:
            name: Character name.
            description: Character description.

        Returns:
            List of visual trait strings.
        """
        state = state_manager.state

        if not state.engine:
            # Return empty list if no engine available
            return []

        try:
            # Use the engine to extract traits
            from storyteller.generation import EXTRACT_VISUAL_TRAITS

            prompt = EXTRACT_VISUAL_TRAITS.render(
                name=name,
                description=description,
            )

            response = state.engine.text_generator.generate(prompt)
            # Parse comma-separated traits
            traits = [t.strip() for t in response.split(",") if t.strip()]
            return traits[:6]  # Limit to 6 traits
        except Exception as e:
            logger.warning(f"Failed to extract traits: {e}")
            return []

    def _update_character_list(self) -> None:
        """Update the character list in the create view."""
        state = state_manager.state
        if state.current_story:
            characters = [
                {"name": c.name, "description": c.description}
                for c in state.current_story.characters
            ]
            self._create_view.update_character_list(characters)

    def _handle_page_select(self, page_number: int) -> None:
        """Handle page selection.

        Args:
            page_number: The selected page number (1-indexed).
        """
        state_manager.set_current_page(page_number)
        self._preview_view.set_page_count(
            state_manager.state.current_story.pages.__len__()
            if state_manager.state.current_story
            else 10,
            page_number,
        )
        self._update_current_page_display()

    def _handle_add_page(self) -> None:
        """Handle add page request."""
        state = state_manager.state
        if not state.current_story:
            self._show_snackbar("Please create a story first.", Colors.WARNING)
            return

        # Calculate next page number
        existing_pages = len(state.current_story.pages)
        new_page_number = existing_pages + 1

        # Create new empty page
        new_page = create_page(page_number=new_page_number, text="")
        updated_story = add_page(state.current_story, new_page)

        # Update state
        state_manager.set_story(updated_story)
        state_manager.set_current_page(new_page_number)
        state_manager.mark_modified()

        # Update UI
        self._update_page_list()
        self._update_current_page_display()
        self._preview_view.set_page_count(new_page_number, new_page_number)

        self._show_snackbar(f"Added page {new_page_number}", Colors.SUCCESS)
        self.page.update()

    def _handle_edit_from_preview(self) -> None:
        """Handle edit request from preview tab."""
        self._tabs.selected_index = 1  # Switch to Create tab
        self.page.update()

    def _handle_fullscreen(self) -> None:
        """Handle fullscreen preview request."""
        # TODO: Implement fullscreen preview
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text("Fullscreen preview coming soon!"),
        )
        self.page.snack_bar.open = True
        self.page.update()

    def _handle_cancel_generation(self) -> None:
        """Handle cancel generation request."""
        self._generation_cancel_requested = True

        # Cancel the image generator if running
        if self._image_generator:
            self._image_generator.cancel()

        state_manager.set_generation_status(GenerationStatus.IDLE)
        self._progress_overlay.hide()
        self._show_snackbar("Generation cancelled.", Colors.WARNING)

    def _update_ui_from_story(self, story: Story) -> None:
        """Update all UI components from a loaded story.

        Args:
            story: The story to display.
        """
        logger.info(
            f"Updating UI from story: {story.metadata.title}, "
            f"{len(story.pages)} pages, {len(story.characters)} characters"
        )

        # Update settings
        self._settings_view.set_story_settings(
            title=story.metadata.title,
            author=story.metadata.author,
            target_age=story.metadata.target_age,
            style=story.metadata.style,
        )

        # Update character list
        self._update_character_list()

        # Update page list and preview
        page_count = len(story.pages) or 1
        self._preview_view.set_page_count(page_count, 1)
        self._update_page_list()

        if story.pages:
            first_page = story.pages[0]
            self._create_view.update_current_page(
                first_page.text,
                first_page.illustration_prompt,
            )
            self._preview_view.set_page_text(first_page.text)
            if first_page.illustration_path:
                self._preview_view.set_image(first_page.illustration_path)

        self.page.update()

    def _update_page_list(self) -> None:
        """Update the page list in the create view."""
        state = state_manager.state
        if state.current_story:
            pages = [
                {
                    "number": page.page_number,
                    "has_text": bool(page.text),
                    "has_image": page.has_illustration,
                }
                for page in state.current_story.pages
            ]
        else:
            # Create placeholder pages
            page_count = 10
            pages = [
                {"number": i, "has_text": False, "has_image": False}
                for i in range(1, page_count + 1)
            ]

        self._create_view.update_page_list(pages, state.current_page_number)

    def _update_current_page_display(self) -> None:
        """Update the current page display in both views."""
        state = state_manager.state
        if state.current_story and state.current_story.pages:
            page = state.current_story.get_page(state.current_page_number)
            if page:
                self._create_view.update_current_page(
                    page.text,
                    page.illustration_prompt,
                )
                self._preview_view.set_page_text(page.text)
                if page.illustration_path:
                    self._preview_view.set_image(page.illustration_path)


def main(page: ft.Page) -> None:
    """Main entry point for the Flet application.

    Args:
        page: The Flet page instance.
    """
    StorytellerApp(page)


def run() -> None:
    """Run the Storyteller application."""
    ft.app(target=main)


if __name__ == "__main__":
    run()
