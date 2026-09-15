"""Language selection screen."""
import lvgl as lv
from ..basic.templates.specter_gui_base import t as _tr
from ..basic.ui_consts import (
    theme_color, theme_font, FONT_TITLE_THEME, FONT_TEXT_THEME, FONT_SMALL_THEME, FONT_CAPTION_THEME,
    PAD_MD, PAD_SM, ROW_HEIGHT, ROW_ICON_ZOOM,
    BG_BLACK_HEX, BG_CARD_HEX, BG_ELEVATED_HEX,
    WHITE_HEX, GREY_LIGHT_HEX, GREY_DARK_HEX, CYAN_HEX, GREEN_HEX,
)
from ..basic.symbol_lib import BTC_ICONS


class LanguageScreen(lv.obj):
    """Language selection screen."""

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

        # Title
        title = lv.label(self)
        title.set_text(_tr("SCHN_LANGUAGE"))
        title.set_style_text_font(theme_font(FONT_TITLE_THEME), 0)
        title.set_style_text_color(theme_color(WHITE_HEX), 0)

        # Get available languages
        current_lang = gui.i18n.get_language()
        languages = gui.i18n.get_available_languages()

        for lang_code in languages:
            lang_name = gui.i18n.get_language_name(lang_code)
            is_active = lang_code == current_lang
            self._add_lang_row(lang_code, lang_name, is_active)

        # Load from SD option
        if gui.specter_state.SD_detected():
            divider = lv.obj(self)
            divider.set_size(lv.pct(100), 1)
            divider.set_style_bg_color(theme_color(GREY_DARK_HEX), 0)
            divider.set_style_bg_opa(lv.OPA.COVER, 0)
            divider.set_style_border_width(0, 0)

            load_btn = lv.button(self)
            load_btn.set_size(lv.pct(100), ROW_HEIGHT)
            load_btn.set_style_bg_color(theme_color(BG_CARD_HEX), 0)
            load_btn.set_style_bg_opa(lv.OPA.COVER, 0)
            load_btn.set_style_radius(10, 0)
            load_btn.set_style_border_width(0, 0)
            load_btn.set_style_shadow_width(0, 0)

            load_btn.set_layout(lv.LAYOUT.FLEX)
            load_btn.set_flex_flow(lv.FLEX_FLOW.ROW)
            load_btn.set_flex_align(lv.FLEX_ALIGN.START, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER)
            load_btn.set_style_pad_column(PAD_SM, 0)
            load_btn.set_style_pad_left(PAD_MD, 0)

            ico = lv.image(load_btn)
            BTC_ICONS.SD_CARD(theme_color(CYAN_HEX)).add_to_parent(ico, zoom=ROW_ICON_ZOOM)

            lbl = lv.label(load_btn)
            lbl.set_text(_tr("SCHN_LOAD_FROM_SD"))
            lbl.set_style_text_font(theme_font(FONT_TEXT_THEME), 0)
            lbl.set_style_text_color(theme_color(WHITE_HEX), 0)
            lbl.set_flex_grow(1)

            arrow = lv.label(load_btn)
            arrow.set_text(lv.SYMBOL.RIGHT)
            arrow.set_style_text_font(theme_font(FONT_SMALL_THEME), 0)
            arrow.set_style_text_color(theme_color(GREY_LIGHT_HEX), 0)

            load_btn.add_event_cb(
                lambda event: self.gui.show_menu("import_language"),
                lv.EVENT.CLICKED,
                None,
            )

    def _add_lang_row(self, lang_code, lang_name, is_active):
        btn = lv.button(self)
        btn.set_size(lv.pct(100), ROW_HEIGHT)
        btn.set_style_bg_color(theme_color(BG_ELEVATED_HEX) if is_active else theme_color(BG_CARD_HEX), 0)
        btn.set_style_bg_opa(lv.OPA.COVER, 0)
        btn.set_style_radius(10, 0)
        btn.set_style_shadow_width(0, 0)
        if is_active:
            btn.set_style_border_width(2, 0)
            btn.set_style_border_color(theme_color(CYAN_HEX), 0)
        else:
            btn.set_style_border_width(0, 0)

        btn.set_layout(lv.LAYOUT.FLEX)
        btn.set_flex_flow(lv.FLEX_FLOW.ROW)
        btn.set_flex_align(lv.FLEX_ALIGN.START, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER)
        btn.set_style_pad_column(PAD_SM, 0)
        btn.set_style_pad_left(PAD_MD, 0)

        lbl = lv.label(btn)
        lbl.set_text(lang_name)
        lbl.set_style_text_font(theme_font(FONT_TEXT_THEME), 0)
        lbl.set_style_text_color(theme_color(CYAN_HEX) if is_active else theme_color(WHITE_HEX), 0)
        lbl.set_flex_grow(1)

        if is_active:
            check = lv.label(btn)
            check.set_text(lv.SYMBOL.OK)
            check.set_style_text_font(theme_font(FONT_TEXT_THEME), 0)
            check.set_style_text_color(theme_color(GREEN_HEX), 0)

        btn.add_event_cb(lambda e, lc=lang_code: self._select(lc), lv.EVENT.CLICKED, None)

    def _select(self, lang_code):
        self.gui.change_language(lang_code)
        self.gui.show_menu("language_settings")
