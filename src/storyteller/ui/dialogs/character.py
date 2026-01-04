"""Character definition dialog for the Storyteller GUI.

This module provides the dialog for defining story characters
with visual traits for illustration consistency.
"""

from __future__ import annotations

from collections.abc import Callable

import flet as ft

from storyteller.ui.theme import BorderRadius, Colors, Spacing, Typography


class CharacterDialog(ft.AlertDialog):
    """Dialog for defining a story character.

    Collects character name, description, and visual traits
    that will be used for consistent illustration generation.
    """

    def __init__(
        self,
        on_save: Callable[[dict], None] | None = None,
        on_extract_traits: Callable[[str, str], list[str]] | None = None,
    ) -> None:
        """Initialize the character dialog.

        Args:
            on_save: Callback when character is saved, receives character dict.
            on_extract_traits: Optional callback to extract visual traits from
                description using AI. Receives (name, description), returns traits.
        """
        super().__init__()

        self.on_save_callback = on_save
        self.on_extract_traits = on_extract_traits

        # Form fields
        self._name_field = ft.TextField(
            label="Character Name",
            hint_text="e.g., Luna, Mr. Fox, Captain Whiskers",
            border_radius=BorderRadius.MD,
            autofocus=True,
        )

        self._description_field = ft.TextField(
            label="Description (who are they? what are they like?)",
            hint_text="Describe the character's personality and appearance...",
            multiline=True,
            min_lines=3,
            max_lines=5,
            border_radius=BorderRadius.MD,
        )

        self._extract_button = ft.TextButton(
            content=ft.Text("Extract Visual Traits with AI"),
            icon=ft.Icons.AUTO_AWESOME,
            on_click=self._handle_extract,
        )

        # Visual traits as editable chips
        self._traits_container = ft.Column(
            controls=[],
            spacing=Spacing.XS,
        )

        self._add_trait_field = ft.TextField(
            hint_text="Add a visual trait...",
            border_radius=BorderRadius.MD,
            expand=True,
            on_submit=self._handle_add_trait,
        )

        self._traits: list[str] = []

        self._build()

    def _build(self) -> None:
        """Build the dialog content."""
        self.modal = True
        self.title = ft.Text(
            value="Define Character",
            size=Typography.SIZE_XL,
            weight=Typography.WEIGHT_BOLD,
        )

        # Traits section with explanation
        traits_section = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        value="Visual Traits (for consistent illustrations)",
                        size=Typography.SIZE_SM,
                        weight=Typography.WEIGHT_MEDIUM,
                        color=Colors.TEXT_SECONDARY,
                    ),
                    ft.Text(
                        value=(
                            "Add 3-5 visual details that should appear in every "
                            "illustration of this character."
                        ),
                        size=Typography.SIZE_SM,
                        color=Colors.TEXT_SECONDARY,
                        italic=True,
                    ),
                    self._extract_button,
                    ft.Container(
                        content=self._traits_container,
                        bgcolor=Colors.SURFACE_VARIANT,
                        border_radius=BorderRadius.MD,
                        padding=Spacing.SM,
                        border=ft.Border.all(1, Colors.BORDER),
                    ),
                    ft.Row(
                        controls=[
                            self._add_trait_field,
                            ft.IconButton(
                                icon=ft.Icons.ADD,
                                tooltip="Add trait",
                                on_click=self._handle_add_trait,
                            ),
                        ],
                        spacing=Spacing.XS,
                    ),
                ],
                spacing=Spacing.SM,
            ),
        )

        self.content = ft.Container(
            content=ft.Column(
                controls=[
                    self._name_field,
                    self._description_field,
                    traits_section,
                ],
                spacing=Spacing.MD,
                tight=True,
            ),
            width=500,
            padding=Spacing.MD,
        )

        self.actions = [
            ft.TextButton(
                content=ft.Text("Cancel"),
                on_click=self._handle_cancel,
            ),
            ft.ElevatedButton(
                content=ft.Text("Save Character"),
                icon=ft.Icons.SAVE,
                bgcolor=Colors.PRIMARY,
                color=Colors.TEXT_ON_PRIMARY,
                on_click=self._handle_save,
            ),
        ]

        self.actions_alignment = ft.MainAxisAlignment.END

    def _handle_cancel(self, _e: ft.ControlEvent) -> None:
        """Handle cancel button click."""
        self.open = False
        if self.page:
            self.page.update()

    def _handle_save(self, _e: ft.ControlEvent) -> None:
        """Handle save button click."""
        # Validate required fields
        name = self._name_field.value
        if not name or not name.strip():
            self._name_field.error_text = "Please enter a name"
            if self.page:
                self._name_field.update()
            return

        description = self._description_field.value or ""

        # Collect character data
        character_data = {
            "name": name.strip(),
            "description": description.strip(),
            "visual_traits": self._traits.copy(),
        }

        # Close dialog
        self.open = False
        if self.page:
            self.page.update()

        # Call callback
        if self.on_save_callback:
            self.on_save_callback(character_data)

    def _handle_extract(self, _e: ft.ControlEvent) -> None:
        """Handle extract traits button click."""
        name = self._name_field.value or ""
        description = self._description_field.value or ""

        if not description.strip():
            self._description_field.error_text = "Please add a description first"
            if self.page:
                self._description_field.update()
            return

        self._description_field.error_text = None

        if self.on_extract_traits:
            # Call the AI extraction callback
            try:
                traits = self.on_extract_traits(name, description)
                if traits:
                    self._traits = traits
                    self._update_traits_display()
            except Exception:
                # Silently fail - the user can still add traits manually
                pass
        else:
            # Fallback: simple extraction from description
            self._extract_traits_simple(description)

    def _extract_traits_simple(self, description: str) -> None:
        """Simple trait extraction without AI.

        Extracts basic visual keywords from the description.

        Args:
            description: The character description text.
        """
        # Look for common visual descriptors
        words = description.lower().split()

        # Color words
        colors = {"red", "blue", "green", "yellow", "brown", "black", "white",
                  "pink", "purple", "orange", "gray", "grey", "golden"}

        # Size words
        sizes = {"small", "tiny", "little", "big", "large", "tall", "short"}

        # Animal words
        animals = {"mouse", "cat", "dog", "bear", "rabbit", "fox", "owl",
                   "bird", "bunny", "squirrel", "dragon", "unicorn"}

        found_traits = []

        for i, word in enumerate(words):
            # Check for color + noun combinations
            if word in colors and i + 1 < len(words):
                next_word = words[i + 1].strip(",.!?")
                found_traits.append(f"{word} {next_word}")
            elif word in sizes and i + 1 < len(words):
                next_word = words[i + 1].strip(",.!?")
                found_traits.append(f"{word} {next_word}")
            elif word in animals:
                found_traits.append(word)

        # Add any found traits
        for trait in found_traits[:5]:  # Limit to 5 traits
            if trait not in self._traits:
                self._traits.append(trait)

        self._update_traits_display()

    def _handle_add_trait(self, _e: ft.ControlEvent) -> None:
        """Handle adding a new trait."""
        trait = self._add_trait_field.value
        if trait and trait.strip():
            trait = trait.strip()
            if trait not in self._traits:
                self._traits.append(trait)
                self._add_trait_field.value = ""
                self._update_traits_display()
                if self.page:
                    self._add_trait_field.update()

    def _handle_remove_trait(self, trait: str) -> None:
        """Handle removing a trait.

        Args:
            trait: The trait to remove.
        """
        if trait in self._traits:
            self._traits.remove(trait)
            self._update_traits_display()

    def _update_traits_display(self) -> None:
        """Update the visual traits display."""
        self._traits_container.controls.clear()

        if not self._traits:
            self._traits_container.controls.append(
                ft.Text(
                    value="No traits defined yet",
                    size=Typography.SIZE_SM,
                    color=Colors.TEXT_DISABLED,
                    italic=True,
                )
            )
        else:
            # Create a row of chips
            chips_row = ft.Row(
                controls=[],
                wrap=True,
                spacing=Spacing.XS,
            )
            for trait in self._traits:
                chip = ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Text(
                                value=trait,
                                size=Typography.SIZE_SM,
                                color=Colors.TEXT_PRIMARY,
                            ),
                            ft.IconButton(
                                icon=ft.Icons.CLOSE,
                                icon_size=14,
                                tooltip="Remove",
                                on_click=lambda _e, t=trait: self._handle_remove_trait(t),
                            ),
                        ],
                        spacing=Spacing.XS,
                        tight=True,
                    ),
                    bgcolor=Colors.PRIMARY_LIGHT,
                    border_radius=BorderRadius.SM,
                    padding=ft.Padding(left=Spacing.SM, right=2, top=2, bottom=2),
                )
                chips_row.controls.append(chip)

            self._traits_container.controls.append(chips_row)

        if self.page:
            self._traits_container.update()

    def reset(self) -> None:
        """Reset all fields to defaults."""
        self._name_field.value = ""
        self._name_field.error_text = None
        self._description_field.value = ""
        self._description_field.error_text = None
        self._add_trait_field.value = ""
        self._traits = []
        self._update_traits_display()

    def set_character(
        self,
        name: str,
        description: str,
        visual_traits: list[str],
    ) -> None:
        """Set the dialog to edit an existing character.

        Args:
            name: Character name.
            description: Character description.
            visual_traits: List of visual traits.
        """
        self._name_field.value = name
        self._description_field.value = description
        self._traits = list(visual_traits)
        self._update_traits_display()
