"""Signing screen: transaction review and signing flow."""
import lvgl as lv
from ..basic.templates.specter_gui_base import t as _tr
from ..basic.ui_consts import (
    theme_color, theme_font, FONT_TITLE_THEME, FONT_TEXT_THEME, FONT_SMALL_THEME, FONT_CAPTION_THEME,
    PAD_MD, PAD_SM, PAD_LG,
    BG_BLACK_HEX, BG_CARD_HEX,
    WHITE_HEX, GREY_LIGHT_HEX, CYAN_HEX, CYAN_DARK_HEX, GREEN_HEX, ORANGE_HEX, RED_HEX,
)
from ..basic.symbol_lib import BTC_ICONS


class SigningScreen(lv.obj):
    """Transaction signing review screen."""

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
        title.set_text(_tr("SCHN_SIGN_TRANSACTION"))
        title.set_style_text_font(theme_font(FONT_TITLE_THEME), 0)
        title.set_style_text_color(theme_color(WHITE_HEX), 0)

        # Transaction summary (mock data)
        self._add_info_row(_tr("SCHN_SENDING_TO"), "bc1q...xz7k4")
        self._add_info_row(_tr("SCHN_AMOUNT"), "0.005 BTC")
        self._add_info_row(_tr("SCHN_FEE"), "0.00001 BTC")
        self._add_info_row(_tr("SCHN_WALLET"), gui.specter_state.active_wallet.label if gui.specter_state.active_wallet else "N/A")

        # Spacer
        spacer = lv.obj(self)
        spacer.set_size(lv.pct(100), 20)
        spacer.set_style_bg_opa(lv.OPA.TRANSP, 0)
        spacer.set_style_border_width(0, 0)

        # Sign button
        sign_btn = lv.button(self)
        sign_btn.set_size(lv.pct(100), 60)
        sign_btn.set_style_bg_color(theme_color(GREEN_HEX), 0)
        sign_btn.set_style_bg_opa(lv.OPA.COVER, 0)
        sign_btn.set_style_radius(12, 0)
        sign_btn.set_style_border_width(0, 0)
        sign_btn.set_style_shadow_width(0, 0)

        sign_lbl = lv.label(sign_btn)
        sign_lbl.set_text(_tr("SCHN_CONFIRM_SIGN"))
        sign_lbl.set_style_text_font(theme_font(FONT_TEXT_THEME), 0)
        sign_lbl.set_style_text_color(theme_color(WHITE_HEX), 0)
        sign_lbl.center()

        sign_btn.add_event_cb(self._sign_cb, lv.EVENT.CLICKED, None)

        # Reject button
        reject_btn = lv.button(self)
        reject_btn.set_size(lv.pct(100), 48)
        reject_btn.set_style_bg_color(theme_color(BG_CARD_HEX), 0)
        reject_btn.set_style_bg_opa(lv.OPA.COVER, 0)
        reject_btn.set_style_radius(12, 0)
        reject_btn.set_style_border_width(1, 0)
        reject_btn.set_style_border_color(theme_color(RED_HEX), 0)
        reject_btn.set_style_shadow_width(0, 0)

        reject_lbl = lv.label(reject_btn)
        reject_lbl.set_text(_tr("SCHN_REJECT"))
        reject_lbl.set_style_text_font(theme_font(FONT_TEXT_THEME), 0)
        reject_lbl.set_style_text_color(theme_color(RED_HEX), 0)
        reject_lbl.center()

        reject_btn.add_event_cb(lambda e: self.gui.show_menu(None), lv.EVENT.CLICKED, None)

    def _add_info_row(self, label, value):
        row = lv.obj(self)
        row.set_size(lv.pct(100), 56)
        row.set_style_bg_color(theme_color(BG_CARD_HEX), 0)
        row.set_style_bg_opa(lv.OPA.COVER, 0)
        row.set_style_radius(10, 0)
        row.set_style_border_width(0, 0)
        row.set_style_pad_left(PAD_MD, 0)
        row.set_style_pad_right(PAD_MD, 0)

        key = lv.label(row)
        key.set_text(label)
        key.set_style_text_font(theme_font(FONT_SMALL_THEME), 0)
        key.set_style_text_color(theme_color(GREY_LIGHT_HEX), 0)
        key.align(lv.ALIGN.LEFT_MID, 0, 0)

        val = lv.label(row)
        val.set_text(value)
        val.set_style_text_font(theme_font(FONT_TEXT_THEME), 0)
        val.set_style_text_color(theme_color(WHITE_HEX), 0)
        val.align(lv.ALIGN.RIGHT_MID, 0, 0)

    def _sign_cb(self, e):
        if e.get_code() == lv.EVENT.CLICKED:
            # TODO: actual signing logic
            self.gui.show_menu("main")
