"""Receive screen: shows addresses for the selected wallet."""
import lvgl as lv
from ..basic.templates.specter_gui_base import t as _tr
from ..basic.ui_consts import (
    theme_color, theme_font, FONT_TITLE_THEME, FONT_TEXT_THEME, FONT_SMALL_THEME, FONT_CAPTION_THEME,
    PAD_MD, PAD_SM, PAD_XS,
    BG_BLACK_HEX, BG_CARD_HEX, BG_ELEVATED_HEX, BG_WARN_HEX,
    WHITE_HEX, GREY_LIGHT_HEX, CYAN_HEX, RED_HEX, ORANGE_HEX, YELLOW_HEX,
)
from ..basic.symbol_lib import BTC_ICONS


# Mock addresses for demonstration
_MOCK_ADDRESSES = [
    ("bc1q...xz7k4", False),
    ("bc1q...m9p2e", False),
    ("bc1q...4f8hn", True),   # used - address reuse warning
    ("bc1q...r3j5w", False),
    ("bc1q...t6y2q", False),
]

_MOCK_CHANGE_ADDRESSES = [
    ("bc1q...ch001", False),
    ("bc1q...ch002", False),
    ("bc1q...ch003", False),
]


class ReceiveScreen(lv.obj):
    """Receive addresses for the currently selected wallet."""

    def __init__(self, gui, parent):
        super().__init__(parent)
        self.gui = gui
        self._showing_change = False

        self.set_size(lv.pct(100), lv.pct(100))
        self.set_style_bg_color(theme_color(BG_BLACK_HEX), 0)
        self.set_style_bg_opa(lv.OPA.COVER, 0)
        self.set_style_border_width(0, 0)
        self.set_style_radius(0, 0)
        self.set_style_pad_all(PAD_MD, 0)

        self.set_layout(lv.LAYOUT.FLEX)
        self.set_flex_flow(lv.FLEX_FLOW.COLUMN)
        self.set_style_pad_row(PAD_SM, 0)

        self._build()

    def _build(self):
        self.clean()

        wallet = self.gui.specter_state.active_wallet
        wallet_name = wallet.label if wallet else _tr("SCHN_WALLET")

        # Title row with subtle change address toggle
        header = lv.obj(self)
        header.set_size(lv.pct(100), 36)
        header.set_style_bg_opa(lv.OPA.TRANSP, 0)
        header.set_style_border_width(0, 0)
        header.set_style_pad_all(0, 0)

        title = lv.label(header)
        addr_type = (_tr("SCHN_CHANGE_ADDRESSES") if self._showing_change
                     else _tr("SCHN_RECEIVE_ADDRESSES"))
        title.set_text(addr_type)
        title.set_style_text_font(theme_font(FONT_TITLE_THEME), 0)
        title.set_style_text_color(theme_color(WHITE_HEX), 0)
        title.align(lv.ALIGN.LEFT_MID, 0, 0)

        # Toggle button (slightly hidden at top)
        toggle_btn = lv.button(header)
        toggle_btn.set_size(lv.SIZE_CONTENT, 28)
        toggle_btn.set_style_bg_color(theme_color(BG_CARD_HEX), 0)
        toggle_btn.set_style_bg_opa(lv.OPA.COVER, 0)
        toggle_btn.set_style_radius(4, 0)
        toggle_btn.set_style_border_width(0, 0)
        toggle_btn.set_style_shadow_width(0, 0)
        toggle_btn.set_style_pad_all(PAD_XS, 0)
        toggle_btn.align(lv.ALIGN.RIGHT_MID, 0, 0)

        toggle_lbl = lv.label(toggle_btn)
        toggle_text = (_tr("SCHN_RECEIVE") if self._showing_change
                       else _tr("SCHN_CHANGE"))
        toggle_lbl.set_text(toggle_text)
        toggle_lbl.set_style_text_font(theme_font(FONT_CAPTION_THEME), 0)
        toggle_lbl.set_style_text_color(theme_color(GREY_LIGHT_HEX), 0)
        toggle_lbl.center()

        toggle_btn.add_event_cb(self._toggle_change, lv.EVENT.CLICKED, None)

        # Wallet name subtitle
        subtitle = lv.label(self)
        subtitle.set_text(wallet_name)
        subtitle.set_style_text_font(theme_font(FONT_CAPTION_THEME), 0)
        subtitle.set_style_text_color(theme_color(CYAN_HEX), 0)

        # Address list
        addresses = _MOCK_CHANGE_ADDRESSES if self._showing_change else _MOCK_ADDRESSES
        for idx, (addr, is_used) in enumerate(addresses):
            self._add_address_row(idx, addr, is_used)

    def _add_address_row(self, index, address, is_used):
        row = lv.button(self)
        row.set_size(lv.pct(100), 48)
        row.set_style_radius(8, 0)
        row.set_style_border_width(0, 0)
        row.set_style_shadow_width(0, 0)

        if is_used:
            row.set_style_bg_color(theme_color(BG_WARN_HEX), 0)  # subtle warning bg
        else:
            row.set_style_bg_color(theme_color(BG_CARD_HEX), 0)
        row.set_style_bg_opa(lv.OPA.COVER, 0)

        row.set_layout(lv.LAYOUT.FLEX)
        row.set_flex_flow(lv.FLEX_FLOW.ROW)
        row.set_flex_align(lv.FLEX_ALIGN.START, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER)
        row.set_style_pad_column(PAD_SM, 0)
        row.set_style_pad_left(PAD_SM, 0)

        # Index
        idx_lbl = lv.label(row)
        idx_lbl.set_text("#" + str(index))
        idx_lbl.set_style_text_font(theme_font(FONT_CAPTION_THEME), 0)
        idx_lbl.set_style_text_color(theme_color(GREY_LIGHT_HEX), 0)

        # Address
        addr_lbl = lv.label(row)
        addr_lbl.set_text(address)
        addr_lbl.set_style_text_font(theme_font(FONT_CAPTION_THEME), 0)
        addr_lbl.set_style_text_color(theme_color(WHITE_HEX), 0)
        addr_lbl.set_flex_grow(1)

        # Address reuse warning
        if is_used:
            warn = lv.image(row)
            BTC_ICONS.ALERT(theme_color(YELLOW_HEX)).add_to_parent(warn, zoom=110)

        # Tap to show QR
        row.add_event_cb(lambda e, a=address: self._show_address_qr(a), lv.EVENT.CLICKED, None)

    def _toggle_change(self, e):
        if e.get_code() == lv.EVENT.CLICKED:
            self._showing_change = not self._showing_change
            self._build()

    def _show_address_qr(self, address):
        self.gui.show_menu("address_qr")
