"""Preview view for the Storyteller GUI.

This module provides the preview tab content with illustration
display, page navigation, and export options.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import flet as ft

from storyteller.ui.theme import (
    BorderRadius,
    Colors,
    Spacing,
    Typography,
)


class PreviewView(ft.Container):
    """Preview tab content.

    Displays the current page illustration with text,
    page navigation strip, and action buttons.
    """

    def __init__(
        self,
        on_regenerate: Callable[[], None] | None = None,
        on_edit: Callable[[], None] | None = None,
        on_fullscreen: Callable[[], None] | None = None,
        on_export: Callable[[], None] | None = None,
        on_page_change: Callable[[int], None] | None = None,
    ) -> None:
        """Initialize the preview view.

        Args:
            on_regenerate: Callback to regenerate current illustration.
            on_edit: Callback to edit current page text.
            on_fullscreen: Callback to enter fullscreen mode.
            on_export: Callback to export to PDF.
            on_page_change: Callback when page is changed.
        """
        super().__init__()

        self.on_regenerate = on_regenerate
        self.on_edit = on_edit
        self.on_fullscreen = on_fullscreen
        self.on_export = on_export
        self.on_page_change = on_page_change

        self._current_page = 1
        self._total_pages = 1

        # Image display
        self._image_container = ft.Container(
            content=self._create_placeholder(),
            alignment=ft.alignment.center,
            expand=True,
        )

        # Page text
        self._page_text = ft.Text(
            value="",
            size=Typography.SIZE_LG,
            color=Colors.TEXT_PRIMARY,
            text_align=ft.TextAlign.CENTER,
        )

        # Progress indicator (for generation)
        self._progress_container = ft.Container(
            content=ft.Column(
                controls=[
                    ft.ProgressRing(
                        width=48,
                        height=48,
                        stroke_width=4,
                        color=Colors.PRIMARY,
                    ),
                    ft.Text(
                        value="Generating illustration...",
                        size=Typography.SIZE_MD,
                        color=Colors.TEXT_SECONDARY,
                    ),
                    ft.ProgressBar(
                        width=200,
                        color=Colors.PRIMARY,
                        bgcolor=Colors.SURFACE_VARIANT,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=Spacing.MD,
            ),
            alignment=ft.alignment.center,
            visible=False,
        )

        # Page navigation
        self._page_strip = ft.Row(
            controls=[],
            spacing=Spacing.XS,
            alignment=ft.MainAxisAlignment.CENTER,
            scroll=ft.ScrollMode.AUTO,
        )

        self._build()

    def _create_placeholder(self) -> ft.Control:
        """Create a placeholder for when no image is available.

        Returns:
            A placeholder control.
        """
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(
                        name=ft.Icons.IMAGE_OUTLINED,
                        size=64,
                        color=Colors.TEXT_DISABLED,
                    ),
                    ft.Text(
                        value="No illustration yet",
                        size=Typography.SIZE_MD,
                        color=Colors.TEXT_DISABLED,
                    ),
                    ft.ElevatedButton(
                        text="Generate Illustration",
                        icon=ft.Icons.AUTO_AWESOME,
                        on_click=lambda _: (
                            self.on_regenerate() if self.on_regenerate else None
                        ),
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=Spacing.MD,
            ),
            width=400,
            height=400,
            bgcolor=Colors.SURFACE_VARIANT,
            border_radius=BorderRadius.LG,
            alignment=ft.alignment.center,
        )

    def _build(self) -> None:
        """Build the preview view layout."""
        # Main preview area
        preview_area = ft.Container(
            content=ft.Column(
                controls=[
                    # Image display
                    ft.Container(
                        content=ft.Stack(
                            controls=[
                                self._image_container,
                                self._progress_container,
                            ],
                        ),
                        expand=True,
                        alignment=ft.alignment.center,
                    ),
                    # Page text
                    ft.Container(
                        content=self._page_text,
                        padding=Spacing.LG,
                        alignment=ft.alignment.center,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                expand=True,
            ),
            bgcolor=Colors.SURFACE,
            border_radius=BorderRadius.LG,
            border=ft.Border.all(1, Colors.BORDER),
            padding=Spacing.LG,
            expand=True,
        )

        # Page navigation strip
        nav_strip = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        value="PAGE NAVIGATION",
                        size=Typography.SIZE_SM,
                        color=Colors.TEXT_SECONDARY,
                        weight=Typography.WEIGHT_MEDIUM,
                    ),
                    ft.Row(
                        controls=[
                            ft.IconButton(
                                icon=ft.Icons.CHEVRON_LEFT,
                                tooltip="Previous Page",
                                on_click=self._handle_prev,
                            ),
                            ft.Container(
                                content=self._page_strip,
                                expand=True,
                            ),
                            ft.IconButton(
                                icon=ft.Icons.CHEVRON_RIGHT,
                                tooltip="Next Page",
                                on_click=self._handle_next,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=Spacing.SM,
            ),
            bgcolor=Colors.SURFACE,
            border_radius=BorderRadius.LG,
            border=ft.Border.all(1, Colors.BORDER),
            padding=Spacing.MD,
        )

        # Action buttons
        actions = ft.Row(
            controls=[
                ft.ElevatedButton(
                    text="Regenerate Image",
                    icon=ft.Icons.REFRESH,
                    on_click=lambda _: (
                        self.on_regenerate() if self.on_regenerate else None
                    ),
                ),
                ft.OutlinedButton(
                    text="Edit Text",
                    icon=ft.Icons.EDIT,
                    on_click=lambda _: self.on_edit() if self.on_edit else None,
                ),
                ft.OutlinedButton(
                    text="Full Screen",
                    icon=ft.Icons.FULLSCREEN,
                    on_click=lambda _: (
                        self.on_fullscreen() if self.on_fullscreen else None
                    ),
                ),
                ft.ElevatedButton(
                    text="Export PDF",
                    icon=ft.Icons.PICTURE_AS_PDF,
                    bgcolor=Colors.SECONDARY,
                    color=Colors.TEXT_ON_PRIMARY,
                    on_click=lambda _: self.on_export() if self.on_export else None,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=Spacing.MD,
        )

        # Main layout
        self.content = ft.Column(
            controls=[
                preview_area,
                nav_strip,
                actions,
            ],
            spacing=Spacing.LG,
            expand=True,
        )

        self.expand = True
        self.padding = Spacing.LG

        # Initialize with empty page strip
        self._update_page_strip()

    def _handle_prev(self, _e: ft.ControlEvent) -> None:
        """Handle previous page button click."""
        if self._current_page > 1:
            self._current_page -= 1
            if self.on_page_change:
                self.on_page_change(self._current_page)
            self._update_page_strip()

    def _handle_next(self, _e: ft.ControlEvent) -> None:
        """Handle next page button click."""
        if self._current_page < self._total_pages:
            self._current_page += 1
            if self.on_page_change:
                self.on_page_change(self._current_page)
            self._update_page_strip()

    def _update_page_strip(self) -> None:
        """Update the page navigation strip."""
        self._page_strip.controls.clear()

        for i in range(1, self._total_pages + 1):
            is_current = i == self._current_page
            page_button = ft.Container(
                content=ft.Text(
                    value=str(i),
                    size=Typography.SIZE_SM,
                    weight=(
                        Typography.WEIGHT_BOLD if is_current else Typography.WEIGHT_NORMAL
                    ),
                    color=Colors.TEXT_ON_PRIMARY if is_current else Colors.TEXT_PRIMARY,
                ),
                width=32,
                height=32,
                bgcolor=Colors.PRIMARY if is_current else Colors.SURFACE,
                border_radius=BorderRadius.SM,
                border=(
                    None
                    if is_current
                    else ft.Border.all(1, Colors.BORDER)
                ),
                alignment=ft.alignment.center,
                on_click=lambda _e, page=i: self._handle_page_click(page),
            )
            self._page_strip.controls.append(page_button)

        if self.page:
            self._page_strip.update()

    def _handle_page_click(self, page: int) -> None:
        """Handle page button click."""
        self._current_page = page
        if self.on_page_change:
            self.on_page_change(page)
        self._update_page_strip()

    def set_page_count(self, total: int, current: int = 1) -> None:
        """Set the total page count and current page.

        Args:
            total: Total number of pages.
            current: Current page number (1-indexed).
        """
        self._total_pages = max(1, total)
        self._current_page = max(1, min(current, total))
        self._update_page_strip()

    def set_page_text(self, text: str) -> None:
        """Set the page text to display.

        Args:
            text: The page text.
        """
        self._page_text.value = text
        if self.page:
            self._page_text.update()

    def set_image(self, image_path: Path | None) -> None:
        """Set the illustration image to display.

        Args:
            image_path: Path to the image file, or None for placeholder.
        """
        if image_path and image_path.exists():
            self._image_container.content = ft.Image(
                src=str(image_path),
                fit=ft.ImageFit.CONTAIN,
                border_radius=BorderRadius.LG,
            )
        else:
            self._image_container.content = self._create_placeholder()

        if self.page:
            self._image_container.update()

    def set_generating(self, is_generating: bool, progress: float = 0.0) -> None:
        """Show or hide the generation progress indicator.

        Args:
            is_generating: Whether generation is in progress.
            progress: Progress value (0.0-1.0).
        """
        self._progress_container.visible = is_generating

        if is_generating:
            # Update progress bar
            progress_bar = self._progress_container.content.controls[2]
            progress_bar.value = progress

        if self.page:
            self._progress_container.update()

    def update_page_statuses(self, _statuses: list[dict[str, bool]]) -> None:
        """Update the status indicators in the page strip.

        Args:
            _statuses: List of dicts with 'has_text' and 'has_image' keys.
        """
        # This would update the visual indicators on each page button
        # For now, just rebuild the strip
        self._update_page_strip()
