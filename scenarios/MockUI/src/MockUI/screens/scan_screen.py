"""Scan screen: QR scanner with auto-detection of content type."""
import lvgl as lv
from ..basic.templates.specter_gui_base import t as _tr
from ..basic.ui_consts import (
    theme_color, theme_font, FONT_TITLE_THEME, FONT_TEXT_THEME,
    PAD_MD, PAD_LG,
    BG_BLACK_HEX, BG_DARK_HEX,
    WHITE_HEX, GREY_LIGHT_HEX, CYAN_HEX,
)
from ..basic.symbol_lib import BTC_ICONS
from ..basic.widgets import Btn, button_modal


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
        self.set_style_pad_all(0, 0)

        # Keep the scanner content centered while anchoring its help control
        # independently in the upper-left corner.
        content = lv.obj(self)
        content.set_size(lv.pct(100), lv.pct(100))
        content.set_style_bg_opa(lv.OPA.TRANSP, 0)
        content.set_style_border_width(0, 0)
        content.set_style_radius(0, 0)
        content.set_style_pad_all(PAD_MD, 0)
        content.set_layout(lv.LAYOUT.FLEX)
        content.set_flex_flow(lv.FLEX_FLOW.COLUMN)
        content.set_flex_align(lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER)
        content.set_style_pad_row(PAD_LG, 0)

        # Title
        title = lv.label(content)
        title.set_text(_tr("SCHN_SCAN_QR_CODE"))
        title.set_style_text_font(theme_font(FONT_TITLE_THEME), 0)
        title.set_style_text_color(theme_color(WHITE_HEX), 0)

        # Scanner viewfinder area (placeholder)
        viewfinder = lv.obj(content)
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
        status = lv.label(content)
        status.set_text(_tr("SCHN_POINT_CAMERA"))
        status.set_style_text_font(theme_font(FONT_TITLE_THEME), 0)
        status.set_style_text_color(theme_color(GREY_LIGHT_HEX), 0)

        # Auto-detect info
        info = lv.label(content)
        info.set_text(_tr("SCHN_DETECTS_TYPES"))
        info.set_width(lv.pct(100))
        info.set_long_mode(lv.label.LONG_MODE.WRAP)
        info.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
        info.set_style_text_font(theme_font(FONT_TEXT_THEME), 0)
        info.set_style_text_color(theme_color(GREY_LIGHT_HEX), 0)

        help_text = _tr("MAIN_MENU_SCAN_QR") + "\n\n" + _tr("HELP_SCAN_QR")
        help_btn = Btn(
            self,
            icon=BTC_ICONS.QUESTION_CIRCLE,
            callback=lambda: button_modal(text=help_text),
            consume_click=True,
            background_style="APPEARANCE.TRANSPARENT",
            foreground_style="WIDGET.HELP_ICON",
        )
        help_btn.align(lv.ALIGN.TOP_LEFT, PAD_MD, PAD_MD)
