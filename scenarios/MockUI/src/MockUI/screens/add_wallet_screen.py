"""Add wallet screen: create custom wallet or import from descriptor.
Follows Specter-DIY approach — no testnet toggle."""
import lvgl as lv
from ..basic.templates.specter_gui_base import t as _tr
import urandom
from ..basic.ui_consts import (
    theme_color, theme_font, FONT_TITLE_THEME, FONT_TEXT_THEME, FONT_SMALL_THEME, FONT_CAPTION_THEME,
    PAD_MD, PAD_SM, PAD_LG, ROW_HEIGHT, ROW_ICON_ZOOM,
    BG_BLACK_HEX, BG_CARD_HEX,
    WHITE_HEX, GREY_LIGHT_HEX, GREY_DARK_HEX, CYAN_HEX, GREEN_HEX,
)
from ..basic.symbol_lib import BTC_ICONS
from ..basic.keyboard_manager import Layout
from ..stubs.wallet import Wallet


class AddWalletScreen(lv.obj):
    """Dedicated screen for creating or importing a wallet."""

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

        # Title
        title = lv.label(self)
        title.set_text(_tr("SCHN_ADD_WALLET"))
        title.set_style_text_font(theme_font(FONT_TEXT_THEME), 0)
        title.set_style_text_color(theme_color(WHITE_HEX), 0)

        # Import options
        info = lv.label(self)
        info.set_text(_tr("SCHN_WALLET_IMPORT_INFO"))
        info.set_width(lv.pct(100))
        info.set_style_text_font(theme_font(FONT_CAPTION_THEME), 0)
        info.set_style_text_color(theme_color(GREY_LIGHT_HEX), 0)

        self._add_nav_btn(_tr("SCHN_SCAN_DESCRIPTOR"), BTC_ICONS.QR_CODE, "scan")
        self._add_nav_btn(_tr("SCHN_LOAD_FROM_SD"), BTC_ICONS.SD_CARD, "sd_card")

        # Divider
        divider = lv.obj(self)
        divider.set_size(lv.pct(100), 1)
        divider.set_style_bg_color(theme_color(GREY_DARK_HEX), 0)
        divider.set_style_bg_opa(lv.OPA.COVER, 0)
        divider.set_style_border_width(0, 0)

        create_lbl = lv.label(self)
        create_lbl.set_text(_tr("SCHN_CREATE_MANUALLY"))
        create_lbl.set_style_text_font(theme_font(FONT_CAPTION_THEME), 0)
        create_lbl.set_style_text_color(theme_color(GREY_LIGHT_HEX), 0)

        ROW_H = 64

        # Wallet name
        name_row = self._make_row(ROW_H)
        name_lbl = lv.label(name_row)
        name_lbl.set_text(_tr("SCHN_NAME"))
        name_lbl.set_width(lv.pct(25))
        name_lbl.set_style_text_font(theme_font(FONT_TEXT_THEME), 0)
        name_lbl.set_style_text_color(theme_color(WHITE_HEX), 0)

        self.name_ta = lv.textarea(name_row)
        self.name_ta.set_text(_tr("SCHN_WALLET_NAME_PREFIX") + str(urandom.randint(1, 99)))
        self.name_ta.set_width(lv.pct(65))
        self.name_ta.set_height(46)
        self.name_ta.set_style_text_font(theme_font(FONT_TEXT_THEME), 0)
        kb = lambda e: gui.keyboard_manager.bind(self.name_ta, Layout.FULL)
        self.name_ta.add_event_cb(kb, lv.EVENT.CLICKED, None)

        # Multisig toggle
        ms_row = self._make_row(ROW_H)
        ms_lbl = lv.label(ms_row)
        ms_lbl.set_text(_tr("SCHN_MULTISIG"))
        ms_lbl.set_width(lv.pct(50))
        ms_lbl.set_style_text_font(theme_font(FONT_TEXT_THEME), 0)
        ms_lbl.set_style_text_color(theme_color(WHITE_HEX), 0)

        self.ms_sw = lv.switch(ms_row)
        self.ms_sw.set_size(62, 32)
        self.ms_sw.set_style_bg_color(theme_color(CYAN_HEX), lv.PART.INDICATOR | lv.STATE.CHECKED)
        self.ms_sw.add_event_cb(self._on_multisig_toggle, lv.EVENT.VALUE_CHANGED, None)

        # Threshold (hidden until multisig)
        self.thresh_row = self._make_row(ROW_H)
        th_lbl = lv.label(self.thresh_row)
        th_lbl.set_text(_tr("SCHN_THRESHOLD"))
        th_lbl.set_width(lv.pct(50))
        th_lbl.set_style_text_font(theme_font(FONT_TEXT_THEME), 0)
        th_lbl.set_style_text_color(theme_color(WHITE_HEX), 0)

        self.thresh_ta = lv.textarea(self.thresh_row)
        self.thresh_ta.set_text("2")
        self.thresh_ta.set_width(lv.pct(30))
        self.thresh_ta.set_height(46)
        self.thresh_ta.set_accepted_chars("0123456789")
        self.thresh_ta.set_style_text_font(theme_font(FONT_TEXT_THEME), 0)
        self.thresh_row.add_flag(lv.obj.FLAG.HIDDEN)

        # Signers (hidden until multisig)
        self.fp_row = self._make_row(ROW_H)
        fp_lbl = lv.label(self.fp_row)
        fp_lbl.set_text(_tr("SCHN_SIGNERS"))
        fp_lbl.set_width(lv.pct(30))
        fp_lbl.set_style_text_font(theme_font(FONT_SMALL_THEME), 0)
        fp_lbl.set_style_text_color(theme_color(WHITE_HEX), 0)

        self.fp_ta = lv.textarea(self.fp_row)
        state = gui.specter_state
        sig_text = ""
        if state.active_seed:
            sig_text = state.active_seed.fingerprint[:]
            if len(state.loaded_seeds) > 1:
                fps = [s.fingerprint[:] for s in state.loaded_seeds if s.fingerprint != state.active_seed.fingerprint]
                sig_text += "," + fps[0][:]
            else:
                sig_text += ",0xabcd"
        else:
            sig_text = "0x0123,0xabcd"
        self.fp_ta.set_text(sig_text)
        self.fp_ta.set_width(lv.pct(60))
        self.fp_ta.set_height(46)
        self.fp_ta.set_accepted_chars("0123456789abcdefx,")
        self.fp_ta.set_style_text_font(theme_font(FONT_SMALL_THEME), 0)
        self.fp_row.add_flag(lv.obj.FLAG.HIDDEN)

        # Create button
        create_btn = lv.button(self)
        create_btn.set_size(lv.pct(100), ROW_HEIGHT)
        create_btn.set_style_bg_color(theme_color(GREEN_HEX), 0)
        create_btn.set_style_bg_opa(lv.OPA.COVER, 0)
        create_btn.set_style_radius(12, 0)
        create_btn.set_style_border_width(0, 0)
        create_btn.set_style_shadow_width(0, 0)

        btn_lbl = lv.label(create_btn)
        btn_lbl.set_text(_tr("SCHN_CREATE_WALLET"))
        btn_lbl.set_style_text_font(theme_font(FONT_TEXT_THEME), 0)
        btn_lbl.set_style_text_color(theme_color(WHITE_HEX), 0)
        btn_lbl.center()

        create_btn.add_event_cb(self._on_create, lv.EVENT.CLICKED, None)

    def _add_nav_btn(self, text, icon, target):
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

    def _make_row(self, height):
        row = lv.obj(self)
        row.set_size(lv.pct(100), height)
        row.set_style_bg_color(theme_color(BG_CARD_HEX), 0)
        row.set_style_bg_opa(lv.OPA.COVER, 0)
        row.set_style_radius(8, 0)
        row.set_style_border_width(0, 0)
        row.set_style_pad_all(4, 0)
        row.set_style_pad_left(PAD_MD, 0)
        row.set_style_pad_right(PAD_MD, 0)
        row.set_layout(lv.LAYOUT.FLEX)
        row.set_flex_flow(lv.FLEX_FLOW.ROW)
        row.set_flex_align(lv.FLEX_ALIGN.SPACE_BETWEEN, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER)
        row.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
        return row

    def _on_multisig_toggle(self, e):
        if self.ms_sw.has_state(lv.STATE.CHECKED):
            self.thresh_row.remove_flag(lv.obj.FLAG.HIDDEN)
            self.fp_row.remove_flag(lv.obj.FLAG.HIDDEN)
        else:
            self.thresh_row.add_flag(lv.obj.FLAG.HIDDEN)
            self.fp_row.add_flag(lv.obj.FLAG.HIDDEN)

    def _on_create(self, e):
        if e.get_code() != lv.EVENT.CLICKED:
            return

        name = self.name_ta.get_text()
        is_multi = self.ms_sw.has_state(lv.STATE.CHECKED)

        fps = []
        try:
            threshold = int(self.thresh_ta.get_text()) if is_multi else None
        except (ValueError, TypeError):
            threshold = 2 if is_multi else None
        if is_multi:
            raw = self.fp_ta.get_text().strip()
            if raw:
                for fp in raw.split(","):
                    fp = fp.strip()
                    if fp and fp not in fps:
                        fps.append(fp)
        else:
            # Single-sig: use active seed fingerprint
            if self.gui.specter_state.active_seed:
                fps = [self.gui.specter_state.active_seed.fingerprint]

        if is_multi:
            desc = "wsh(sortedmulti(%d,%s))" % (threshold, ",".join(fps))
        else:
            fp0 = fps[0] if fps else "00000000"
            desc = "wpkh([%s/84h/0h/0h]xpub...)" % fp0

        wallet = Wallet(
            label=name,
            descriptor=desc,
            isMultiSig=is_multi,
            net="mainnet",
            required_fingerprints=fps,
            threshold=threshold,
        )
        self.gui.specter_state.register_wallet(wallet)

        self.gui.ui_state.clear_history()
        self.gui.show_menu("main")
