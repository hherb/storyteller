"""Status bar component for the Storyteller GUI.

This module provides the bottom status bar that shows save status,
current model, page position, and generation status.
"""

from __future__ import annotations

import flet as ft

from storyteller.ui.state import GenerationStatus
from storyteller.ui.theme import Colors, Dimensions, Spacing, Typography


class StatusBar(ft.Container):
    """Bottom status bar showing application status.

    Displays save status, current LLM model, page position,
    and generation progress during AI operations.
    """

    def __init__(self) -> None:
        """Initialize the status bar."""
        super().__init__()

        self._save_status = ft.Row(
            controls=[
                ft.Icon(
                    name=ft.Icons.CHECK_CIRCLE,
                    color=Colors.SUCCESS,
                    size=Dimensions.ICON_SM,
                ),
                ft.Text(
                    value="Saved",
                    size=Typography.SIZE_SM,
                    color=Colors.TEXT_SECONDARY,
                ),
            ],
            spacing=Spacing.XS,
        )

        self._model_indicator = ft.Text(
            value="Model: phi4",
            size=Typography.SIZE_SM,
            color=Colors.TEXT_SECONDARY,
        )

        self._page_indicator = ft.Text(
            value="Page 1 of 1",
            size=Typography.SIZE_SM,
            color=Colors.TEXT_SECONDARY,
        )

        self._generation_indicator = ft.Row(
            controls=[
                ft.ProgressRing(
                    width=Dimensions.ICON_SM,
                    height=Dimensions.ICON_SM,
                    stroke_width=2,
                    color=Colors.PRIMARY,
                ),
                ft.Text(
                    value="Generating...",
                    size=Typography.SIZE_SM,
                    color=Colors.PRIMARY,
                ),
            ],
            spacing=Spacing.XS,
            visible=False,
        )

        self._build()

    def _build(self) -> None:
        """Build the status bar layout."""
        # Dividers between sections
        divider = ft.VerticalDivider(width=1, color=Colors.BORDER)

        self.content = ft.Row(
            controls=[
                self._save_status,
                divider,
                self._model_indicator,
                divider,
                self._page_indicator,
                ft.Container(expand=True),  # Spacer
                self._generation_indicator,
            ],
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=Spacing.MD,
        )

        self.bgcolor = Colors.SURFACE_VARIANT
        self.height = Dimensions.STATUS_BAR_HEIGHT
        self.padding = ft.Padding(Spacing.MD, Spacing.XS, Spacing.MD, Spacing.XS)
        self.border = ft.Border(
            top=ft.BorderSide(1, Colors.BORDER),
        )

    def update_save_status(self, is_saved: bool) -> None:
        """Update the save status indicator.

        Args:
            is_saved: Whether the current project is saved.
        """
        icon = self._save_status.controls[0]
        text = self._save_status.controls[1]

        if is_saved:
            icon.name = ft.Icons.CHECK_CIRCLE
            icon.color = Colors.SUCCESS
            text.value = "Saved"
        else:
            icon.name = ft.Icons.CIRCLE_OUTLINED
            icon.color = Colors.WARNING
            text.value = "Unsaved"

        if self.page:
            self._save_status.update()

    def update_model(self, model_name: str) -> None:
        """Update the model indicator.

        Args:
            model_name: Name of the current LLM model.
        """
        self._model_indicator.value = f"Model: {model_name}"
        if self.page:
            self._model_indicator.update()

    def update_page(self, current: int, total: int) -> None:
        """Update the page indicator.

        Args:
            current: Current page number (1-indexed).
            total: Total number of pages.
        """
        self._page_indicator.value = f"Page {current} of {total}"
        if self.page:
            self._page_indicator.update()

    def update_generation_status(
        self,
        status: GenerationStatus,
        message: str = "",
    ) -> None:
        """Update the generation status indicator.

        Args:
            status: Current generation status.
            message: Optional status message to display.
        """
        if status == GenerationStatus.IDLE:
            self._generation_indicator.visible = False
        else:
            self._generation_indicator.visible = True
            text = self._generation_indicator.controls[1]

            if status == GenerationStatus.GENERATING_TEXT:
                text.value = message or "Generating text..."
            elif status == GenerationStatus.GENERATING_IMAGE:
                text.value = message or "Generating image..."
            elif status == GenerationStatus.ERROR:
                text.value = message or "Error"
                text.color = Colors.ERROR

        if self.page:
            self._generation_indicator.update()
