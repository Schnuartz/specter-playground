"""Connect companion app: select an app, see app-specific options, share wallet.
Each app has its own logo from the companion-apps-specter icon set."""
import lvgl as lv
from ..basic.templates.specter_gui_base import t as _tr
from ..basic.ui_consts import (
    theme_color, theme_font, FONT_TITLE_THEME, FONT_TEXT_THEME, FONT_SMALL_THEME, FONT_CAPTION_THEME,
    PAD_MD, PAD_SM, PAD_LG, ROW_HEIGHT, ROW_ICON_ZOOM,
    BG_BLACK_HEX, BG_CARD_HEX, BG_ELEVATED_HEX,
    WHITE_HEX, GREY_LIGHT_HEX, CYAN_HEX, GREEN_HEX,
)
from ..basic.symbol_lib import BTC_ICONS


# Companion apps with their icon reference and export methods
_COMPANION_APPS = [
    ("Specter Desktop", "specter", ["QR Code", "SD Card"]),
    ("Sparrow", "sparrow", ["QR Code", "SD Card", "USB"]),
    ("Nunchuk", "nunchuk", ["QR Code"]),
    ("Bitcoin Keeper", "keeper", ["QR Code"]),
    ("Bitcoin Safe", "safe", ["QR Code", "SD Card"]),
    ("BlueWallet", "blue", ["QR Code"]),
    ("Electrum", "electrum", ["QR Code", "SD Card"]),
    ("Bull Bitcoin", "bull", ["QR Code"]),
    ("Liana Wallet", "liana", ["QR Code", "SD Card"]),
]


def _get_app_icon(app_key):
    """Return the icon for a companion app key."""
    if app_key == "specter":
        return BTC_ICONS.SPECTER_LOGO_HIGH_QUALITY_KLEINER
    if app_key == "sparrow":
        return BTC_ICONS.SPARROW
    if app_key == "nunchuk":
        return BTC_ICONS.NUNCHUK
    if app_key == "keeper":
        return BTC_ICONS.BITCOIN_KEEPER
    if app_key == "safe":
        return BTC_ICONS.BITCOIN_SAFE
    if app_key == "electrum":
        return BTC_ICONS.ELECTRUM_LOGO
    return BTC_ICONS.LINK(theme_color(CYAN_HEX))


class ConnectAppScreen(lv.obj):
    """Select a companion app to share the wallet with."""

    def __init__(self, gui, parent):
        super().__init__(parent)
        self.gui = gui
        self.wallet = gui.specter_state.active_wallet
        self._sub_screen = None

        self.set_size(lv.pct(100), lv.pct(100))
        self.set_style_bg_color(theme_color(BG_BLACK_HEX), 0)
        self.set_style_bg_opa(lv.OPA.COVER, 0)
        self.set_style_border_width(0, 0)
        self.set_style_radius(0, 0)
        self.set_style_pad_all(PAD_MD, 0)

        self.set_layout(lv.LAYOUT.FLEX)
        self.set_flex_flow(lv.FLEX_FLOW.COLUMN)
        self.set_style_pad_row(PAD_SM, 0)

        title = lv.label(self)
        title.set_text(_tr("SCHN_CONNECT_COMPANION"))
        title.set_style_text_font(theme_font(FONT_TITLE_THEME), 0)
        title.set_style_text_color(theme_color(WHITE_HEX), 0)

        if self.wallet:
            info = lv.label(self)
            info.set_text(_tr("SCHN_SHARE_PREFIX") + self.wallet.label)
            info.set_style_text_font(theme_font(FONT_SMALL_THEME), 0)
            info.set_style_text_color(theme_color(CYAN_HEX), 0)

        for app_name, app_key, methods in _COMPANION_APPS:
            already_shared = self.wallet and app_name in self.wallet.shared_with
            self._add_app_row(app_name, app_key, methods, already_shared)

    def _add_app_row(self, app_name, app_key, methods, already_shared):
        btn = lv.button(self)
        btn.set_size(lv.pct(100), ROW_HEIGHT)
        btn.set_style_bg_color(theme_color(BG_ELEVATED_HEX) if already_shared else theme_color(BG_CARD_HEX), 0)
        btn.set_style_bg_opa(lv.OPA.COVER, 0)
        btn.set_style_radius(10, 0)
        btn.set_style_shadow_width(0, 0)
        if already_shared:
            btn.set_style_border_width(2, 0)
            btn.set_style_border_color(theme_color(GREEN_HEX), 0)
        else:
            btn.set_style_border_width(0, 0)

        btn.set_layout(lv.LAYOUT.FLEX)
        btn.set_flex_flow(lv.FLEX_FLOW.ROW)
        btn.set_flex_align(lv.FLEX_ALIGN.START, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER)
        btn.set_style_pad_column(PAD_SM, 0)
        btn.set_style_pad_left(PAD_MD, 0)

        # App logo
        ico = lv.image(btn)
        app_icon = _get_app_icon(app_key)
        app_icon.add_to_parent(ico, zoom=ROW_ICON_ZOOM)

        # App name
        lbl = lv.label(btn)
        lbl.set_text(app_name)
        lbl.set_style_text_font(theme_font(FONT_TEXT_THEME), 0)
        lbl.set_style_text_color(theme_color(GREEN_HEX) if already_shared else theme_color(WHITE_HEX), 0)
        lbl.set_flex_grow(1)

        if already_shared:
            check = lv.label(btn)
            check.set_text(lv.SYMBOL.OK)
            check.set_style_text_font(theme_font(FONT_TEXT_THEME), 0)
            check.set_style_text_color(theme_color(GREEN_HEX), 0)
        else:
            arrow = lv.label(btn)
            arrow.set_text(lv.SYMBOL.RIGHT)
            arrow.set_style_text_font(theme_font(FONT_SMALL_THEME), 0)
            arrow.set_style_text_color(theme_color(GREY_LIGHT_HEX), 0)

        btn.add_event_cb(
            lambda e, n=app_name, k=app_key, m=methods: self._select_app(n, k, m),
            lv.EVENT.CLICKED, None
        )

    def _select_app(self, app_name, app_key, methods):
        """Show app-specific export options."""
        from ..basic.modal_overlay import ModalOverlay

        self._sub_screen = ModalOverlay(bg_opa=200)
        overlay = self._sub_screen.overlay

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

        # App logo + name header
        hdr = lv.obj(dialog)
        hdr.set_size(lv.pct(100), 48)
        hdr.set_style_bg_opa(lv.OPA.TRANSP, 0)
        hdr.set_style_border_width(0, 0)
        hdr.set_style_pad_all(0, 0)
        hdr.set_layout(lv.LAYOUT.FLEX)
        hdr.set_flex_flow(lv.FLEX_FLOW.ROW)
        hdr.set_flex_align(lv.FLEX_ALIGN.START, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER)
        hdr.set_style_pad_column(PAD_SM, 0)

        logo = lv.image(hdr)
        _get_app_icon(app_key).add_to_parent(logo, zoom=190)

        name = lv.label(hdr)
        name.set_text(app_name)
        name.set_style_text_font(theme_font(FONT_TEXT_THEME), 0)
        name.set_style_text_color(theme_color(WHITE_HEX), 0)

        # Export method options
        for method in methods:
            m_btn = lv.button(dialog)
            m_btn.set_size(lv.pct(100), 52)
            m_btn.set_style_bg_color(theme_color(BG_ELEVATED_HEX), 0)
            m_btn.set_style_bg_opa(lv.OPA.COVER, 0)
            m_btn.set_style_radius(8, 0)
            m_btn.set_style_border_width(0, 0)
            m_btn.set_style_shadow_width(0, 0)

            m_btn.set_layout(lv.LAYOUT.FLEX)
            m_btn.set_flex_flow(lv.FLEX_FLOW.ROW)
            m_btn.set_flex_align(lv.FLEX_ALIGN.START, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER)
            m_btn.set_style_pad_column(PAD_SM, 0)
            m_btn.set_style_pad_left(PAD_SM, 0)

            if method == "QR Code":
                m_ico = lv.image(m_btn)
                BTC_ICONS.QR_CODE(theme_color(CYAN_HEX)).add_to_parent(m_ico, zoom=150)
            elif method == "SD Card":
                m_ico = lv.image(m_btn)
                BTC_ICONS.SD_CARD(theme_color(CYAN_HEX)).add_to_parent(m_ico, zoom=150)
            elif method == "USB":
                m_ico = lv.image(m_btn)
                BTC_ICONS.USB(theme_color(CYAN_HEX)).add_to_parent(m_ico, zoom=150)

            m_lbl = lv.label(m_btn)
            m_lbl.set_text(_tr("SCHN_EXPORT_VIA_PREFIX") + method)
            m_lbl.set_style_text_font(theme_font(FONT_SMALL_THEME), 0)
            m_lbl.set_style_text_color(theme_color(WHITE_HEX), 0)

            m_btn.add_event_cb(
                lambda e, n=app_name: self._confirm_share(n),
                lv.EVENT.CLICKED, None
            )

        # Cancel
        cancel = lv.button(dialog)
        cancel.set_size(lv.pct(100), 48)
        cancel.set_style_bg_color(theme_color(BG_CARD_HEX), 0)
        cancel.set_style_bg_opa(lv.OPA.COVER, 0)
        cancel.set_style_radius(8, 0)
        cancel.set_style_border_width(0, 0)
        cancel.set_style_shadow_width(0, 0)
        c_lbl = lv.label(cancel)
        c_lbl.set_text(_tr("SCHN_CANCEL"))
        c_lbl.set_style_text_font(theme_font(FONT_SMALL_THEME), 0)
        c_lbl.set_style_text_color(theme_color(GREY_LIGHT_HEX), 0)
        c_lbl.center()
        cancel.add_event_cb(lambda e: self._close_sub(), lv.EVENT.CLICKED, None)

    def _confirm_share(self, app_name):
        if self.wallet:
            self.wallet.mark_shared(app_name)
        self._close_sub()
        # Refresh to show checkmark
        self.gui.show_menu("connect_app")

    def _close_sub(self):
        if self._sub_screen:
            self._sub_screen.close()
            self._sub_screen = None
