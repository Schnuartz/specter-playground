"""xPub export screen — shows extended public key info."""
import lvgl as lv
from ..basic.templates.specter_gui_base import t as _tr
from ..basic.ui_consts import (
    theme_color, theme_font, FONT_TITLE_THEME, FONT_TEXT_THEME, FONT_SMALL_THEME, FONT_CAPTION_THEME,
    PAD_MD, PAD_SM, PAD_LG,
    BG_BLACK_HEX, BG_CARD_HEX,
    WHITE_HEX, GREY_LIGHT_HEX, CYAN_HEX,
)
from ..basic.symbol_lib import BTC_ICONS


class XPubExportScreen(lv.obj):
    """Display xPub key with QR code option."""

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
        self.set_flex_align(lv.FLEX_ALIGN.START, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER)
        self.set_style_pad_row(PAD_SM, 0)

        title = lv.label(self)
        title.set_text(_tr("SCHN_XPUB_EXPORT"))
        title.set_style_text_font(theme_font(FONT_TEXT_THEME), 0)
        title.set_style_text_color(theme_color(WHITE_HEX), 0)

        seed = gui.specter_state.active_seed
        if seed:
            seed_lbl = lv.label(self)
            seed_lbl.set_text(_tr("SCHN_SEED_PREFIX") + seed.label + " [" + seed.fingerprint[:8] + "]")
            seed_lbl.set_style_text_font(theme_font(FONT_CAPTION_THEME), 0)
            seed_lbl.set_style_text_color(theme_color(CYAN_HEX), 0)

        # Derivation paths
        paths = [
            ("Native Segwit (BIP84)", "m/84'/0'/0'", "zpub..."),
            ("Nested Segwit (BIP49)", "m/49'/0'/0'", "ypub..."),
            ("Legacy (BIP44)", "m/44'/0'/0'", "xpub..."),
            ("Multisig (BIP48)", "m/48'/0'/0'/2'", "Zpub..."),
        ]

        for name, path, key_prefix in paths:
            self._add_xpub_row(name, path, key_prefix)

    def _add_xpub_row(self, name, path, key_prefix):
        card = lv.obj(self)
        card.set_size(lv.pct(100), 80)
        card.set_style_bg_color(theme_color(BG_CARD_HEX), 0)
        card.set_style_bg_opa(lv.OPA.COVER, 0)
        card.set_style_radius(10, 0)
        card.set_style_border_width(0, 0)
        card.set_style_pad_all(PAD_SM, 0)

        name_lbl = lv.label(card)
        name_lbl.set_text(name)
        name_lbl.set_style_text_font(theme_font(FONT_TEXT_THEME), 0)
        name_lbl.set_style_text_color(theme_color(WHITE_HEX), 0)
        name_lbl.align(lv.ALIGN.TOP_LEFT, 0, 0)

        path_lbl = lv.label(card)
        path_lbl.set_text(path)
        path_lbl.set_style_text_font(theme_font(FONT_SMALL_THEME), 0)
        path_lbl.set_style_text_color(theme_color(GREY_LIGHT_HEX), 0)
        path_lbl.align(lv.ALIGN.BOTTOM_LEFT, 0, 0)

        # QR button
        qr_btn = lv.button(card)
        qr_btn.set_size(56, 56)
        qr_btn.set_style_bg_opa(lv.OPA.TRANSP, 0)
        qr_btn.set_style_border_width(0, 0)
        qr_btn.set_style_shadow_width(0, 0)
        qr_btn.align(lv.ALIGN.RIGHT_MID, 0, 0)

        qr_ico = lv.image(qr_btn)
        BTC_ICONS.QR_CODE(theme_color(CYAN_HEX)).add_to_parent(qr_ico, zoom=220)
        qr_ico.center()

        card.add_flag(lv.obj.FLAG.CLICKABLE)
        card.add_event_cb(lambda e: self.gui.show_menu("address_qr"), lv.EVENT.CLICKED, None)
