"""Settings view for the Storyteller GUI.

This module provides the Settings tab content with configuration
options for story metadata, LLM settings, and image generation.
"""

from __future__ import annotations

from collections.abc import Callable

import flet as ft

from storyteller.ui.state import state_manager
from storyteller.ui.theme import (
    BorderRadius,
    Colors,
    Dimensions,
    Spacing,
    Typography,
)


def _create_settings_card(
    title: str,
    icon: str,
    content: ft.Control,
) -> ft.Container:
    """Create a styled settings card.

    Args:
        title: Card title text.
        icon: Icon name for the card header.
        content: The card body content.

    Returns:
        A styled container with the card content.
    """
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Icon(
                            icon,
                            color=Colors.PRIMARY,
                            size=Dimensions.ICON_MD,
                        ),
                        ft.Text(
                            value=title,
                            size=Typography.SIZE_LG,
                            weight=Typography.WEIGHT_MEDIUM,
                            color=Colors.TEXT_PRIMARY,
                        ),
                    ],
                    spacing=Spacing.SM,
                ),
                ft.Divider(height=1, color=Colors.BORDER),
                content,
            ],
            spacing=Spacing.MD,
        ),
        bgcolor=Colors.SURFACE,
        border_radius=BorderRadius.LG,
        padding=Spacing.LG,
        border=ft.Border.all(1, Colors.BORDER),
        expand=True,
    )


class SettingsView(ft.Container):
    """Settings tab content with configuration options.

    Provides four settings cards:
    - Story Settings: Title, author, target age, page count
    - Text Generation: LLM model, temperature, max tokens
    - Illustration Style: Style preset selection
    - Image Generation: FLUX model, quantization, steps
    """

    def __init__(
        self,
        on_refresh_models: Callable[[], None] | None = None,
    ) -> None:
        """Initialize the settings view.

        Args:
            on_refresh_models: Callback to refresh available models.
        """
        super().__init__()

        self.on_refresh_models = on_refresh_models

        # Story settings fields
        self._title_field = ft.TextField(
            label="Story Title",
            value="",
            border_radius=BorderRadius.MD,
            on_change=self._on_title_change,
        )

        self._author_field = ft.TextField(
            label="Author",
            value="",
            border_radius=BorderRadius.MD,
            on_change=self._on_author_change,
        )

        self._target_age_dropdown = ft.Dropdown(
            label="Target Age",
            value="5-8",
            options=[
                ft.dropdown.Option(key="2-5", text="Pre-readers (ages 2-5)"),
                ft.dropdown.Option(key="5-8", text="Early readers (ages 5-8)"),
                ft.dropdown.Option(key="6-10", text="Primary school (ages 6-10)"),
            ],
            border_radius=BorderRadius.MD,
            on_select=self._on_target_age_change,
        )

        self._page_count_dropdown = ft.Dropdown(
            label="Total Pages",
            value="10",
            options=[
                ft.dropdown.Option(key="6", text="6 pages"),
                ft.dropdown.Option(key="8", text="8 pages"),
                ft.dropdown.Option(key="10", text="10 pages"),
                ft.dropdown.Option(key="12", text="12 pages"),
                ft.dropdown.Option(key="16", text="16 pages"),
            ],
            border_radius=BorderRadius.MD,
        )

        # LLM settings fields
        self._model_dropdown = ft.Dropdown(
            label="Text Model",
            value="phi4",
            options=[
                ft.dropdown.Option(key="phi4", text="phi4"),
            ],
            border_radius=BorderRadius.MD,
            on_select=self._on_model_change,
        )

        self._temperature_slider = ft.Slider(
            min=0.0,
            max=1.0,
            value=0.7,
            divisions=10,
            label="{value}",
            on_change=self._on_temperature_change,
        )

        self._temperature_label = ft.Text(
            value="Temperature: 0.7",
            size=Typography.SIZE_SM,
            color=Colors.TEXT_SECONDARY,
        )

        self._max_tokens_dropdown = ft.Dropdown(
            label="Max Tokens",
            value="auto",
            options=[
                ft.dropdown.Option(key="auto", text="Auto (recommended)"),
                ft.dropdown.Option(key="256", text="256"),
                ft.dropdown.Option(key="512", text="512"),
                ft.dropdown.Option(key="1024", text="1024"),
                ft.dropdown.Option(key="2048", text="2048"),
            ],
            border_radius=BorderRadius.MD,
        )

        # Style settings
        self._style_radio = ft.RadioGroup(
            value="watercolor",
            content=ft.Column(
                controls=[
                    ft.Radio(value="watercolor", label="Watercolor"),
                    ft.Radio(value="cartoon", label="Cartoon"),
                    ft.Radio(value="storybook_classic", label="Storybook Classic"),
                    ft.Radio(value="modern_digital", label="Modern Digital"),
                    ft.Radio(value="pencil_sketch", label="Pencil Sketch"),
                ],
                spacing=Spacing.SM,
            ),
            on_change=self._on_style_change,
        )

        # Image generation settings
        self._image_model_radio = ft.RadioGroup(
            value="schnell",
            content=ft.Column(
                controls=[
                    ft.Radio(value="schnell", label="FLUX.1-schnell (fast)"),
                    ft.Radio(value="dev", label="FLUX.1-dev (quality)"),
                ],
                spacing=Spacing.SM,
            ),
            on_change=self._on_image_model_change,
        )

        self._quantization_radio = ft.RadioGroup(
            value="4-bit",
            content=ft.Column(
                controls=[
                    ft.Radio(value="4-bit", label="4-bit quantized (~6GB RAM)"),
                    ft.Radio(value="8-bit", label="8-bit quantized (~12GB RAM)"),
                ],
                spacing=Spacing.SM,
            ),
            on_change=self._on_quantization_change,
        )

        self._steps_slider = ft.Slider(
            min=2,
            max=8,
            value=4,
            divisions=6,
            label="{value}",
            on_change=self._on_steps_change,
        )

        self._steps_label = ft.Text(
            value="Steps: 4",
            size=Typography.SIZE_SM,
            color=Colors.TEXT_SECONDARY,
        )

        self._auto_generate_checkbox = ft.Checkbox(
            label="Auto-generate illustrations after page text",
            value=False,
            on_change=self._on_auto_generate_change,
        )

        self._build()

    def _build(self) -> None:
        """Build the settings view layout."""
        # Story Settings Card
        story_card = _create_settings_card(
            title="Story Settings",
            icon=ft.Icons.BOOK,
            content=ft.Column(
                controls=[
                    self._title_field,
                    self._author_field,
                    self._target_age_dropdown,
                    self._page_count_dropdown,
                ],
                spacing=Spacing.MD,
            ),
        )

        # Text Generation Card
        text_gen_card = _create_settings_card(
            title="Text Generation",
            icon=ft.Icons.SMART_TOY,
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Container(
                                content=self._model_dropdown,
                                expand=True,
                            ),
                            ft.IconButton(
                                icon=ft.Icons.REFRESH,
                                tooltip="Refresh Models",
                                on_click=lambda _: (
                                    self.on_refresh_models()
                                    if self.on_refresh_models
                                    else None
                                ),
                            ),
                        ],
                    ),
                    ft.Column(
                        controls=[
                            self._temperature_label,
                            ft.Row(
                                controls=[
                                    ft.Text(
                                        "Precise",
                                        size=Typography.SIZE_SM,
                                        color=Colors.TEXT_SECONDARY,
                                    ),
                                    ft.Container(
                                        content=self._temperature_slider,
                                        expand=True,
                                    ),
                                    ft.Text(
                                        "Creative",
                                        size=Typography.SIZE_SM,
                                        color=Colors.TEXT_SECONDARY,
                                    ),
                                ],
                            ),
                        ],
                        spacing=Spacing.XS,
                    ),
                    self._max_tokens_dropdown,
                ],
                spacing=Spacing.MD,
            ),
        )

        # Illustration Style Card
        style_card = _create_settings_card(
            title="Illustration Style",
            icon=ft.Icons.PALETTE,
            content=ft.Column(
                controls=[
                    self._style_radio,
                ],
                spacing=Spacing.MD,
            ),
        )

        # Image Generation Card
        image_gen_card = _create_settings_card(
            title="Image Generation",
            icon=ft.Icons.IMAGE,
            content=ft.Column(
                controls=[
                    ft.Text(
                        "Model:",
                        size=Typography.SIZE_SM,
                        weight=Typography.WEIGHT_MEDIUM,
                    ),
                    self._image_model_radio,
                    ft.Text(
                        "Quantization:",
                        size=Typography.SIZE_SM,
                        weight=Typography.WEIGHT_MEDIUM,
                    ),
                    self._quantization_radio,
                    ft.Column(
                        controls=[
                            self._steps_label,
                            ft.Row(
                                controls=[
                                    ft.Text(
                                        "Fast",
                                        size=Typography.SIZE_SM,
                                        color=Colors.TEXT_SECONDARY,
                                    ),
                                    ft.Container(
                                        content=self._steps_slider,
                                        expand=True,
                                    ),
                                    ft.Text(
                                        "Quality",
                                        size=Typography.SIZE_SM,
                                        color=Colors.TEXT_SECONDARY,
                                    ),
                                ],
                            ),
                        ],
                        spacing=Spacing.XS,
                    ),
                    self._auto_generate_checkbox,
                ],
                spacing=Spacing.MD,
            ),
        )

        # Two-column layout for cards
        self.content = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[story_card, text_gen_card],
                        spacing=Spacing.LG,
                        expand=True,
                    ),
                    ft.Row(
                        controls=[style_card, image_gen_card],
                        spacing=Spacing.LG,
                        expand=True,
                    ),
                ],
                spacing=Spacing.LG,
                scroll=ft.ScrollMode.AUTO,
            ),
            padding=Spacing.LG,
            expand=True,
        )

        self.expand = True

    def _on_title_change(self, _e: ft.ControlEvent) -> None:
        """Handle title field change."""
        state_manager.mark_modified()

    def _on_author_change(self, _e: ft.ControlEvent) -> None:
        """Handle author field change."""
        state_manager.mark_modified()

    def _on_target_age_change(self, _e: ft.ControlEvent) -> None:
        """Handle target age change."""
        state_manager.mark_modified()

    def _on_style_change(self, _e: ft.ControlEvent) -> None:
        """Handle illustration style change."""
        state_manager.mark_modified()

    def _on_model_change(self, e: ft.ControlEvent) -> None:
        """Handle LLM model change."""
        if e.control.value:
            state_manager.update_config(llm_model=e.control.value)

    def _on_temperature_change(self, e: ft.ControlEvent) -> None:
        """Handle temperature slider change."""
        value = round(e.control.value, 1)
        self._temperature_label.value = f"Temperature: {value}"
        state_manager.update_config(llm_temperature=value)
        if self.page:
            self._temperature_label.update()

    def _on_image_model_change(self, e: ft.ControlEvent) -> None:
        """Handle image model change."""
        if e.control.value:
            state_manager.update_config(image_model=e.control.value)
            # Update steps range based on model
            if e.control.value == "schnell":
                self._steps_slider.min = 2
                self._steps_slider.max = 8
                self._steps_slider.value = 4
            else:
                self._steps_slider.min = 15
                self._steps_slider.max = 30
                self._steps_slider.value = 20
            if self.page:
                self._steps_slider.update()

    def _on_steps_change(self, e: ft.ControlEvent) -> None:
        """Handle steps slider change."""
        value = int(e.control.value)
        self._steps_label.value = f"Steps: {value}"
        state_manager.update_config(image_steps=value)
        if self.page:
            self._steps_label.update()

    def _on_auto_generate_change(self, e: ft.ControlEvent) -> None:
        """Handle auto-generate checkbox change."""
        state_manager.update_config(auto_generate_images=e.control.value)

    def _on_quantization_change(self, e: ft.ControlEvent) -> None:
        """Handle quantization radio change."""
        if e.control.value:
            state_manager.update_config(image_quantization=e.control.value)

    def update_available_models(self, models: list[str]) -> None:
        """Update the list of available LLM models.

        Args:
            models: List of model names.
        """
        self._model_dropdown.options = [
            ft.dropdown.Option(key=model, text=model) for model in models
        ]
        if models and self._model_dropdown.value not in models:
            self._model_dropdown.value = models[0]
        if self.page:
            self._model_dropdown.update()

    def get_story_settings(self) -> dict:
        """Get the current story settings.

        Returns:
            Dictionary with title, author, target_age, and style.
        """
        return {
            "title": self._title_field.value or "Untitled Story",
            "author": self._author_field.value or "Anonymous",
            "target_age": self._target_age_dropdown.value,
            "style": self._style_radio.value,
            "page_count": int(self._page_count_dropdown.value or 10),
        }

    def set_story_settings(
        self,
        title: str,
        author: str,
        target_age: str,
        style: str,
    ) -> None:
        """Set the story settings fields.

        Args:
            title: Story title.
            author: Author name.
            target_age: Target age range.
            style: Illustration style.
        """
        self._title_field.value = title
        self._author_field.value = author
        self._target_age_dropdown.value = target_age
        self._style_radio.value = style
        if self.page:
            self.update()

    def set_image_settings(
        self,
        model: str,
        steps: int,
        quantization: str,
    ) -> None:
        """Set the image generation settings fields.

        Args:
            model: FLUX model variant ('schnell' or 'dev').
            steps: Number of inference steps.
            quantization: Quantization level ('4-bit' or '8-bit').
        """
        self._image_model_radio.value = model
        self._steps_slider.value = steps
        self._steps_label.value = f"Steps: {steps}"
        self._quantization_radio.value = quantization
        if self.page:
            self.update()

    def set_llm_settings(
        self,
        model: str,
        temperature: float,
    ) -> None:
        """Set the LLM settings fields.

        Args:
            model: LLM model name.
            temperature: Temperature value (0.0-1.0).
        """
        self._model_dropdown.value = model
        self._temperature_slider.value = temperature
        self._temperature_label.value = f"Temperature: {temperature}"
        if self.page:
            self.update()
