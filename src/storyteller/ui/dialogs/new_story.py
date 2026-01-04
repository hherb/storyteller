"""New Story dialog for the Storyteller GUI.

This module provides the dialog for creating a new story project
with title, author, and settings configuration.
"""

from __future__ import annotations

from collections.abc import Callable

import flet as ft

from storyteller.ui.theme import BorderRadius, Colors, Spacing, Typography


class NewStoryDialog(ft.AlertDialog):
    """Dialog for creating a new story.

    Collects story title, author name, target age group,
    illustration style, and page count.
    """

    def __init__(
        self,
        on_create: Callable[[dict], None] | None = None,
    ) -> None:
        """Initialize the new story dialog.

        Args:
            on_create: Callback when story is created, receives settings dict.
        """
        super().__init__()

        self.on_create_callback = on_create

        # Form fields
        self._title_field = ft.TextField(
            label="What would you like to call your story?",
            hint_text="Enter story title",
            border_radius=BorderRadius.MD,
            autofocus=True,
        )

        self._author_field = ft.TextField(
            label="Who is the author?",
            hint_text="Enter author name",
            border_radius=BorderRadius.MD,
        )

        self._age_radio = ft.RadioGroup(
            value="5-8",
            content=ft.Column(
                controls=[
                    ft.Radio(
                        value="2-5",
                        label="Toddlers & Pre-readers (ages 2-5)",
                    ),
                    ft.Radio(
                        value="5-8",
                        label="Early Readers (ages 5-8)",
                    ),
                    ft.Radio(
                        value="6-10",
                        label="Primary School (ages 6-10)",
                    ),
                ],
                spacing=Spacing.XS,
            ),
        )

        self._style_dropdown = ft.Dropdown(
            label="Illustration style",
            value="watercolor",
            options=[
                ft.dropdown.Option(
                    key="watercolor",
                    text="Watercolor - Soft, dreamy, pastel colors",
                ),
                ft.dropdown.Option(
                    key="cartoon",
                    text="Cartoon - Bright, bold, fun shapes",
                ),
                ft.dropdown.Option(
                    key="storybook_classic",
                    text="Storybook Classic - Traditional, detailed",
                ),
                ft.dropdown.Option(
                    key="modern_digital",
                    text="Modern Digital - Clean, vibrant",
                ),
                ft.dropdown.Option(
                    key="pencil_sketch",
                    text="Pencil Sketch - Hand-drawn feel",
                ),
            ],
            border_radius=BorderRadius.MD,
        )

        self._pages_dropdown = ft.Dropdown(
            label="How many pages?",
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

        self._build()

    def _build(self) -> None:
        """Build the dialog content."""
        self.modal = True
        self.title = ft.Text(
            value="Create New Story",
            size=Typography.SIZE_XL,
            weight=Typography.WEIGHT_BOLD,
        )

        self.content = ft.Container(
            content=ft.Column(
                controls=[
                    self._title_field,
                    self._author_field,
                    ft.Text(
                        value="Who will read this story?",
                        size=Typography.SIZE_MD,
                        weight=Typography.WEIGHT_MEDIUM,
                    ),
                    self._age_radio,
                    self._style_dropdown,
                    self._pages_dropdown,
                ],
                spacing=Spacing.MD,
                tight=True,
            ),
            width=450,
            padding=Spacing.MD,
        )

        self.actions = [
            ft.TextButton(
                text="Cancel",
                on_click=self._handle_cancel,
            ),
            ft.ElevatedButton(
                text="Create Story",
                icon=ft.Icons.ADD,
                bgcolor=Colors.PRIMARY,
                color=Colors.TEXT_ON_PRIMARY,
                on_click=self._handle_create,
            ),
        ]

        self.actions_alignment = ft.MainAxisAlignment.END

    def _handle_cancel(self, _e: ft.ControlEvent) -> None:
        """Handle cancel button click."""
        self.open = False
        if self.page:
            self.page.update()

    def _handle_create(self, _e: ft.ControlEvent) -> None:
        """Handle create button click."""
        # Validate required fields
        title = self._title_field.value
        if not title or not title.strip():
            self._title_field.error_text = "Please enter a title"
            if self.page:
                self._title_field.update()
            return

        # Collect settings
        settings = {
            "title": title.strip(),
            "author": self._author_field.value or "Anonymous",
            "target_age": self._age_radio.value,
            "style": self._style_dropdown.value,
            "page_count": int(self._pages_dropdown.value or 10),
        }

        # Close dialog
        self.open = False
        if self.page:
            self.page.update()

        # Call callback
        if self.on_create_callback:
            self.on_create_callback(settings)

    def reset(self) -> None:
        """Reset all fields to defaults."""
        self._title_field.value = ""
        self._title_field.error_text = None
        self._author_field.value = ""
        self._age_radio.value = "5-8"
        self._style_dropdown.value = "watercolor"
        self._pages_dropdown.value = "10"
