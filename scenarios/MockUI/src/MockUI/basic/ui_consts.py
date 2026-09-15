"""UI constants for the new Specter DIY clean interface."""
from micropython import const

from .theming import (
    SpecterColorPalette,
    SpecterFontPalette,
    get_theme_manager,
)

# --- Screen dimensions ---
SCREEN_WIDTH = const(480)
SCREEN_HEIGHT = const(800)

# --- Layout zone heights (pixels) ---
TOP_BAR_HEIGHT = const(56)
SEED_DROPDOWN_HEIGHT = const(52)
NAV_BAR_HEIGHT = const(56)

# Wallet section: fits ~3 wallet rows (bigger rows + more spacing between them)
WALLET_SECTION_HEIGHT = const(260)

# Action buttons fill remaining space
# 800 - 56 - 52 - 260 - 56 = 376px for action area

# --- Button sizes ---
# Sized so Scan + Receive + SD Card always fit the dashboard action area
# without scrolling/clipping (see _DASHBOARD_H in specter_gui.py).
BTN_SMALL_HEIGHT = const(80)        # SD Card
BTN_MED_HEIGHT = const(92)          # Receive (below Scan, a notch smaller)
BTN_LARGE_HEIGHT = const(140)       # Scan button (largest, centered)
BTN_RADIUS = const(16)

# --- Wallet row ---
WALLET_ROW_HEIGHT = const(64)
WALLET_ROW_HEIGHT_ACTIVE = const(78)
WALLET_ICON_SIZE = const(20)

# --- Standard list/nav row (used across settings, seed menu, wallet menu, etc.) ---
ROW_HEIGHT = const(60)
ROW_ICON_ZOOM = const(170)

# --- Bottom nav ---
NAV_BTN_SIZE = const(44)

# --- Font sizes ---
FONT_TITLE = const(22)
FONT_BODY = const(16)
FONT_SMALL = const(12)
FONT_ICON = const(22)

# --- Spacing ---
PAD_XS = const(4)
PAD_SM = const(8)
PAD_MD = const(12)
PAD_LG = const(16)
PAD_XL = const(24)

# --- Icon sizes ---
BTC_ICON_WIDTH = const(42)
BTC_ICON_ZOOM = const(256)
ICON_SM = const(20)
ICON_MD = const(28)
ICON_LG = const(42)

# --- Status bar (legacy compat for Battery stub) ---
STATUS_BTN_HEIGHT = const(40)
STATUS_BTN_WIDTH = const(50)

# --- Modal ---
MODAL_WIDTH_PCT = const(85)
MODAL_HEIGHT_PCT = const(80)

# --- PIN ---
PIN_BTN_HEIGHT = const(85)
PIN_BTN_WIDTH = const(115)

# --- Keyboard manager compat ---
SWITCH_HEIGHT = const(82)
SWITCH_WIDTH = const(45)
BTN_HEIGHT = const(75)
BTN_WIDTH = const(100)
MENU_PCT = const(100)
PAD_SIZE = const(5)
ONE_LETTER_SYMBOL_WIDTH = const(16)
TWO_LETTER_SYMBOL_WIDTH = const(28)
THREE_LETTER_SYMBOL_WIDTH = const(40)
MENU_TITLE_FONT_SIZE = const(22)
MENU_ITEM_FONT_SIZE = const(16)
STATUS_BAR_PCT = const(5)
CONTENT_PCT = const(90)
BACK_BTN_HEIGHT = const(70)
BACK_BTN_WIDTH = const(48)
TITLE_ROW_HEIGHT = const(60)
TITLE_PADDING = const(15)
EXPLAINER_WIDTH_PCT = const(70)
EXPLAINER_HEIGHT_PCT = const(40)
EXPLAINER_OVERLAY_OPA = const(200)

# Semantic palette keys.  Layout code imports these names for readability,
# but resolves them through ThemeManager whenever a widget is constructed.
# This preserves the exact Schnuartz geometry while allowing a JSON theme to
# replace every colour and font after a screen rebuild.
CYAN_HEX = SpecterColorPalette.PRIMARY
CYAN_DARK_HEX = SpecterColorPalette.ACCENT_DARK
BG_BLACK_HEX = SpecterColorPalette.CANVAS
BG_DARK_HEX = SpecterColorPalette.CANVAS
BG_CARD_HEX = SpecterColorPalette.QUATERNARY
BG_ELEVATED_HEX = SpecterColorPalette.SURFACE_SELECTED
WHITE_HEX = SpecterColorPalette.INK
GREY_LIGHT_HEX = SpecterColorPalette.MUTED_TEXT
GREY_HEX = SpecterColorPalette.MUTED
GREY_DARK_HEX = SpecterColorPalette.DIVIDER
GREEN_HEX = SpecterColorPalette.SUCCESS
ORANGE_HEX = SpecterColorPalette.WARNING
RED_HEX = SpecterColorPalette.DANGER
YELLOW_HEX = SpecterColorPalette.WARNING
BLACK_HEX = SpecterColorPalette.PURE_BLACK
BG_WARN_HEX = SpecterColorPalette.WARNING_SURFACE


def theme_color(palette_key):
    """Resolve a colour from the active JSON theme."""
    value, _error = get_theme_manager().get_color(palette_key)
    return value


def theme_font(palette_key):
    """Resolve a font from the active JSON theme."""
    value, _error = get_theme_manager().get_font(palette_key)
    return value


FONT_TITLE_THEME = SpecterFontPalette.TITLE
FONT_TEXT_THEME = SpecterFontPalette.TEXT
FONT_SMALL_THEME = SpecterFontPalette.SMALL
FONT_CAPTION_THEME = SpecterFontPalette.CAPTION
