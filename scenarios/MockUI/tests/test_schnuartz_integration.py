"""Structural guarantees for the Schnuartz UI integration."""

import json
from pathlib import Path

from MockUI.basic.theming.theme_schema import (
    SpecterColorPalette,
    SpecterFontPalette,
)
from MockUI.screens import get_screen_class, get_view_factory


ROOT = Path(__file__).parents[1] / "src" / "MockUI"
THEMES = ROOT / "basic" / "theming" / "themes"


SCREEN_IDS = (
    "locked", "seed_management", "seed_detail", "generate_seed",
    "set_passphrase", "show_seed_words", "enter_seed_words",
    "wallet_info", "wallet_menu", "wallet_details", "add_wallet",
    "rename_wallet", "connect_app", "export", "receive", "address_qr",
    "scan", "sd_card", "signing", "settings", "security_settings",
    "interfaces", "language_settings", "theme_settings", "import_language",
    "import_theme", "wipe_device", "xpub_export", "firmware_info",
)


def _constant_names(cls):
    return {
        name for name in dir(cls)
        if name.isupper() and isinstance(getattr(cls, name), int)
    }


def test_every_reference_screen_has_a_lazy_factory():
    for screen_id in SCREEN_IDS:
        assert get_screen_class(screen_id) is not None, screen_id
        assert callable(get_view_factory(screen_id))


def test_every_theme_implements_the_extended_palette():
    expected_colors = _constant_names(SpecterColorPalette)
    expected_fonts = _constant_names(SpecterFontPalette)
    for path in THEMES.glob("specter_ui_theme_*.json"):
        data = json.loads(path.read_text(encoding="utf-8"))
        assert {name.upper() for name in data["colors"]} == expected_colors, path.name
        assert {name.upper() for name in data["fonts"]} == expected_fonts, path.name


def test_reference_theme_keeps_schnuartz_geometry_and_colors():
    path = THEMES / "specter_ui_theme_specter.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["colors"]["PRIMARY"] == "#1F99E5"
    assert data["colors"]["CANVAS"] == "#081A2A"
    assert data["colors"]["QUATERNARY"] == "#24384C"
    assert data["styles"]["CONTAINER.NAVBAR"]["height"] == 56
