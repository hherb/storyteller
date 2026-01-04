"""Theme and styling constants for the Storyteller GUI.

This module defines colors, typography, and other visual constants
used throughout the application for a consistent look and feel.
"""

from __future__ import annotations

import flet as ft

# =============================================================================
# Color Palette
# =============================================================================

class Colors:
    """Application color palette.

    A warm, child-friendly color scheme suitable for a storybook application.
    """

    # Primary colors
    PRIMARY = "#6366F1"  # Indigo - main brand color
    PRIMARY_LIGHT = "#818CF8"
    PRIMARY_DARK = "#4F46E5"

    # Secondary colors
    SECONDARY = "#F59E0B"  # Amber - accent color
    SECONDARY_LIGHT = "#FBBF24"
    SECONDARY_DARK = "#D97706"

    # Background colors
    BACKGROUND = "#FAFAFA"
    SURFACE = "#FFFFFF"
    SURFACE_VARIANT = "#F5F5F5"

    # Text colors
    TEXT_PRIMARY = "#1F2937"
    TEXT_SECONDARY = "#6B7280"
    TEXT_DISABLED = "#9CA3AF"
    TEXT_ON_PRIMARY = "#FFFFFF"

    # Status colors
    SUCCESS = "#10B981"
    WARNING = "#F59E0B"
    ERROR = "#EF4444"
    INFO = "#3B82F6"

    # Message bubble colors
    BUBBLE_USER = "#E0E7FF"  # Light indigo
    BUBBLE_ASSISTANT = "#F3F4F6"  # Light gray

    # Border colors
    BORDER = "#E5E7EB"
    BORDER_FOCUS = "#6366F1"


# =============================================================================
# Typography
# =============================================================================

class Typography:
    """Typography constants for consistent text styling."""

    # Font families
    FONT_FAMILY = "Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif"
    FONT_FAMILY_MONO = "Consolas, Monaco, Courier New, monospace"

    # Font sizes
    SIZE_XS = 12
    SIZE_SM = 14
    SIZE_MD = 16
    SIZE_LG = 18
    SIZE_XL = 24
    SIZE_2XL = 32

    # Font weights
    WEIGHT_NORMAL = ft.FontWeight.NORMAL
    WEIGHT_MEDIUM = ft.FontWeight.W_500
    WEIGHT_BOLD = ft.FontWeight.BOLD


# =============================================================================
# Spacing
# =============================================================================

class Spacing:
    """Spacing constants for consistent layout."""

    XS = 4
    SM = 8
    MD = 16
    LG = 24
    XL = 32
    XXL = 48


# =============================================================================
# Border Radius
# =============================================================================

class BorderRadius:
    """Border radius constants for rounded corners."""

    SM = 4
    MD = 8
    LG = 12
    XL = 16
    FULL = 9999  # For pill shapes


# =============================================================================
# Shadows
# =============================================================================

class Shadows:
    """Shadow definitions for elevation effects."""

    SM = ft.BoxShadow(
        spread_radius=0,
        blur_radius=4,
        color="#1A000000",  # Black with 10% opacity
        offset=ft.Offset(0, 1),
    )

    MD = ft.BoxShadow(
        spread_radius=0,
        blur_radius=8,
        color="#26000000",  # Black with 15% opacity
        offset=ft.Offset(0, 2),
    )

    LG = ft.BoxShadow(
        spread_radius=0,
        blur_radius=16,
        color="#33000000",  # Black with 20% opacity
        offset=ft.Offset(0, 4),
    )


# =============================================================================
# Component Dimensions
# =============================================================================

class Dimensions:
    """Standard dimensions for UI components."""

    # App bar
    APP_BAR_HEIGHT = 64

    # Status bar
    STATUS_BAR_HEIGHT = 32

    # Side panel
    SIDE_PANEL_WIDTH = 250

    # Input heights
    INPUT_HEIGHT = 40
    INPUT_HEIGHT_LARGE = 48

    # Button sizes
    BUTTON_HEIGHT = 36
    BUTTON_HEIGHT_LARGE = 44

    # Icon sizes
    ICON_SM = 16
    ICON_MD = 20
    ICON_LG = 24

    # Thumbnail sizes
    THUMBNAIL_SIZE = 60

    # Card dimensions
    CARD_MIN_WIDTH = 300


# =============================================================================
# Theme Configuration
# =============================================================================

def create_theme() -> ft.Theme:
    """Create the application theme.

    Returns:
        A configured Flet theme for the application.
    """
    return ft.Theme(
        color_scheme_seed=Colors.PRIMARY,
        font_family=Typography.FONT_FAMILY,
        visual_density=ft.VisualDensity.COMFORTABLE,
    )


def apply_theme(page: ft.Page) -> None:
    """Apply the application theme to a page.

    Args:
        page: The Flet page to apply the theme to.
    """
    page.theme = create_theme()
    page.bgcolor = Colors.BACKGROUND
    page.padding = 0


# =============================================================================
# Style Helpers
# =============================================================================

def card_style() -> dict[str, object]:
    """Get standard card styling.

    Returns:
        Dictionary of style properties for cards.
    """
    return {
        "bgcolor": Colors.SURFACE,
        "border_radius": BorderRadius.LG,
        "padding": Spacing.MD,
    }


def input_style() -> dict[str, object]:
    """Get standard text input styling.

    Returns:
        Dictionary of style properties for text inputs.
    """
    return {
        "border_radius": BorderRadius.MD,
        "border_color": Colors.BORDER,
        "focused_border_color": Colors.BORDER_FOCUS,
        "text_size": Typography.SIZE_MD,
    }


def button_style_primary() -> ft.ButtonStyle:
    """Get primary button styling.

    Returns:
        ButtonStyle for primary action buttons.
    """
    return ft.ButtonStyle(
        color=Colors.TEXT_ON_PRIMARY,
        bgcolor=Colors.PRIMARY,
        padding=ft.Padding(Spacing.MD, Spacing.SM, Spacing.MD, Spacing.SM),
        shape=ft.RoundedRectangleBorder(radius=BorderRadius.MD),
    )


def button_style_secondary() -> ft.ButtonStyle:
    """Get secondary button styling.

    Returns:
        ButtonStyle for secondary action buttons.
    """
    return ft.ButtonStyle(
        color=Colors.PRIMARY,
        bgcolor=Colors.SURFACE,
        padding=ft.Padding(Spacing.MD, Spacing.SM, Spacing.MD, Spacing.SM),
        shape=ft.RoundedRectangleBorder(radius=BorderRadius.MD),
        side=ft.BorderSide(1, Colors.PRIMARY),
    )
