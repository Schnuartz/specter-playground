"""Wallet details: long-press options for a wallet."""
import lvgl as lv
from ..basic.templates.specter_gui_base import t as _tr
from ..basic.ui_consts import (
    theme_color, theme_font, FONT_TITLE_THEME, FONT_TEXT_THEME, FONT_SMALL_THEME, FONT_CAPTION_THEME,
    PAD_MD, PAD_SM, ROW_HEIGHT, ROW_ICON_ZOOM,
    BG_BLACK_HEX, BG_CARD_HEX, BG_ELEVATED_HEX,
    WHITE_HEX, GREY_LIGHT_HEX, CYAN_HEX, ORANGE_HEX, GREEN_HEX,
)
from ..basic.symbol_lib import BTC_ICONS


class WalletDetails(lv.obj):
    """Long-press wallet options screen."""

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

        # Title: wallet name
        title = lv.label(self)
        name = self.wallet.label if self.wallet else _tr("SCHN_WALLET")
        title.set_text(name)
        title.set_style_text_font(theme_font(FONT_TITLE_THEME), 0)
        title.set_style_text_color(theme_color(WHITE_HEX), 0)

        if not self.wallet:
            return

        # Wallet info card
        info_card = lv.obj(self)
        info_card.set_size(lv.pct(100), 60)
        info_card.set_style_bg_color(theme_color(BG_CARD_HEX), 0)
        info_card.set_style_bg_opa(lv.OPA.COVER, 0)
        info_card.set_style_radius(10, 0)
        info_card.set_style_border_width(1, 0)
        info_card.set_style_border_color(theme_color(CYAN_HEX), 0)
        info_card.set_style_pad_all(PAD_SM, 0)

        detail_parts = []
        if self.wallet.isMultiSig and self.wallet.threshold:
            detail_parts.append(str(self.wallet.threshold) + "-of-" + str(len(self.wallet.required_fingerprints)))
        detail_parts.append(self.wallet.net)
        if self.wallet.has_been_exported:
            detail_parts.append(_tr("SCHN_SHARED"))

        detail = lv.label(info_card)
        detail.set_text(" | ".join(detail_parts))
        detail.set_style_text_font(theme_font(FONT_CAPTION_THEME), 0)
        detail.set_style_text_color(theme_color(GREY_LIGHT_HEX), 0)
        detail.align(lv.ALIGN.LEFT_MID, 0, 0)

        # Options
        self._add_option(_tr("SCHN_RENAME_WALLET"), BTC_ICONS.EDIT, "rename_wallet")
        self._add_option(_tr("SCHN_SHOW_ADVANCED"), BTC_ICONS.INFO, "advanced_details")
        self._add_option(_tr("SCHN_SHOW_RECEIVE"), BTC_ICONS.RECEIVE, "receive")
        self._add_option(_tr("SCHN_SHOW_CHANGE"), BTC_ICONS.EXCHANGE, "change_addresses")

        # Multi-sig only: co-signers
        if self.wallet.isMultiSig:
            self._add_option(_tr("SCHN_SHOW_COSIGNERS"), BTC_ICONS.TWO_KEYS, "cosigners")

        self._add_option(_tr("SCHN_CONNECT_COMPANION"), BTC_ICONS.LINK, "connect_app")
        self._add_option(_tr("SCHN_EXPORT_WALLET"), BTC_ICONS.EXPORT, "export")
        self._add_option(_tr("SCHN_SIGN_MESSAGE"), BTC_ICONS.SIGN, "sign_message")

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
