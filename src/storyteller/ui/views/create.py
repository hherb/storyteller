"""Create Story view for the Storyteller GUI.

This module provides the main story creation interface with
AI conversation, page navigation, and content editing.
"""

from __future__ import annotations

from collections.abc import Callable

import flet as ft

from storyteller.ui.state import ConversationMessage
from storyteller.ui.theme import (
    BorderRadius,
    Colors,
    Dimensions,
    Spacing,
    Typography,
)


def _create_message_bubble(message: ConversationMessage) -> ft.Container:
    """Create a styled message bubble for the conversation.

    Args:
        message: The conversation message to display.

    Returns:
        A styled container with the message content.
    """
    is_user = message.role == "user"

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Icon(
                            ft.Icons.PERSON if is_user else ft.Icons.SMART_TOY,
                            size=Dimensions.ICON_SM,
                            color=Colors.PRIMARY if is_user else Colors.TEXT_SECONDARY,
                        ),
                        ft.Text(
                            value="You" if is_user else "Storyteller",
                            size=Typography.SIZE_SM,
                            weight=Typography.WEIGHT_MEDIUM,
                            color=Colors.PRIMARY if is_user else Colors.TEXT_SECONDARY,
                        ),
                    ],
                    spacing=Spacing.XS,
                ),
                ft.Text(
                    value=message.content,
                    size=Typography.SIZE_MD,
                    color=Colors.TEXT_PRIMARY,
                    selectable=True,
                ),
            ],
            spacing=Spacing.XS,
        ),
        bgcolor=Colors.BUBBLE_USER if is_user else Colors.BUBBLE_ASSISTANT,
        border_radius=BorderRadius.LG,
        padding=Spacing.MD,
        margin=ft.Margin(
            left=Spacing.XL if is_user else 0,
            right=0 if is_user else Spacing.XL,
            top=Spacing.XS,
            bottom=Spacing.XS,
        ),
    )


class CreateView(ft.Container):
    """Create Story tab content.

    Provides the main story creation interface with:
    - Conversation panel for AI interaction
    - Side panel with page and character lists
    - Current page editor
    - Input area with action buttons
    """

    def __init__(
        self,
        on_send: Callable[[str], None] | None = None,
        on_generate_page: Callable[[], None] | None = None,
        on_generate_image: Callable[[], None] | None = None,
        on_add_character: Callable[[], None] | None = None,
        on_page_select: Callable[[int], None] | None = None,
    ) -> None:
        """Initialize the create view.

        Args:
            on_send: Callback when user sends a message.
            on_generate_page: Callback to generate page text.
            on_generate_image: Callback to generate illustration.
            on_add_character: Callback to add a character.
            on_page_select: Callback when a page is selected.
        """
        super().__init__()

        self.on_send = on_send
        self.on_generate_page = on_generate_page
        self.on_generate_image = on_generate_image
        self.on_add_character = on_add_character
        self.on_page_select = on_page_select

        # Conversation components
        self._message_list = ft.ListView(
            spacing=Spacing.SM,
            padding=Spacing.MD,
            auto_scroll=True,
            expand=True,
        )

        self._typing_indicator = ft.Row(
            controls=[
                ft.ProgressRing(
                    width=Dimensions.ICON_SM,
                    height=Dimensions.ICON_SM,
                    stroke_width=2,
                ),
                ft.Text(
                    value="Thinking...",
                    size=Typography.SIZE_SM,
                    color=Colors.TEXT_SECONDARY,
                    italic=True,
                ),
            ],
            spacing=Spacing.SM,
            visible=False,
        )

        # Page list
        self._page_list = ft.ListView(
            spacing=Spacing.XS,
            padding=Spacing.SM,
            expand=True,
        )

        # Character list
        self._character_list = ft.ListView(
            spacing=Spacing.XS,
            padding=Spacing.SM,
            height=150,
        )

        # Current page editor
        self._page_text_field = ft.TextField(
            label="Page Text",
            multiline=True,
            min_lines=2,
            max_lines=4,
            border_radius=BorderRadius.MD,
            read_only=True,
        )

        self._prompt_field = ft.TextField(
            label="Illustration Prompt",
            multiline=True,
            min_lines=2,
            max_lines=3,
            border_radius=BorderRadius.MD,
            read_only=True,
        )

        # Input area
        self._input_field = ft.TextField(
            hint_text="Type your message...",
            multiline=True,
            min_lines=2,
            max_lines=4,
            border_radius=BorderRadius.MD,
            expand=True,
            on_submit=self._handle_send,
        )

        self._build()

    def _build(self) -> None:
        """Build the create view layout."""
        # Conversation panel
        conversation_panel = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Container(
                        content=self._message_list,
                        expand=True,
                        border=ft.Border.all(1, Colors.BORDER),
                        border_radius=BorderRadius.MD,
                        bgcolor=Colors.SURFACE,
                    ),
                    self._typing_indicator,
                ],
                expand=True,
            ),
            expand=3,
        )

        # Side panel with pages and characters
        side_panel = ft.Container(
            content=ft.Column(
                controls=[
                    # Pages section
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Row(
                                    controls=[
                                        ft.Text(
                                            value="PAGES",
                                            size=Typography.SIZE_SM,
                                            weight=Typography.WEIGHT_MEDIUM,
                                            color=Colors.TEXT_SECONDARY,
                                        ),
                                    ],
                                ),
                                ft.Container(
                                    content=self._page_list,
                                    expand=True,
                                    border=ft.Border.all(1, Colors.BORDER),
                                    border_radius=BorderRadius.MD,
                                    bgcolor=Colors.SURFACE,
                                ),
                                ft.TextButton(
                                    content=ft.Text("+ Add Page"),
                                    icon=ft.Icons.ADD,
                                    on_click=self._handle_add_page,
                                ),
                            ],
                            spacing=Spacing.XS,
                            expand=True,
                        ),
                        expand=True,
                    ),
                    # Characters section
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Row(
                                    controls=[
                                        ft.Text(
                                            value="CHARACTERS",
                                            size=Typography.SIZE_SM,
                                            weight=Typography.WEIGHT_MEDIUM,
                                            color=Colors.TEXT_SECONDARY,
                                        ),
                                    ],
                                ),
                                ft.Container(
                                    content=self._character_list,
                                    border=ft.Border.all(1, Colors.BORDER),
                                    border_radius=BorderRadius.MD,
                                    bgcolor=Colors.SURFACE,
                                ),
                                ft.TextButton(
                                    content=ft.Text("+ Add Character"),
                                    icon=ft.Icons.PERSON_ADD,
                                    on_click=lambda _: (
                                        self.on_add_character()
                                        if self.on_add_character
                                        else None
                                    ),
                                ),
                            ],
                            spacing=Spacing.XS,
                        ),
                    ),
                ],
                spacing=Spacing.MD,
            ),
            width=Dimensions.SIDE_PANEL_WIDTH,
            padding=Spacing.SM,
        )

        # Current page panel
        page_panel = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text(
                                value="CURRENT PAGE",
                                size=Typography.SIZE_SM,
                                weight=Typography.WEIGHT_MEDIUM,
                                color=Colors.TEXT_SECONDARY,
                            ),
                            ft.Container(expand=True),
                            ft.IconButton(
                                icon=ft.Icons.EDIT,
                                tooltip="Edit",
                                icon_size=Dimensions.ICON_SM,
                            ),
                        ],
                    ),
                    self._page_text_field,
                    self._prompt_field,
                ],
                spacing=Spacing.SM,
            ),
            bgcolor=Colors.SURFACE_VARIANT,
            border_radius=BorderRadius.MD,
            padding=Spacing.MD,
        )

        # Input area
        input_area = ft.Container(
            content=ft.Column(
                controls=[
                    self._input_field,
                    ft.Row(
                        controls=[
                            ft.ElevatedButton(
                                content=ft.Text("Send"),
                                icon=ft.Icons.SEND,
                                on_click=self._handle_send,
                                bgcolor=Colors.PRIMARY,
                                color=Colors.TEXT_ON_PRIMARY,
                            ),
                            ft.OutlinedButton(
                                content=ft.Text("Generate Page Text"),
                                icon=ft.Icons.AUTO_AWESOME,
                                on_click=lambda _: (
                                    self.on_generate_page()
                                    if self.on_generate_page
                                    else None
                                ),
                            ),
                            ft.OutlinedButton(
                                content=ft.Text("Generate Illustration"),
                                icon=ft.Icons.IMAGE,
                                on_click=lambda _: (
                                    self.on_generate_image()
                                    if self.on_generate_image
                                    else None
                                ),
                            ),
                            ft.OutlinedButton(
                                content=ft.Text("Ideas"),
                                icon=ft.Icons.LIGHTBULB_OUTLINE,
                            ),
                        ],
                        spacing=Spacing.SM,
                    ),
                ],
                spacing=Spacing.SM,
            ),
            padding=Spacing.MD,
            bgcolor=Colors.SURFACE,
            border=ft.Border(top=ft.BorderSide(1, Colors.BORDER)),
        )

        # Main layout
        self.content = ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        conversation_panel,
                        ft.VerticalDivider(width=1, color=Colors.BORDER),
                        side_panel,
                    ],
                    expand=True,
                ),
                page_panel,
                input_area,
            ],
            spacing=0,
            expand=True,
        )

        self.expand = True
        self.padding = 0

        # Add welcome message
        self._add_welcome_message()

    def _add_welcome_message(self) -> None:
        """Add the initial welcome message."""
        welcome = ConversationMessage(
            role="assistant",
            content=(
                "Welcome to Storyteller! I'm here to help you create a wonderful "
                "children's story.\n\n"
                "What would you like your story to be about? Tell me about the "
                "characters, setting, or theme you have in mind."
            ),
        )
        self._message_list.controls.append(_create_message_bubble(welcome))

    def _handle_send(self, _e: ft.ControlEvent | None = None) -> None:
        """Handle sending a message."""
        text = self._input_field.value
        if text and text.strip():
            # Add user message to conversation
            user_msg = ConversationMessage(role="user", content=text.strip())
            self._message_list.controls.append(_create_message_bubble(user_msg))
            self._input_field.value = ""

            if self.page:
                self._message_list.update()
                self._input_field.update()

            # Call the send callback
            if self.on_send:
                self.on_send(text.strip())

    def _handle_add_page(self, _e: ft.ControlEvent) -> None:
        """Handle adding a new page."""
        # This will be connected to the state manager
        pass

    def add_assistant_message(self, content: str) -> None:
        """Add an assistant message to the conversation.

        Args:
            content: The message content.
        """
        msg = ConversationMessage(role="assistant", content=content)
        self._message_list.controls.append(_create_message_bubble(msg))
        if self.page:
            self._message_list.update()

    def set_typing(self, is_typing: bool) -> None:
        """Show or hide the typing indicator.

        Args:
            is_typing: Whether the assistant is typing.
        """
        self._typing_indicator.visible = is_typing
        if self.page:
            self._typing_indicator.update()

    def update_page_list(
        self,
        pages: list[dict],
        current_page: int,
    ) -> None:
        """Update the page list display.

        Args:
            pages: List of page data dicts with 'number', 'has_text', 'has_image'.
            current_page: Currently selected page number.
        """
        self._page_list.controls.clear()

        for page_data in pages:
            page_num = page_data["number"]
            has_text = page_data.get("has_text", False)
            has_image = page_data.get("has_image", False)

            # Determine status icon
            if has_text and has_image:
                status_icon = ft.Icons.CHECK_CIRCLE
                status_color = Colors.SUCCESS
            elif has_text:
                status_icon = ft.Icons.CIRCLE
                status_color = Colors.WARNING
            else:
                status_icon = ft.Icons.CIRCLE_OUTLINED
                status_color = Colors.TEXT_DISABLED

            is_current = page_num == current_page

            page_item = ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Text(
                            value=f"[{page_num}]",
                            size=Typography.SIZE_SM,
                            weight=(
                                Typography.WEIGHT_BOLD
                                if is_current
                                else Typography.WEIGHT_NORMAL
                            ),
                            color=(
                                Colors.PRIMARY if is_current else Colors.TEXT_PRIMARY
                            ),
                        ),
                        ft.Icon(
                            status_icon,
                            size=Dimensions.ICON_SM,
                            color=status_color,
                        ),
                    ],
                    spacing=Spacing.SM,
                ),
                bgcolor=Colors.PRIMARY_LIGHT if is_current else None,
                border_radius=BorderRadius.SM,
                padding=Spacing.XS,
                on_click=lambda _e, n=page_num: self._handle_page_click(n),
            )
            self._page_list.controls.append(page_item)

        if self.page:
            self._page_list.update()

    def _handle_page_click(self, page_number: int) -> None:
        """Handle page selection."""
        if self.on_page_select:
            self.on_page_select(page_number)

    def update_character_list(self, characters: list[dict]) -> None:
        """Update the character list display.

        Args:
            characters: List of character data dicts with 'name' and 'description'.
        """
        self._character_list.controls.clear()

        for char in characters:
            char_item = ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Icon(
                            ft.Icons.PERSON,
                            size=Dimensions.ICON_SM,
                            color=Colors.PRIMARY,
                        ),
                        ft.Text(
                            value=char["name"],
                            size=Typography.SIZE_SM,
                            color=Colors.TEXT_PRIMARY,
                        ),
                    ],
                    spacing=Spacing.SM,
                ),
                padding=Spacing.XS,
            )
            self._character_list.controls.append(char_item)

        if self.page:
            self._character_list.update()

    def update_current_page(self, text: str, prompt: str) -> None:
        """Update the current page content display.

        Args:
            text: The page text.
            prompt: The illustration prompt.
        """
        self._page_text_field.value = text
        self._prompt_field.value = prompt
        if self.page:
            self._page_text_field.update()
            self._prompt_field.update()
