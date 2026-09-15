"""Wallet Menu: full-screen with structured wallet grouping.
Heading = Wallet Type (Single Sig / Multi Sig / Miniskript)
Subheading = Address Type (Native Segwit / Legacy / Taproot)
Includes seed dropdown at top. Long-press for options including delete."""
import lvgl as lv
from ..basic.templates.specter_gui_base import t as _tr
from ..basic.ui_consts import (
    theme_color, theme_font, FONT_TITLE_THEME, FONT_TEXT_THEME, FONT_SMALL_THEME, FONT_CAPTION_THEME,
    PAD_MD, PAD_SM, PAD_LG, PAD_XS,
    BG_BLACK_HEX, BG_CARD_HEX, BG_ELEVATED_HEX,
    WHITE_HEX, GREY_LIGHT_HEX, GREY_DARK_HEX, CYAN_HEX, CYAN_DARK_HEX,
    RED_HEX, GREEN_HEX, ORANGE_HEX,
    WALLET_ROW_HEIGHT, WALLET_ROW_HEIGHT_ACTIVE,
)
from ..basic.symbol_lib import BTC_ICONS
from ..basic.modal_overlay import ModalOverlay
from ..basic.seed_dropdown import SeedDropdown
from ..stubs.wallet import ADDR_NATIVE_SEGWIT, ADDR_LEGACY, ADDR_TAPROOT, ADDR_NESTED_SEGWIT


_ADDR_NAME_KEYS = {
    ADDR_NATIVE_SEGWIT: "SCHN_NATIVE_SEGWIT",
    ADDR_NESTED_SEGWIT: "SCHN_NESTED_SEGWIT",
    ADDR_LEGACY: "SCHN_LEGACY",
    ADDR_TAPROOT: "SCHN_TAPROOT",
}
_ADDR_ORDER = {ADDR_NATIVE_SEGWIT: 0, ADDR_NESTED_SEGWIT: 1, ADDR_LEGACY: 2, ADDR_TAPROOT: 3}


def _build_grouped(wallets):
    """Build hierarchy: Wallet Type → Address Type → wallets.
    Returns [(type_heading, [(addr_heading, [wallets])])]"""
    # Separate by wallet type
    singlesig = []
    multisig = []
    miniskript = []
    for w in wallets:
        if w.is_default_wallet():
            continue
        if not w.is_standard():
            miniskript.append(w)
        elif w.isMultiSig:
            multisig.append(w)
        else:
            singlesig.append(w)

    result = []

    # Single Sig group
    if singlesig:
        addr_groups = {}
        for w in singlesig:
            at = w.address_type or ADDR_NATIVE_SEGWIT
            if at not in addr_groups:
                addr_groups[at] = []
            addr_groups[at].append(w)
        for at in addr_groups:
            addr_groups[at].sort(key=lambda w: w.account)
        sub = []
        for at in sorted(addr_groups.keys(), key=lambda t: _ADDR_ORDER.get(t, 99)):
            sub.append((_tr(_ADDR_NAME_KEYS.get(at, "SCHN_OTHER")), addr_groups[at]))
        result.append((_tr("COMMON_SINGLESIG"), sub))

    # Multi Sig group
    if multisig:
        addr_groups = {}
        for w in multisig:
            at = w.address_type or ADDR_NATIVE_SEGWIT
            if at not in addr_groups:
                addr_groups[at] = []
            addr_groups[at].append(w)
        for at in addr_groups:
            addr_groups[at].sort(key=lambda w: w.account)
        sub = []
        for at in sorted(addr_groups.keys(), key=lambda t: _ADDR_ORDER.get(t, 99)):
            label = _tr(_ADDR_NAME_KEYS.get(at, "SCHN_OTHER"))
            for w in addr_groups[at]:
                if w.threshold:
                    label = str(w.threshold) + "/" + str(len(w.required_fingerprints)) + " " + label
                    break
            sub.append((label, addr_groups[at]))
        result.append((_tr("COMMON_MULTISIG"), sub))

    # Miniskript group
    if miniskript:
        result.append((_tr("COMMON_MINISCRIPT"), [(_tr("ADD_WALLET_CUSTOM"), miniskript)]))

    return result


class WalletMenu(lv.obj):
    """Full wallet management with type heading / address subheading structure."""

    def __init__(self, gui, parent):
        super().__init__(parent)
        self.gui = gui
        self._modal = None

        self.set_size(lv.pct(100), lv.pct(100))
        self.set_style_bg_color(theme_color(BG_BLACK_HEX), 0)
        self.set_style_bg_opa(lv.OPA.COVER, 0)
        self.set_style_border_width(0, 0)
        self.set_style_radius(0, 0)
        self.set_style_pad_all(PAD_MD, 0)
        self.set_layout(lv.LAYOUT.FLEX)
        self.set_flex_flow(lv.FLEX_FLOW.COLUMN)
        self.set_style_pad_row(PAD_SM, 0)

        state = gui.specter_state

        # "Wallets from main seed" caption + the SAME interactive seed dropdown
        # used on the main dashboard (tap to switch seeds without leaving this screen).
        caption = lv.label(self)
        caption.set_text(_tr("SCHN_WALLETS_MAIN_SEED"))
        caption.set_style_text_font(theme_font(FONT_TEXT_THEME), 0)
        caption.set_style_text_color(theme_color(GREY_LIGHT_HEX), 0)

        self.seed_dropdown = SeedDropdown(gui, parent=self, on_change=self._build_wallets)

        # Container for the grouped wallet list, rebuilt whenever the seed changes.
        self._list = lv.obj(self)
        self._list.set_size(lv.pct(100), lv.SIZE_CONTENT)
        self._list.set_style_bg_opa(lv.OPA.TRANSP, 0)
        self._list.set_style_border_width(0, 0)
        self._list.set_style_pad_all(0, 0)
        self._list.set_style_pad_row(PAD_XS, 0)
        self._list.set_layout(lv.LAYOUT.FLEX)
        self._list.set_flex_flow(lv.FLEX_FLOW.COLUMN)

        self._build_wallets()

    def _build_wallets(self):
        state = self.gui.specter_state
        self._list.clean()

        wallets = state.wallets_for_seed(state.active_seed) or state.registered_wallets
        groups = _build_grouped(wallets)

        if not groups:
            empty = lv.label(self._list)
            empty.set_text(_tr("SCHN_NO_WALLETS"))
            empty.set_style_text_color(theme_color(GREY_LIGHT_HEX), 0)
            return

        for type_heading, addr_groups in groups:
            # === TYPE HEADING (big) ===
            th = lv.label(self._list)
            th.set_text(type_heading)
            th.set_style_text_font(theme_font(FONT_TITLE_THEME), 0)
            th.set_style_text_color(theme_color(WHITE_HEX), 0)

            for addr_heading, group_wallets in addr_groups:
                # === ADDRESS SUBHEADING ===
                ah = lv.label(self._list)
                ah.set_text(addr_heading)
                ah.set_style_text_font(theme_font(FONT_TEXT_THEME), 0)
                ah.set_style_text_color(theme_color(GREY_LIGHT_HEX), 0)

                for w in group_wallets:
                    self._add_wallet_row(w)

    def _add_wallet_row(self, wallet):
        state = self.gui.specter_state
        is_active = state.active_wallet is wallet

        row = lv.button(self._list)
        row.set_size(lv.pct(100), WALLET_ROW_HEIGHT_ACTIVE if is_active else WALLET_ROW_HEIGHT)
        row.set_style_bg_color(theme_color(BG_ELEVATED_HEX) if is_active else theme_color(BG_CARD_HEX), 0)
        row.set_style_bg_opa(lv.OPA.COVER, 0)
        row.set_style_radius(10, 0)
        row.set_style_shadow_width(0, 0)
        row.set_style_pad_left(PAD_MD, 0)
        row.set_style_pad_right(PAD_SM, 0)
        if is_active:
            row.set_style_border_width(2, 0)
            row.set_style_border_side(lv.BORDER_SIDE.FULL, 0)
            row.set_style_border_color(theme_color(CYAN_HEX), 0)
        else:
            # Left accent bar marks these as a distinct, selectable list
            # rather than plain nav buttons (same treatment as the dashboard).
            row.set_style_border_width(4, 0)
            row.set_style_border_side(lv.BORDER_SIDE.LEFT, 0)
            row.set_style_border_color(theme_color(CYAN_DARK_HEX), 0)

        row.set_layout(lv.LAYOUT.FLEX)
        row.set_flex_flow(lv.FLEX_FLOW.ROW)
        row.set_flex_align(lv.FLEX_ALIGN.START, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER)
        row.set_style_pad_column(PAD_SM, 0)

        # Account
        acc = lv.label(row)
        acc.set_text(_tr("SCHN_ACCOUNT_SHORT") + str(wallet.account))
        acc.set_style_text_font(theme_font(FONT_SMALL_THEME), 0)
        acc.set_style_text_color(theme_color(CYAN_HEX), 0)

        # Name
        name = lv.label(row)
        name.set_text(wallet.label)
        name.set_style_text_font(theme_font(FONT_TEXT_THEME), 0)
        name.set_style_text_color(theme_color(WHITE_HEX), 0)
        name.set_flex_grow(1)

        # Companion app logos (bigger)
        if wallet.shared_with:
            from ..basic.wallet_list import _get_app_icon
            for i, app in enumerate(wallet.shared_with[:3]):
                app_ico = lv.image(row)
                icon = _get_app_icon(app)
                if icon:
                    icon.add_to_parent(app_ico, zoom=140)

        # Click → wallet info
        row.add_event_cb(lambda e, w=wallet: self._open_wallet(w), lv.EVENT.CLICKED, None)
        # Long-press → options dropdown
        row.add_event_cb(lambda e, w=wallet: self._long_press(w), lv.EVENT.LONG_PRESSED, None)

    def _open_wallet(self, wallet):
        self.gui.specter_state.set_active_wallet(wallet)
        self.gui.show_menu("wallet_info")

    def _long_press(self, wallet):
        self._modal = ModalOverlay(bg_opa=200)
        overlay = self._modal.overlay

        dialog = lv.obj(overlay)
        dialog.set_size(360, lv.SIZE_CONTENT)
        dialog.set_style_bg_color(theme_color(BG_CARD_HEX), 0)
        dialog.set_style_bg_opa(lv.OPA.COVER, 0)
        dialog.set_style_radius(12, 0)
        dialog.set_style_border_width(0, 0)
        dialog.set_style_pad_all(PAD_MD, 0)
        dialog.set_style_pad_row(PAD_SM, 0)
        dialog.center()
        dialog.set_layout(lv.LAYOUT.FLEX)
        dialog.set_flex_flow(lv.FLEX_FLOW.COLUMN)

        title = lv.label(dialog)
        title.set_text(wallet.label)
        title.set_style_text_font(theme_font(FONT_SMALL_THEME), 0)
        title.set_style_text_color(theme_color(WHITE_HEX), 0)

        self._dd_opt(dialog, _tr("SCHN_WALLET_DETAILS"), lambda: self._nav(wallet, "wallet_info"))
        self._dd_opt(dialog, _tr("SCHN_RECEIVE_ADDRESSES"), lambda: self._nav(wallet, "receive"))
        self._dd_opt(dialog, _tr("SCHN_EXPORT_WALLET"), lambda: self._nav(wallet, "export"))
        self._dd_opt(dialog, _tr("SCHN_CONNECT_COMPANION"), lambda: self._nav(wallet, "connect_app"))
        if not wallet.is_default_wallet():
            self._dd_opt(dialog, _tr("SCHN_DELETE_WALLET"), lambda: self._delete(wallet), color=theme_color(RED_HEX))
        self._dd_opt(dialog, _tr("SCHN_CANCEL"), self._close_modal, color=theme_color(GREY_LIGHT_HEX))

    def _dd_opt(self, parent, text, callback, color=None):
        btn = lv.button(parent)
        btn.set_size(lv.pct(100), 40)
        btn.set_style_bg_color(theme_color(BG_ELEVATED_HEX), 0)
        btn.set_style_bg_opa(lv.OPA.COVER, 0)
        btn.set_style_radius(6, 0)
        btn.set_style_border_width(0, 0)
        btn.set_style_shadow_width(0, 0)
        lbl = lv.label(btn)
        lbl.set_text(text)
        lbl.set_style_text_font(theme_font(FONT_SMALL_THEME), 0)
        lbl.set_style_text_color(color if color else theme_color(WHITE_HEX), 0)
        lbl.center()
        btn.add_event_cb(lambda e: callback(), lv.EVENT.CLICKED, None)

    def _nav(self, wallet, target):
        self._close_modal()
        self.gui.specter_state.set_active_wallet(wallet)
        self.gui.show_menu(target)

    def _delete(self, wallet):
        self._close_modal()
        self._modal = ModalOverlay(bg_opa=200)
        d = lv.obj(self._modal.overlay)
        d.set_size(340, 180)
        d.set_style_bg_color(theme_color(BG_CARD_HEX), 0)
        d.set_style_bg_opa(lv.OPA.COVER, 0)
        d.set_style_radius(12, 0)
        d.set_style_border_width(0, 0)
        d.set_style_pad_all(PAD_MD, 0)
        d.set_style_pad_row(PAD_SM, 0)
        d.center()
        d.set_layout(lv.LAYOUT.FLEX)
        d.set_flex_flow(lv.FLEX_FLOW.COLUMN)
        d.set_flex_align(lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER)

        t = lv.label(d)
        t.set_text(_tr("SCHN_DELETE_PREFIX") + "\"" + wallet.label + "\"?")
        t.set_style_text_font(theme_font(FONT_SMALL_THEME), 0)
        t.set_style_text_color(theme_color(WHITE_HEX), 0)

        db = lv.button(d)
        db.set_size(lv.pct(100), 44)
        db.set_style_bg_color(theme_color(RED_HEX), 0)
        db.set_style_radius(8, 0)
        db.set_style_border_width(0, 0)
        db.set_style_shadow_width(0, 0)
        dl = lv.label(db)
        dl.set_text(_tr("SCHN_DELETE"))
        dl.set_style_text_color(theme_color(WHITE_HEX), 0)
        dl.center()
        db.add_event_cb(lambda e, w=wallet: self._confirm_del(w), lv.EVENT.CLICKED, None)

        cb = lv.button(d)
        cb.set_size(lv.pct(100), 38)
        cb.set_style_bg_color(theme_color(BG_ELEVATED_HEX), 0)
        cb.set_style_radius(8, 0)
        cb.set_style_border_width(0, 0)
        cb.set_style_shadow_width(0, 0)
        cl = lv.label(cb)
        cl.set_text(_tr("SCHN_CANCEL"))
        cl.set_style_text_color(theme_color(GREY_LIGHT_HEX), 0)
        cl.center()
        cb.add_event_cb(lambda e: self._close_modal(), lv.EVENT.CLICKED, None)

    def _confirm_del(self, wallet):
        self._close_modal()
        self.gui.specter_state.remove_wallet(wallet)
        self.gui.show_menu("wallet_menu")

    def _close_modal(self):
        if self._modal:
            self._modal.close()
            self._modal = None
