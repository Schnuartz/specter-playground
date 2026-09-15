"""Security Settings submenu: backup/restore, firmware info, wipe device.

Split out of the main Settings page so Security groups as its own submenu,
matching the section layout of the upstream specter-playground Settings page
(https://github.com/k9ert/specter-playground) rather than one long flat list.
"""
import lvgl as lv
from ..basic.templates.specter_gui_base import t as _tr
from ..basic.ui_consts import (
    theme_color, theme_font, FONT_TITLE_THEME, FONT_TEXT_THEME, FONT_SMALL_THEME, FONT_CAPTION_THEME,
    PAD_MD, PAD_SM,
    BG_BLACK_HEX, BG_CARD_HEX,
    WHITE_HEX, GREY_LIGHT_HEX, CYAN_HEX, RED_HEX,
)
from ..basic.symbol_lib import BTC_ICONS


class SecuritySettingsScreen(lv.obj):
    """Security-related settings, grouped separately from general device settings."""

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
        title.set_text(_tr("SCHN_SECURITY_SETTINGS"))
        title.set_style_text_font(theme_font(FONT_TITLE_THEME), 0)
        title.set_style_text_color(theme_color(WHITE_HEX), 0)

        self._add_nav_item(_tr("SCHN_BACKUP_RESTORE"), BTC_ICONS.SAFE, "backup")
        self._add_nav_item(_tr("SCHN_FIRMWARE_INFO"), BTC_ICONS.INFO, "firmware_info")

        danger_lbl = lv.label(self)
        danger_lbl.set_text(_tr("SCHN_DANGER_ZONE"))
        danger_lbl.set_style_text_font(theme_font(FONT_TEXT_THEME), 0)
        danger_lbl.set_style_text_color(theme_color(RED_HEX), 0)

        self._add_nav_item(_tr("SCHN_WIPE_DEVICE"), BTC_ICONS.TRASH, "wipe_device", color=theme_color(RED_HEX))

    def _add_nav_item(self, text, icon, target, color=None):
        btn = lv.button(self)
        btn.set_size(lv.pct(100), 60)
        btn.set_style_bg_color(theme_color(BG_CARD_HEX), 0)
        btn.set_style_bg_opa(lv.OPA.COVER, 0)
        btn.set_style_radius(10, 0)
        btn.set_style_border_width(0, 0)
        btn.set_style_shadow_width(0, 0)

        btn.set_layout(lv.LAYOUT.FLEX)
        btn.set_flex_flow(lv.FLEX_FLOW.ROW)
        btn.set_flex_align(lv.FLEX_ALIGN.START, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER)
        btn.set_style_pad_column(PAD_SM, 0)
        btn.set_style_pad_left(PAD_MD, 0)

        ico = lv.image(btn)
        txt_color = color if color else theme_color(WHITE_HEX)
        icon(txt_color).add_to_parent(ico, zoom=150)

        lbl = lv.label(btn)
        lbl.set_text(text)
        lbl.set_style_text_font(theme_font(FONT_TEXT_THEME), 0)
        lbl.set_style_text_color(txt_color, 0)
        lbl.set_flex_grow(1)

        arrow = lv.label(btn)
        arrow.set_text(lv.SYMBOL.RIGHT)
        arrow.set_style_text_color(theme_color(GREY_LIGHT_HEX), 0)

        btn.add_event_cb(lambda e, t=target: self.gui.show_menu(t), lv.EVENT.CLICKED, None)
