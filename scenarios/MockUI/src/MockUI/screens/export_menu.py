"""Export menu: wallet export options optimized per wallet type."""
import lvgl as lv
from ..basic.templates.specter_gui_base import t as _tr
from ..basic.ui_consts import (
    theme_color, theme_font, FONT_TITLE_THEME, FONT_TEXT_THEME, FONT_SMALL_THEME, FONT_CAPTION_THEME,
    PAD_MD, PAD_SM, ROW_HEIGHT, ROW_ICON_ZOOM,
    BG_BLACK_HEX, BG_CARD_HEX,
    WHITE_HEX, GREY_LIGHT_HEX, CYAN_HEX,
)
from ..basic.symbol_lib import BTC_ICONS


class ExportMenu(lv.obj):
    """Wallet export options screen."""

    def __init__(self, gui, parent):
        super().__init__(parent)
        self.gui = gui
        self.wallet = gui.specter_state.active_wallet

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
        wallet_name = self.wallet.label if self.wallet else _tr("SCHN_WALLET")
        title.set_text(_tr("SCHN_EXPORT_PREFIX") + wallet_name)
        title.set_style_text_font(theme_font(FONT_TITLE_THEME), 0)
        title.set_style_text_color(theme_color(WHITE_HEX), 0)

        # Export options
        self._add_option(_tr("SCHN_EXPORT_QR"), BTC_ICONS.QR_CODE, "export_qr")
        self._add_option(_tr("SCHN_EXPORT_SD"), BTC_ICONS.SD_CARD, "export_sd")
        self._add_option(_tr("SCHN_EXPORT_XPUB"), BTC_ICONS.KEY, "xpub_export")

        if self.wallet and self.wallet.isMultiSig:
            self._add_option(_tr("SCHN_EXPORT_MULTISIG"), BTC_ICONS.TWO_KEYS, "export_multisig")

    def _add_option(self, text, icon, target):
        btn = lv.button(self)
        btn.set_size(lv.pct(100), ROW_HEIGHT)
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
        icon(theme_color(CYAN_HEX)).add_to_parent(ico, zoom=ROW_ICON_ZOOM)

        lbl = lv.label(btn)
        lbl.set_text(text)
        lbl.set_style_text_font(theme_font(FONT_TEXT_THEME), 0)
        lbl.set_style_text_color(theme_color(WHITE_HEX), 0)
        lbl.set_flex_grow(1)

        arrow = lv.label(btn)
        arrow.set_text(lv.SYMBOL.RIGHT)
        arrow.set_style_text_font(theme_font(FONT_SMALL_THEME), 0)
        arrow.set_style_text_color(theme_color(GREY_LIGHT_HEX), 0)

        btn.add_event_cb(lambda e, t=target: self.gui.show_menu(t), lv.EVENT.CLICKED, None)
