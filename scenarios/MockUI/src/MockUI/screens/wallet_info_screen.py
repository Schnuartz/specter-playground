"""Wallet info page: shows all wallet details structured by type.
Wallet Type (heading), Address Type (subheading), Account, Shared With (logos)."""
import lvgl as lv
from ..basic.templates.specter_gui_base import t as _tr
from ..basic.ui_consts import (
    theme_color, theme_font, FONT_TITLE_THEME, FONT_TEXT_THEME, FONT_SMALL_THEME, FONT_CAPTION_THEME,
    PAD_MD, PAD_SM, PAD_LG, PAD_XS, ROW_HEIGHT, ROW_ICON_ZOOM,
    BG_BLACK_HEX, BG_CARD_HEX, BG_ELEVATED_HEX,
    WHITE_HEX, GREY_LIGHT_HEX, CYAN_HEX, GREEN_HEX, ORANGE_HEX,
)
from ..basic.symbol_lib import BTC_ICONS
from ..basic.wallet_list import _get_app_icon
from ..stubs.wallet import ADDR_NATIVE_SEGWIT, ADDR_LEGACY, ADDR_TAPROOT, ADDR_NESTED_SEGWIT


_ADDR_NAME_KEYS = {
    ADDR_NATIVE_SEGWIT: "SCHN_NATIVE_SEGWIT",
    ADDR_NESTED_SEGWIT: "SCHN_NESTED_SEGWIT",
    ADDR_LEGACY: "SCHN_LEGACY",
    ADDR_TAPROOT: "SCHN_TAPROOT",
}


class WalletInfoScreen(lv.obj):
    """Dedicated wallet page with full info and actions."""

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

        if not self.wallet:
            lbl = lv.label(self)
            lbl.set_text(_tr("SCHN_NO_WALLET_SELECTED"))
            lbl.set_style_text_color(theme_color(GREY_LIGHT_HEX), 0)
            return

        w = self.wallet

        # === Wallet Name (large) ===
        name_lbl = lv.label(self)
        name_lbl.set_text(w.label)
        name_lbl.set_style_text_font(theme_font(FONT_TITLE_THEME), 0)
        name_lbl.set_style_text_color(theme_color(WHITE_HEX), 0)

        # === Info Card with structured display ===
        info = lv.obj(self)
        info.set_size(lv.pct(100), lv.SIZE_CONTENT)
        info.set_style_bg_color(theme_color(BG_CARD_HEX), 0)
        info.set_style_bg_opa(lv.OPA.COVER, 0)
        info.set_style_radius(12, 0)
        info.set_style_border_width(1, 0)
        info.set_style_border_color(theme_color(CYAN_HEX), 0)
        info.set_style_pad_all(PAD_MD, 0)
        info.set_style_pad_row(PAD_XS, 0)
        info.set_layout(lv.LAYOUT.FLEX)
        info.set_flex_flow(lv.FLEX_FLOW.COLUMN)

        # Wallet Type (heading)
        type_label = lv.label(info)
        type_label.set_text(_tr("SCHN_WALLET_TYPE"))
        type_label.set_style_text_font(theme_font(FONT_CAPTION_THEME), 0)
        type_label.set_style_text_color(theme_color(GREY_LIGHT_HEX), 0)

        if w.isMultiSig and w.threshold:
            wtype = (str(w.threshold) + "-of-" + str(len(w.required_fingerprints))
                     + " " + _tr("COMMON_MULTISIG"))
        elif not w.is_standard():
            wtype = _tr("COMMON_MINISCRIPT")
        else:
            wtype = _tr("COMMON_SINGLESIG")
        type_val = lv.label(info)
        type_val.set_text(wtype)
        type_val.set_style_text_font(theme_font(FONT_TEXT_THEME), 0)
        type_val.set_style_text_color(theme_color(WHITE_HEX), 0)

        # Address Type (subheading)
        addr_label = lv.label(info)
        addr_label.set_text(_tr("SCHN_ADDRESS_TYPE"))
        addr_label.set_style_text_font(theme_font(FONT_CAPTION_THEME), 0)
        addr_label.set_style_text_color(theme_color(GREY_LIGHT_HEX), 0)

        addr_name = _tr(_ADDR_NAME_KEYS.get(w.address_type, "SCHN_NATIVE_SEGWIT"))
        addr_val = lv.label(info)
        addr_val.set_text(addr_name)
        addr_val.set_style_text_font(theme_font(FONT_SMALL_THEME), 0)
        addr_val.set_style_text_color(theme_color(CYAN_HEX), 0)

        # Account Number
        acc_label = lv.label(info)
        acc_label.set_text(_tr("SCHN_ACCOUNT"))
        acc_label.set_style_text_font(theme_font(FONT_CAPTION_THEME), 0)
        acc_label.set_style_text_color(theme_color(GREY_LIGHT_HEX), 0)

        acc_val = lv.label(info)
        acc_val.set_text(_tr("SCHN_ACCOUNT_PREFIX") + str(w.account))
        acc_val.set_style_text_font(theme_font(FONT_SMALL_THEME), 0)
        acc_val.set_style_text_color(theme_color(WHITE_HEX), 0)

        # Shared With (companion app logos — BIG)
        if w.shared_with:
            shared_label = lv.label(info)
            shared_label.set_text(_tr("SCHN_SHARED_WITH"))
            shared_label.set_style_text_font(theme_font(FONT_CAPTION_THEME), 0)
            shared_label.set_style_text_color(theme_color(GREY_LIGHT_HEX), 0)

            logos_row = lv.obj(info)
            logos_row.set_size(lv.pct(100), 48)
            logos_row.set_style_bg_opa(lv.OPA.TRANSP, 0)
            logos_row.set_style_border_width(0, 0)
            logos_row.set_style_pad_all(0, 0)
            logos_row.set_layout(lv.LAYOUT.FLEX)
            logos_row.set_flex_flow(lv.FLEX_FLOW.ROW)
            logos_row.set_flex_align(lv.FLEX_ALIGN.START, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER)
            logos_row.set_style_pad_column(PAD_SM, 0)

            for app_name in w.shared_with:
                # Big app logo
                app_ico = lv.image(logos_row)
                icon = _get_app_icon(app_name)
                if icon:
                    icon.add_to_parent(app_ico, zoom=200)

                # App name next to logo
                app_lbl = lv.label(logos_row)
                app_lbl.set_text(app_name)
                app_lbl.set_style_text_font(theme_font(FONT_CAPTION_THEME), 0)
                app_lbl.set_style_text_color(theme_color(GREEN_HEX), 0)

        # === Action buttons ===
        self._add_action(_tr("SCHN_RECEIVE_ADDRESSES"), BTC_ICONS.RECEIVE, "receive")
        self._add_action(_tr("SCHN_CHANGE_ADDRESSES"), BTC_ICONS.EXCHANGE, "receive")
        self._add_action(_tr("SCHN_EXPORT_WALLET"), BTC_ICONS.EXPORT, "export")
        self._add_action(_tr("SCHN_CONNECT_COMPANION"), BTC_ICONS.LINK, "connect_app")

        if w.isMultiSig:
            self._add_action(_tr("SCHN_SHOW_COSIGNERS"), BTC_ICONS.TWO_KEYS, "cosigners")

        self._add_action(_tr("SCHN_XPUB_EXPORT"), BTC_ICONS.KEY, "xpub_export")
        self._add_action(_tr("SCHN_RENAME_WALLET"), BTC_ICONS.EDIT, "rename_wallet")

    def _add_action(self, text, icon, target):
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
