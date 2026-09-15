"""Theme selection for the Schnuartz settings flow."""

import lvgl as lv

from ..basic.symbol_lib import BTC_ICONS
from ..basic.theming import ColorMode
from ..basic.ui_consts import (
    ROW_HEIGHT, ROW_ICON_ZOOM, PAD_MD, PAD_SM,
    BG_BLACK_HEX, BG_CARD_HEX, BG_ELEVATED_HEX,
    WHITE_HEX, GREY_LIGHT_HEX, CYAN_HEX, GREEN_HEX,
    theme_color, theme_font, FONT_TITLE_THEME, FONT_TEXT_THEME,
)


class ThemeScreen(lv.obj):
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
        title.set_text(gui.i18n.t("DEVICE_MENU_THEME"))
        title.set_style_text_font(theme_font(FONT_TITLE_THEME), 0)
        title.set_style_text_color(theme_color(WHITE_HEX), 0)

        for theme_name in gui.theme.get_available_files():
            self._add_theme_row(theme_name, theme_name == gui.theme.current)

        self._add_mode_row()

        if gui.specter_state.SD_detected():
            self._add_action_row(
                gui.i18n.t("MENU_LOAD_NEW_THEME"),
                BTC_ICONS.SD_CARD,
                lambda: gui.show_menu("import_theme"),
            )

    def _base_button(self, selected=False):
        button = lv.button(self)
        button.set_size(lv.pct(100), ROW_HEIGHT)
        button.set_style_bg_color(
            theme_color(BG_ELEVATED_HEX if selected else BG_CARD_HEX), 0
        )
        button.set_style_bg_opa(lv.OPA.COVER, 0)
        button.set_style_radius(10, 0)
        button.set_style_shadow_width(0, 0)
        button.set_style_border_width(2 if selected else 0, 0)
        if selected:
            button.set_style_border_color(theme_color(CYAN_HEX), 0)
        button.set_layout(lv.LAYOUT.FLEX)
        button.set_flex_flow(lv.FLEX_FLOW.ROW)
        button.set_flex_align(
            lv.FLEX_ALIGN.START, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER
        )
        button.set_style_pad_column(PAD_SM, 0)
        button.set_style_pad_left(PAD_MD, 0)
        return button

    def _add_theme_row(self, theme_name, selected):
        button = self._base_button(selected)
        label = lv.label(button)
        label.set_text(self.gui.theme.get_file_name(theme_name) or theme_name)
        label.set_style_text_font(theme_font(FONT_TEXT_THEME), 0)
        label.set_style_text_color(
            theme_color(CYAN_HEX if selected else WHITE_HEX), 0
        )
        label.set_flex_grow(1)
        if selected:
            check = lv.image(button)
            BTC_ICONS.CHECK(theme_color(GREEN_HEX)).add_to_parent(
                check, zoom=ROW_ICON_ZOOM
            )
        button.add_event_cb(
            lambda event, name=theme_name: self._select_theme(event, name),
            lv.EVENT.CLICKED,
            None,
        )

    def _add_mode_row(self):
        button = self._base_button(False)
        label = lv.label(button)
        label.set_text(self.gui.i18n.t("DEVICE_MENU_DARK_MODE"))
        label.set_style_text_font(theme_font(FONT_TEXT_THEME), 0)
        label.set_style_text_color(theme_color(WHITE_HEX), 0)
        label.set_flex_grow(1)
        mode_switch = lv.switch(button)
        mode_switch.set_size(62, 32)
        mode_switch.set_style_bg_color(
            theme_color(CYAN_HEX), lv.PART.INDICATOR | lv.STATE.CHECKED
        )
        if self.gui.theme.mode == ColorMode.DARK:
            mode_switch.add_state(lv.STATE.CHECKED)
        mode_switch.add_event_cb(self._toggle_mode, lv.EVENT.VALUE_CHANGED, None)
        button.add_event_cb(self._toggle_mode, lv.EVENT.CLICKED, None)

    def _add_action_row(self, text, icon, callback):
        button = self._base_button(False)
        image = lv.image(button)
        icon(theme_color(CYAN_HEX)).add_to_parent(image, zoom=ROW_ICON_ZOOM)
        label = lv.label(button)
        label.set_text(text)
        label.set_style_text_font(theme_font(FONT_TEXT_THEME), 0)
        label.set_style_text_color(theme_color(WHITE_HEX), 0)
        button.add_event_cb(lambda event: callback(), lv.EVENT.CLICKED, None)

    def _select_theme(self, event, theme_name):
        if event.get_code() == lv.EVENT.CLICKED:
            self.gui.change_theme(theme_name)

    def _toggle_mode(self, event):
        if event.get_code() != lv.EVENT.CLICKED:
            return
        mode = (ColorMode.LIGHT
                if self.gui.theme.mode == ColorMode.DARK
                else ColorMode.DARK)
        self.gui.change_mode(mode)
