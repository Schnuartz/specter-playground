"""Settings menu (hamburger): completely independent page.
Interface icons at top, unique settings below. No wallets/seeds shown."""
import lvgl as lv
from ..basic.templates.specter_gui_base import t as _tr
from ..basic.ui_consts import (
    theme_color, theme_font, FONT_TITLE_THEME, FONT_TEXT_THEME, FONT_SMALL_THEME, FONT_CAPTION_THEME,
    SCREEN_WIDTH, PAD_MD, PAD_SM, PAD_LG,
    BG_BLACK_HEX, BG_CARD_HEX, BG_ELEVATED_HEX,
    WHITE_HEX, GREY_LIGHT_HEX, CYAN_HEX, GREEN_HEX, GREY_HEX,
)
from ..basic.symbol_lib import BTC_ICONS


class SettingsMenu(lv.obj):
    """Full independent settings page with interface status at top."""

    def __init__(self, gui, parent):
        super().__init__(parent)
        self.gui = gui
        state = gui.specter_state

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
        title.set_text(_tr("SCHN_SETTINGS"))
        title.set_style_text_font(theme_font(FONT_TITLE_THEME), 0)
        title.set_style_text_color(theme_color(WHITE_HEX), 0)

        # === Interface Status Bar (moved from old top bar) ===
        iface_card = lv.obj(self)
        iface_card.set_size(lv.pct(100), 84)
        iface_card.set_style_bg_color(theme_color(BG_CARD_HEX), 0)
        iface_card.set_style_bg_opa(lv.OPA.COVER, 0)
        iface_card.set_style_radius(10, 0)
        iface_card.set_style_border_width(0, 0)
        iface_card.set_style_pad_all(PAD_SM, 0)
        iface_card.set_layout(lv.LAYOUT.FLEX)
        iface_card.set_flex_flow(lv.FLEX_FLOW.ROW)
        iface_card.set_flex_align(lv.FLEX_ALIGN.SPACE_EVENLY, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER)

        # QR Scanner
        if state.hasQR():
            self._add_iface_icon(iface_card, BTC_ICONS.QR_CODE, "QR",
                                 state.QR_enabled(), "interfaces")
        # USB
        if state.hasUSB():
            self._add_iface_icon(iface_card, BTC_ICONS.USB, "USB",
                                 state.USB_enabled(), "interfaces")
        # SD Card
        if state.hasSD():
            color = theme_color(GREEN_HEX) if state.SD_detected() else (theme_color(WHITE_HEX) if state.SD_enabled() else theme_color(GREY_HEX))
            self._add_iface_icon_colored(iface_card, BTC_ICONS.SD_CARD, "SD", color, "interfaces")
        # SmartCard
        if state.hasSmartCard():
            color = theme_color(GREEN_HEX) if state.SmartCard_detected() else (theme_color(WHITE_HEX) if state.SmartCard_enabled() else theme_color(GREY_HEX))
            self._add_iface_icon_colored(iface_card, BTC_ICONS.SMARTCARD, "SC", color, "interfaces")

        # === Settings Menu Items (unique to this menu) ===

        # Device section
        section_lbl = lv.label(self)
        section_lbl.set_text(_tr("SCHN_DEVICE"))
        section_lbl.set_style_text_font(theme_font(FONT_TEXT_THEME), 0)
        section_lbl.set_style_text_color(theme_color(GREY_LIGHT_HEX), 0)

        self._add_toggle_row(_tr("SCHN_POWER"), state.battery_pct is not None, self._power_cb)
        self._add_toggle_row(_tr("SCHN_LOCK_DEVICE"), state.is_locked, self._lock_cb)
        self._add_nav_item(_tr("SCHN_MANAGE_INTERFACES"), BTC_ICONS.USB, "interfaces")
        self._add_nav_item(_tr("SCHN_LANGUAGE"), BTC_ICONS.GLOBE, "language_settings")
        self._add_nav_item(_tr("SCHN_THEME"), BTC_ICONS.BRUSH, "theme_settings")

        # Security: grouped as its own submenu (backup/restore, firmware info,
        # wipe device), matching the section layout of the upstream
        # specter-playground Settings page.
        sec_lbl = lv.label(self)
        sec_lbl.set_text(_tr("SCHN_SECURITY"))
        sec_lbl.set_style_text_font(theme_font(FONT_TEXT_THEME), 0)
        sec_lbl.set_style_text_color(theme_color(GREY_LIGHT_HEX), 0)

        self._add_nav_item(_tr("SCHN_SECURITY_SETTINGS"), BTC_ICONS.SAFE, "security_settings")

    def _add_iface_icon(self, parent, icon, label, enabled, target):
        color = theme_color(GREEN_HEX) if enabled else theme_color(GREY_HEX)
        self._add_iface_icon_colored(parent, icon, label, color, target)

    def _add_iface_icon_colored(self, parent, icon, label, color, target):
        btn = lv.button(parent)
        btn.set_size(lv.SIZE_CONTENT, 68)
        btn.set_style_bg_opa(lv.OPA.TRANSP, 0)
        btn.set_style_border_width(0, 0)
        btn.set_style_shadow_width(0, 0)
        btn.set_style_pad_all(4, 0)

        btn.set_layout(lv.LAYOUT.FLEX)
        btn.set_flex_flow(lv.FLEX_FLOW.COLUMN)
        btn.set_flex_align(lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER)

        ico = lv.image(btn)
        icon(color).add_to_parent(ico, zoom=220)

        lbl = lv.label(btn)
        lbl.set_text(label)
        lbl.set_style_text_font(theme_font(FONT_SMALL_THEME), 0)
        lbl.set_style_text_color(color, 0)

        btn.add_event_cb(lambda e, t=target: self.gui.show_menu(t), lv.EVENT.CLICKED, None)

    def _add_toggle_row(self, text, initial_state, callback):
        row = lv.obj(self)
        row.set_size(lv.pct(100), 60)
        row.set_style_bg_color(theme_color(BG_CARD_HEX), 0)
        row.set_style_bg_opa(lv.OPA.COVER, 0)
        row.set_style_radius(10, 0)
        row.set_style_border_width(0, 0)
        row.set_style_pad_left(PAD_MD, 0)
        row.set_style_pad_right(PAD_MD, 0)

        lbl = lv.label(row)
        lbl.set_text(text)
        lbl.set_style_text_font(theme_font(FONT_TEXT_THEME), 0)
        lbl.set_style_text_color(theme_color(WHITE_HEX), 0)
        lbl.align(lv.ALIGN.LEFT_MID, 0, 0)

        sw = lv.switch(row)
        sw.set_size(62, 32)
        sw.align(lv.ALIGN.RIGHT_MID, 0, 0)
        if initial_state:
            sw.add_state(lv.STATE.CHECKED)
        sw.set_style_bg_color(theme_color(CYAN_HEX), lv.PART.INDICATOR | lv.STATE.CHECKED)
        sw.add_event_cb(callback, lv.EVENT.VALUE_CHANGED, None)

    def _add_nav_item(self, text, icon, target, color=None):
        btn = lv.button(self)
        btn.set_size(lv.pct(100), 60)
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
        txt_color = color if color else theme_color(WHITE_HEX)
        icon(txt_color).add_to_parent(ico, zoom=150)

        lbl = lv.label(btn)
        lbl.set_text(text)
        lbl.set_style_text_font(theme_font(FONT_TEXT_THEME), 0)
        lbl.set_style_text_color(txt_color, 0)
        lbl.set_flex_grow(1)

        arrow = lv.label(btn)
        arrow.set_text(lv.SYMBOL.RIGHT)
        arrow.set_style_text_color(theme_color(GREY_LIGHT_HEX), 0)

        btn.add_event_cb(lambda e, t=target: self.gui.show_menu(t), lv.EVENT.CLICKED, None)

    def _power_cb(self, e):
        if e.get_code() == lv.EVENT.VALUE_CHANGED:
            sw = e.get_target_obj()
            if sw.has_state(lv.STATE.CHECKED):
                self.gui.specter_state.battery_pct = 100
            else:
                self.gui.specter_state.battery_pct = None
            self.gui.refresh_ui()

    def _lock_cb(self, e):
        if e.get_code() == lv.EVENT.VALUE_CHANGED:
            sw = e.get_target_obj()
            if sw.has_state(lv.STATE.CHECKED):
                self.gui.specter_state.lock()
                self.gui.show_menu(None)
