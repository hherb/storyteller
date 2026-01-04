"""Application bar component for the Storyteller GUI.

This module provides the top application bar with branding,
project title, and quick action buttons.
"""

from __future__ import annotations

from collections.abc import Callable

import flet as ft

from storyteller.ui.theme import Colors, Dimensions, Spacing, Typography


class StorytellerAppBar(ft.Container):
    """Top application bar with branding and actions.

    Displays the app logo, current project title, and quick action
    buttons for common operations like New, Open, and Save.

    Attributes:
        on_new: Callback when New button is clicked.
        on_open: Callback when Open button is clicked.
        on_save: Callback when Save button is clicked.
        on_export: Callback when Export button is clicked.
    """

    def __init__(
        self,
        on_new: Callable[[], None] | None = None,
        on_open: Callable[[], None] | None = None,
        on_save: Callable[[], None] | None = None,
        on_export: Callable[[], None] | None = None,
    ) -> None:
        """Initialize the application bar.

        Args:
            on_new: Callback for New button click.
            on_open: Callback for Open button click.
            on_save: Callback for Save button click.
            on_export: Callback for Export button click.
        """
        super().__init__()

        self.on_new = on_new
        self.on_open = on_open
        self.on_save = on_save
        self.on_export = on_export

        self._project_title = ft.Text(
            value="Untitled Story",
            size=Typography.SIZE_MD,
            color=Colors.TEXT_SECONDARY,
            italic=True,
        )

        self._build()

    def _build(self) -> None:
        """Build the app bar layout."""
        # Logo and branding
        logo = ft.Row(
            controls=[
                ft.Icon(
                    name=ft.Icons.AUTO_STORIES,
                    color=Colors.PRIMARY,
                    size=Dimensions.ICON_LG,
                ),
                ft.Text(
                    value="Storyteller",
                    size=Typography.SIZE_XL,
                    weight=Typography.WEIGHT_BOLD,
                    color=Colors.TEXT_PRIMARY,
                ),
            ],
            spacing=Spacing.SM,
        )

        # Action buttons
        actions = ft.Row(
            controls=[
                ft.IconButton(
                    icon=ft.Icons.ADD,
                    tooltip="New Story",
                    icon_color=Colors.TEXT_SECONDARY,
                    on_click=lambda _: self.on_new() if self.on_new else None,
                ),
                ft.IconButton(
                    icon=ft.Icons.FOLDER_OPEN,
                    tooltip="Open Story",
                    icon_color=Colors.TEXT_SECONDARY,
                    on_click=lambda _: self.on_open() if self.on_open else None,
                ),
                ft.IconButton(
                    icon=ft.Icons.SAVE,
                    tooltip="Save Story",
                    icon_color=Colors.TEXT_SECONDARY,
                    on_click=lambda _: self.on_save() if self.on_save else None,
                ),
                ft.VerticalDivider(width=1, color=Colors.BORDER),
                ft.IconButton(
                    icon=ft.Icons.PICTURE_AS_PDF,
                    tooltip="Export to PDF",
                    icon_color=Colors.TEXT_SECONDARY,
                    on_click=lambda _: self.on_export() if self.on_export else None,
                ),
            ],
            spacing=Spacing.XS,
        )

        # Main layout
        self.content = ft.Row(
            controls=[
                logo,
                self._project_title,
                ft.Container(expand=True),  # Spacer
                actions,
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        self.bgcolor = Colors.SURFACE
        self.height = Dimensions.APP_BAR_HEIGHT
        self.padding = ft.Padding(Spacing.LG, Spacing.MD, Spacing.LG, Spacing.MD)
        self.border = ft.Border(
            bottom=ft.BorderSide(1, Colors.BORDER),
        )

    def update_title(self, title: str | None, is_modified: bool = False) -> None:
        """Update the displayed project title.

        Args:
            title: The project title to display, or None for default.
            is_modified: Whether the project has unsaved changes.
        """
        if title:
            display_title = f"{title}{'*' if is_modified else ''}"
            self._project_title.value = display_title
            self._project_title.italic = False
            self._project_title.color = Colors.TEXT_PRIMARY
        else:
            self._project_title.value = "Untitled Story"
            self._project_title.italic = True
            self._project_title.color = Colors.TEXT_SECONDARY

        if self.page:
            self._project_title.update()
