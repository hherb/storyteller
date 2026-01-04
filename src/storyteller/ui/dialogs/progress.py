"""Progress overlay for the Storyteller GUI.

This module provides a modal overlay for showing generation
progress during AI operations.
"""

from __future__ import annotations

from collections.abc import Callable

import flet as ft

from storyteller.ui.theme import Colors, Spacing, Typography


class ProgressOverlay(ft.AlertDialog):
    """Modal overlay showing generation progress.

    Displays a progress indicator with status message and
    optional cancel button during long-running operations.
    """

    def __init__(
        self,
        on_cancel: Callable[[], None] | None = None,
    ) -> None:
        """Initialize the progress overlay.

        Args:
            on_cancel: Callback when cancel is clicked.
        """
        super().__init__()

        self.on_cancel_callback = on_cancel

        self._icon = ft.Icon(
            ft.Icons.AUTO_AWESOME,
            size=48,
            color=Colors.PRIMARY,
        )

        self._message = ft.Text(
            value="Generating...",
            size=Typography.SIZE_LG,
            weight=Typography.WEIGHT_MEDIUM,
            text_align=ft.TextAlign.CENTER,
        )

        self._progress_bar = ft.ProgressBar(
            width=300,
            color=Colors.PRIMARY,
            bgcolor=Colors.SURFACE_VARIANT,
        )

        self._time_remaining = ft.Text(
            value="",
            size=Typography.SIZE_SM,
            color=Colors.TEXT_SECONDARY,
            text_align=ft.TextAlign.CENTER,
        )

        self._build()

    def _build(self) -> None:
        """Build the overlay content."""
        self.modal = True

        self.content = ft.Container(
            content=ft.Column(
                controls=[
                    self._icon,
                    self._message,
                    self._progress_bar,
                    self._time_remaining,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=Spacing.MD,
            ),
            width=350,
            padding=Spacing.XL,
        )

        self.actions = [
            ft.TextButton(
                content=ft.Text("Cancel"),
                on_click=self._handle_cancel,
            ),
        ]

        self.actions_alignment = ft.MainAxisAlignment.CENTER

    def _handle_cancel(self, _e: ft.ControlEvent) -> None:
        """Handle cancel button click."""
        self.open = False
        try:
            if self.page:
                self.page.update()
        except RuntimeError:
            pass  # Control not mounted

        if self.on_cancel_callback:
            self.on_cancel_callback()

    def show(
        self,
        message: str = "Generating...",
        icon: str = ft.Icons.AUTO_AWESOME,
    ) -> None:
        """Show the progress overlay.

        Args:
            message: The status message to display.
            icon: The icon name to display.
        """
        self._message.value = message
        self._icon.icon = icon
        self._progress_bar.value = None  # Indeterminate
        self._time_remaining.value = ""
        self.open = True

        try:
            if self.page:
                self.page.update()
        except RuntimeError:
            pass  # Control not mounted

    def update_progress(
        self,
        progress: float,
        message: str | None = None,
        time_remaining: str | None = None,
    ) -> None:
        """Update the progress display.

        Args:
            progress: Progress value (0.0-1.0).
            message: Optional updated message.
            time_remaining: Optional time remaining string.
        """
        self._progress_bar.value = progress

        if message:
            self._message.value = message

        if time_remaining:
            self._time_remaining.value = f"Estimated time remaining: {time_remaining}"
        else:
            self._time_remaining.value = ""

        try:
            if self.page:
                self.content.update()
        except RuntimeError:
            pass  # Control not mounted

    def hide(self) -> None:
        """Hide the progress overlay."""
        self.open = False
        try:
            if self.page:
                self.page.update()
        except RuntimeError:
            pass  # Control not mounted

    def show_error(self, message: str) -> None:
        """Show an error state.

        Args:
            message: The error message to display.
        """
        self._icon.icon = ft.Icons.ERROR_OUTLINE
        self._icon.color = Colors.ERROR
        self._message.value = message
        self._message.color = Colors.ERROR
        self._progress_bar.visible = False
        self._time_remaining.value = ""

        try:
            if self.page:
                self.content.update()
        except RuntimeError:
            pass  # Control not mounted
