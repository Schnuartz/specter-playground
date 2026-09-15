"""Scan screen: QR scanner with auto-detection of content type."""
import lvgl as lv
from ..basic.templates.specter_gui_base import t as _tr
from ..basic.ui_consts import (
    theme_color, theme_font, FONT_TITLE_THEME, FONT_TEXT_THEME, FONT_SMALL_THEME, FONT_CAPTION_THEME,
    PAD_MD, PAD_SM, PAD_LG,
    BG_BLACK_HEX, BG_DARK_HEX, BG_CARD_HEX,
    WHITE_HEX, GREY_LIGHT_HEX, CYAN_HEX,
)
from ..basic.symbol_lib import BTC_ICONS


class ScanScreen(lv.obj):
    """QR scanner screen with viewfinder and status."""

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
        self.set_flex_align(lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER)
        self.set_style_pad_row(PAD_LG, 0)

        # Title
        title = lv.label(self)
        title.set_text(_tr("SCHN_SCAN_QR_CODE"))
        title.set_style_text_font(theme_font(FONT_TITLE_THEME), 0)
        title.set_style_text_color(theme_color(WHITE_HEX), 0)

        # Scanner viewfinder area (placeholder)
        viewfinder = lv.obj(self)
        viewfinder.set_size(280, 280)
        viewfinder.set_style_bg_color(theme_color(BG_DARK_HEX), 0)
        viewfinder.set_style_bg_opa(lv.OPA.COVER, 0)
        viewfinder.set_style_border_width(2, 0)
        viewfinder.set_style_border_color(theme_color(CYAN_HEX), 0)
        viewfinder.set_style_radius(12, 0)

        # QR icon in center
        qr_ico = lv.image(viewfinder)
        BTC_ICONS.QR_CODE(theme_color(CYAN_HEX)).add_to_parent(qr_ico, zoom=300)
        qr_ico.center()

        # Status text
        status = lv.label(self)
        status.set_text(_tr("SCHN_POINT_CAMERA"))
        status.set_style_text_font(theme_font(FONT_SMALL_THEME), 0)
        status.set_style_text_color(theme_color(GREY_LIGHT_HEX), 0)

        # Auto-detect info
        info = lv.label(self)
        info.set_text(_tr("SCHN_DETECTS_TYPES"))
        info.set_style_text_font(theme_font(FONT_CAPTION_THEME), 0)
        info.set_style_text_color(theme_color(GREY_LIGHT_HEX), 0)
