"""Install language and theme JSON files from the mounted SD card."""

import os
import lvgl as lv

from ..basic.symbol_lib import BTC_ICONS
from ..basic.ui_consts import (
    ROW_HEIGHT, ROW_ICON_ZOOM, PAD_MD, PAD_SM,
    BG_BLACK_HEX, BG_CARD_HEX, WHITE_HEX, GREY_LIGHT_HEX,
    CYAN_HEX, RED_HEX,
    theme_color, theme_font, FONT_TITLE_THEME, FONT_TEXT_THEME,
    FONT_SMALL_THEME,
)


class SettingsImportScreen(lv.obj):
    kind = None
    prefix = None
    return_screen = None

    def __init__(self, gui, parent):
        super().__init__(parent)
        self.gui = gui
        self.set_size(lv.pct(100), lv.pct(100))
        self.set_style_bg_color(theme_color(BG_BLACK_HEX), 0)
        self.set_style_bg_opa(lv.OPA.COVER, 0)
        self.set_style_border_width(0, 0)
        self.set_style_radius(0, 0)
        self.set_style_pad_all(PAD_MD, 0)
        self.set_layout(lv.LAYOUT.FLEX)
        self.set_flex_flow(lv.FLEX_FLOW.COLUMN)
        self.set_style_pad_row(PAD_SM, 0)

        title = lv.label(self)
        title.set_text(gui.i18n.t(self.title_key))
        title.set_style_text_font(theme_font(FONT_TITLE_THEME), 0)
        title.set_style_text_color(theme_color(WHITE_HEX), 0)

        files = self._find_json_files()
        if not files:
            self._status(self.gui.i18n.t("SCHN_NO_COMPATIBLE_JSON"), error=True)
        for filename in files:
            self._add_file(filename)

    def _find_json_files(self):
        try:
            return [name for name in sorted(os.listdir("/sd"))
                    if name.lower().startswith(self.prefix)
                    and name.lower().endswith(".json")]
        except OSError:
            return []

    def _add_file(self, filename):
        button = lv.button(self)
        button.set_size(lv.pct(100), ROW_HEIGHT)
        button.set_style_bg_color(theme_color(BG_CARD_HEX), 0)
        button.set_style_bg_opa(lv.OPA.COVER, 0)
        button.set_style_border_width(0, 0)
        button.set_style_radius(10, 0)
        button.set_style_shadow_width(0, 0)
        button.set_layout(lv.LAYOUT.FLEX)
        button.set_flex_flow(lv.FLEX_FLOW.ROW)
        button.set_flex_align(
            lv.FLEX_ALIGN.START, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER
        )
        button.set_style_pad_column(PAD_SM, 0)

        image = lv.image(button)
        BTC_ICONS.FILE(theme_color(CYAN_HEX)).add_to_parent(
            image, zoom=ROW_ICON_ZOOM
        )
        label = lv.label(button)
        label.set_text(filename)
        label.set_style_text_font(theme_font(FONT_TEXT_THEME), 0)
        label.set_style_text_color(theme_color(WHITE_HEX), 0)
        label.set_flex_grow(1)
        button.add_event_cb(
            lambda event, name=filename: self._install(event, name),
            lv.EVENT.CLICKED,
            None,
        )

    def _install(self, event, filename):
        if event.get_code() != lv.EVENT.CLICKED:
            return
        path = "/sd/" + filename
        if self.kind == "language":
            success = self.gui.i18n.load_language_from_json(path)
        else:
            success = self.gui.theme.load_theme_from_json(path)
        if success:
            self.gui.show_menu(self.return_screen)
        else:
            self._status(self.gui.i18n.t("SCHN_INVALID_JSON"), error=True)

    def _status(self, text, error=False):
        label = lv.label(self)
        label.set_text(text)
        label.set_style_text_font(theme_font(FONT_SMALL_THEME), 0)
        label.set_style_text_color(
            theme_color(RED_HEX if error else GREY_LIGHT_HEX), 0
        )
        label.set_width(lv.pct(100))
        label.set_long_mode(lv.label.LONG_MODE.WRAP)


class LanguageImportScreen(SettingsImportScreen):
    kind = "language"
    title_key = "SCHN_LOAD_LANGUAGE_SD"
    prefix = "specter_ui_"
    return_screen = "language_settings"

    def _find_json_files(self):
        return [name for name in super()._find_json_files()
                if not name.lower().startswith("specter_ui_theme_")]


class ThemeImportScreen(SettingsImportScreen):
    kind = "theme"
    title_key = "SCHN_LOAD_THEME_SD"
    prefix = "specter_ui_theme_"
    return_screen = "theme_settings"
