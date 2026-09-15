"""Address QR display screen — shows address as QR code with copy option."""
import lvgl as lv
from ..basic.templates.specter_gui_base import t as _tr
from ..basic.ui_consts import (
    theme_color, theme_font, FONT_TITLE_THEME, FONT_TEXT_THEME, FONT_SMALL_THEME, FONT_CAPTION_THEME,
    PAD_MD, PAD_SM, PAD_LG,
    BG_BLACK_HEX, BG_CARD_HEX,
    WHITE_HEX, BLACK_HEX, GREY_LIGHT_HEX, CYAN_HEX,
)
from ..basic.symbol_lib import BTC_ICONS


class AddressQRScreen(lv.obj):
    """Display a Bitcoin address as QR code (mock)."""

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

        title = lv.label(self)
        title.set_text(_tr("SCHN_RECEIVE_ADDRESS"))
        title.set_style_text_font(theme_font(FONT_TITLE_THEME), 0)
        title.set_style_text_color(theme_color(WHITE_HEX), 0)

        # QR code placeholder
        qr_box = lv.obj(self)
        qr_box.set_size(240, 240)
        qr_box.set_style_bg_color(theme_color(WHITE_HEX), 0)
        qr_box.set_style_bg_opa(lv.OPA.COVER, 0)
        qr_box.set_style_radius(12, 0)
        qr_box.set_style_border_width(0, 0)

        # QR icon in center (placeholder for actual QR)
        qr_ico = lv.image(qr_box)
        BTC_ICONS.QR_CODE(theme_color(BLACK_HEX)).add_to_parent(qr_ico, zoom=400)
        qr_ico.center()

        # Address text
        addr = lv.label(self)
        addr.set_text("bc1q...xz7k4m9p2e")
        addr.set_style_text_font(theme_font(FONT_SMALL_THEME), 0)
        addr.set_style_text_color(theme_color(CYAN_HEX), 0)
        addr.set_width(lv.pct(90))
        addr.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)

        # Wallet info
        wallet = gui.specter_state.active_wallet
        if wallet:
            w_lbl = lv.label(self)
            w_lbl.set_text(wallet.label)
            w_lbl.set_style_text_font(theme_font(FONT_CAPTION_THEME), 0)
            w_lbl.set_style_text_color(theme_color(GREY_LIGHT_HEX), 0)
