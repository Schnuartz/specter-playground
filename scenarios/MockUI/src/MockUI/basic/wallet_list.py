"""Dashboard wallet list: simple rows with type symbols.
Click → select this wallet (shown bigger + bordered; Receive then shows its
addresses). Long-press → dropdown options.
Grouping with headers is only shown in the Wallet Menu (wrench), not here.
"""
import lvgl as lv
from .templates.specter_gui_base import t as _tr
from .ui_consts import (
    theme_color, theme_font, FONT_TITLE_THEME, FONT_TEXT_THEME, FONT_SMALL_THEME, FONT_CAPTION_THEME,
    WALLET_SECTION_HEIGHT, SCREEN_WIDTH, WALLET_ROW_HEIGHT, WALLET_ROW_HEIGHT_ACTIVE,
    PAD_SM, PAD_MD, PAD_XS,
    BG_BLACK_HEX, BG_CARD_HEX, BG_ELEVATED_HEX,
    WHITE_HEX, GREY_LIGHT_HEX, CYAN_HEX, CYAN_DARK_HEX,
    ORANGE_HEX, GREEN_HEX, GREY_HEX,
)
from .symbol_lib import BTC_ICONS
from ..stubs.wallet import ADDR_NATIVE_SEGWIT, ADDR_LEGACY, ADDR_TAPROOT, ADDR_NESTED_SEGWIT


# Short type symbols for dashboard display
_TYPE_SYMBOLS = {
    # (isMultiSig, address_type, is_standard) → (symbol, color)
}


def _get_type_symbol(wallet):
    """Return (symbol_text, color) for a wallet's type indicator."""
    if not wallet.is_standard():
        return ("MS", theme_color(ORANGE_HEX))  # Miniskript
    if wallet.isMultiSig:
        return None  # use TWO_KEYS icon instead
    if wallet.address_type == ADDR_LEGACY:
        return ("L", theme_color(ORANGE_HEX))
    if wallet.address_type == ADDR_TAPROOT:
        return ("T", theme_color(GREEN_HEX))
    if wallet.address_type == ADDR_NESTED_SEGWIT:
        return ("nS", theme_color(CYAN_HEX))
    # Native Segwit single sig = cleanest, no symbol
    return None


def _wallet_sort_key(wallet):
    sig = 1 if wallet.isMultiSig else 0
    custom = 0 if wallet.is_standard() else 2
    addr_order = {ADDR_NATIVE_SEGWIT: 0, ADDR_NESTED_SEGWIT: 1, ADDR_LEGACY: 2, ADDR_TAPROOT: 3}
    addr = addr_order.get(wallet.address_type, 0)
    return (custom, sig, addr, wallet.account)


class WalletList(lv.obj):
    """Dashboard wallet list. Simple rows with type symbols."""

    def __init__(self, gui, parent=None):
        super().__init__(parent if parent is not None else gui)
        self.gui = gui

        self.set_size(SCREEN_WIDTH, WALLET_SECTION_HEIGHT)
        self.set_style_bg_color(theme_color(BG_BLACK_HEX), 0)
        self.set_style_bg_opa(lv.OPA.COVER, 0)
        self.set_style_border_width(0, 0)
        self.set_style_radius(0, 0)
        self.set_style_pad_left(PAD_MD, 0)
        self.set_style_pad_right(PAD_MD, 0)
        self.set_style_pad_top(PAD_SM, 0)
        self.set_style_pad_bottom(0, 0)

        # Header: "Wallets" + wrench
        header = lv.obj(self)
        header.set_size(SCREEN_WIDTH - 2 * PAD_MD, 28)
        header.set_style_bg_opa(lv.OPA.TRANSP, 0)
        header.set_style_border_width(0, 0)
        header.set_style_pad_all(0, 0)

        title = lv.label(header)
        title.set_text(_tr("SCHN_WALLETS"))
        title.set_style_text_font(theme_font(FONT_TEXT_THEME), 0)
        title.set_style_text_color(theme_color(WHITE_HEX), 0)
        title.align(lv.ALIGN.LEFT_MID, 0, 0)

        wrench_btn = lv.button(header)
        wrench_btn.set_size(40, 40)
        wrench_btn.set_style_bg_opa(lv.OPA.TRANSP, 0)
        wrench_btn.set_style_border_width(0, 0)
        wrench_btn.set_style_shadow_width(0, 0)
        wrench_btn.align(lv.ALIGN.RIGHT_MID, 0, 0)

        wrench_ico = lv.image(wrench_btn)
        BTC_ICONS.EDIT(theme_color(GREY_LIGHT_HEX)).add_to_parent(wrench_ico, zoom=190)
        wrench_ico.center()
        wrench_btn.add_event_cb(self._wrench_cb, lv.EVENT.CLICKED, None)

        # Scrollable rows
        self.wallet_container = lv.obj(self)
        self.wallet_container.set_size(SCREEN_WIDTH - 2 * PAD_MD, WALLET_SECTION_HEIGHT - 36)
        self.wallet_container.set_style_bg_opa(lv.OPA.TRANSP, 0)
        self.wallet_container.set_style_border_width(0, 0)
        self.wallet_container.set_style_pad_all(0, 0)
        self.wallet_container.set_style_pad_row(PAD_MD, 0)
        self.wallet_container.set_layout(lv.LAYOUT.FLEX)
        self.wallet_container.set_flex_flow(lv.FLEX_FLOW.COLUMN)
        self.wallet_container.align_to(header, lv.ALIGN.OUT_BOTTOM_LEFT, 0, PAD_XS)

        self.refresh()

    def refresh(self):
        self.wallet_container.clean()
        state = self.gui.specter_state

        if not state.active_seed:
            lbl = lv.label(self.wallet_container)
            lbl.set_text(_tr("SCHN_LOAD_SEED_FOR_WALLETS"))
            lbl.set_style_text_color(theme_color(GREY_LIGHT_HEX), 0)
            lbl.set_style_text_font(theme_font(FONT_CAPTION_THEME), 0)
            return

        wallets = state.wallets_for_seed(state.active_seed) or []
        others = [w for w in wallets if not w.is_default_wallet()]
        others.sort(key=_wallet_sort_key)

        for w in others:
            self._add_row(w)

    def hint_scroll(self):
        """Briefly scroll down and back up to reveal there's more to see.

        Only plays when the wallet list actually overflows its visible area.
        Called when landing on the dashboard (not on every in-place refresh,
        e.g. selecting a wallet), so it doesn't replay constantly.
        """
        def _peek(timer):
            timer.delete()
            bottom = self.wallet_container.get_scroll_bottom()
            if bottom and bottom > 4:
                self.wallet_container.scroll_to_y(bottom, True)

                def _back(timer2):
                    timer2.delete()
                    self.wallet_container.scroll_to_y(0, True)

                lv.timer_create(_back, 700, None)

        lv.timer_create(_peek, 350, None)

    def _add_row(self, wallet):
        state = self.gui.specter_state
        is_active = state.active_wallet is wallet

        row = lv.button(self.wallet_container)
        row.set_size(lv.pct(100), WALLET_ROW_HEIGHT_ACTIVE if is_active else WALLET_ROW_HEIGHT)
        row.set_style_bg_color(theme_color(BG_ELEVATED_HEX) if is_active else theme_color(BG_CARD_HEX), 0)
        row.set_style_bg_opa(lv.OPA.COVER, 0)
        row.set_style_radius(10, 0)
        row.set_style_shadow_width(0, 0)
        row.set_style_pad_left(PAD_MD, 0)
        row.set_style_pad_right(PAD_MD, 0)

        if is_active:
            row.set_style_border_width(2, 0)
            row.set_style_border_side(lv.BORDER_SIDE.FULL, 0)
            row.set_style_border_color(theme_color(CYAN_HEX), 0)
        else:
            # Left accent bar (not on action buttons) marks these as a
            # distinct, selectable list rather than plain nav buttons.
            row.set_style_border_width(4, 0)
            row.set_style_border_side(lv.BORDER_SIDE.LEFT, 0)
            row.set_style_border_color(theme_color(CYAN_DARK_HEX), 0)

        row.set_layout(lv.LAYOUT.FLEX)
        row.set_flex_flow(lv.FLEX_FLOW.ROW)
        row.set_flex_align(lv.FLEX_ALIGN.START, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER)
        row.set_style_pad_column(PAD_SM, 0)

        # Type symbol
        sym = _get_type_symbol(wallet)
        if wallet.isMultiSig:
            ms_ico = lv.image(row)
            BTC_ICONS.TWO_KEYS(theme_color(ORANGE_HEX)).add_to_parent(ms_ico, zoom=180)
        elif sym:
            sym_lbl = lv.label(row)
            sym_lbl.set_text(sym[0])
            sym_lbl.set_style_text_font(theme_font(FONT_SMALL_THEME), 0)
            sym_lbl.set_style_text_color(sym[1], 0)

        # Account badge
        acc_lbl = lv.label(row)
        acc_lbl.set_text(_tr("SCHN_ACCOUNT_SHORT") + str(wallet.account))
        acc_lbl.set_style_text_font(theme_font(FONT_SMALL_THEME), 0)
        acc_lbl.set_style_text_color(theme_color(CYAN_HEX), 0)

        # Wallet name
        name_lbl = lv.label(row)
        name_lbl.set_text(wallet.label)
        name_lbl.set_style_text_font(theme_font(FONT_TEXT_THEME), 0)
        name_lbl.set_style_text_color(theme_color(WHITE_HEX), 0)
        name_lbl.set_flex_grow(1)

        # Companion app logos (actual icons)
        if wallet.shared_with:
            for i, app in enumerate(wallet.shared_with):
                if i >= 2:
                    break
                app_ico = lv.image(row)
                icon = _get_app_icon(app)
                if icon:
                    icon.add_to_parent(app_ico, zoom=140)

        # Selected indicator
        if is_active:
            check = lv.label(row)
            check.set_text(lv.SYMBOL.OK)
            check.set_style_text_font(theme_font(FONT_TEXT_THEME), 0)
            check.set_style_text_color(theme_color(CYAN_HEX), 0)

        # Click → select this wallet (highlighted here; Receive shows its addresses)
        row.add_event_cb(lambda e, w=wallet: self._select_wallet(w), lv.EVENT.CLICKED, None)
        # Long-press → options (rename / receive / export / delete / details)
        row.add_event_cb(lambda e, w=wallet: self._long_press(w), lv.EVENT.LONG_PRESSED, None)

    def _select_wallet(self, wallet):
        self.gui.specter_state.set_active_wallet(wallet)
        self.refresh()

    def _long_press(self, wallet):
        self.gui.specter_state.set_active_wallet(wallet)
        self.gui.show_menu("wallet_details")

    def _wrench_cb(self, e):
        if e.get_code() == lv.EVENT.CLICKED:
            self.gui.show_menu("wallet_menu")


def _get_app_icon(app_name):
    """Return the BTC_ICONS icon for a companion app, or None."""
    name = app_name.lower()
    if "sparrow" in name:
        return BTC_ICONS.SPARROW
    if "nunchuk" in name:
        return BTC_ICONS.NUNCHUK
    if "keeper" in name:
        return BTC_ICONS.BITCOIN_KEEPER
    if "safe" in name:
        return BTC_ICONS.BITCOIN_SAFE
    if "specter" in name:
        return BTC_ICONS.SPECTER_LOGO_HIGH_QUALITY_KLEINER
    if "electrum" in name:
        return BTC_ICONS.ELECTRUM_LOGO
    # Fallback: generic link icon
    return BTC_ICONS.LINK(theme_color(GREEN_HEX))
