"""Device wipe confirmation screen."""
import lvgl as lv
from ..basic.templates.specter_gui_base import t as _tr
from ..basic.ui_consts import (
    theme_color, theme_font, FONT_TITLE_THEME, FONT_TEXT_THEME, FONT_SMALL_THEME, FONT_CAPTION_THEME,
    PAD_MD, PAD_LG, PAD_XL,
    BG_BLACK_HEX, BG_CARD_HEX,
    WHITE_HEX, GREY_LIGHT_HEX, RED_HEX, CYAN_HEX,
)
from ..basic.symbol_lib import BTC_ICONS


class ConfirmWipeScreen(lv.obj):
    """Confirmation screen before wiping the device."""

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
        self.set_flex_align(lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER)
        self.set_style_pad_row(PAD_LG, 0)

        # Warning icon
        ico = lv.image(self)
        BTC_ICONS.ALERT(theme_color(RED_HEX)).add_to_parent(ico, zoom=350)

        title = lv.label(self)
        title.set_text(_tr("SCHN_WIPE_DEVICE_QUESTION"))
        title.set_style_text_font(theme_font(FONT_TITLE_THEME), 0)
        title.set_style_text_color(theme_color(RED_HEX), 0)

        warn = lv.label(self)
        warn.set_text(_tr("SCHN_WIPE_WARNING"))
        warn.set_width(lv.pct(85))
        warn.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
        warn.set_style_text_font(theme_font(FONT_SMALL_THEME), 0)
        warn.set_style_text_color(theme_color(WHITE_HEX), 0)

        # Confirm button
        confirm_btn = lv.button(self)
        confirm_btn.set_size(lv.pct(100), 56)
        confirm_btn.set_style_bg_color(theme_color(RED_HEX), 0)
        confirm_btn.set_style_bg_opa(lv.OPA.COVER, 0)
        confirm_btn.set_style_radius(12, 0)
        confirm_btn.set_style_border_width(0, 0)
        confirm_btn.set_style_shadow_width(0, 0)

        confirm_lbl = lv.label(confirm_btn)
        confirm_lbl.set_text(_tr("SCHN_CONFIRM_WIPE"))
        confirm_lbl.set_style_text_font(theme_font(FONT_TEXT_THEME), 0)
        confirm_lbl.set_style_text_color(theme_color(WHITE_HEX), 0)
        confirm_lbl.center()

        confirm_btn.add_event_cb(self._wipe, lv.EVENT.CLICKED, None)

        # Cancel button
        cancel_btn = lv.button(self)
        cancel_btn.set_size(lv.pct(100), 48)
        cancel_btn.set_style_bg_color(theme_color(BG_CARD_HEX), 0)
        cancel_btn.set_style_bg_opa(lv.OPA.COVER, 0)
        cancel_btn.set_style_radius(12, 0)
        cancel_btn.set_style_border_width(0, 0)
        cancel_btn.set_style_shadow_width(0, 0)

        cancel_lbl = lv.label(cancel_btn)
        cancel_lbl.set_text(_tr("SCHN_CANCEL"))
        cancel_lbl.set_style_text_font(theme_font(FONT_TEXT_THEME), 0)
        cancel_lbl.set_style_text_color(theme_color(CYAN_HEX), 0)
        cancel_lbl.center()

        cancel_btn.add_event_cb(lambda e: gui.show_menu(None), lv.EVENT.CLICKED, None)

    def _wipe(self, e):
        if e.get_code() != lv.EVENT.CLICKED:
            return
        state = self.gui.specter_state
        state.loaded_seeds.clear()
        state.active_seed = None
        state.registered_wallets.clear()
        state.active_wallet = None
        state.pin = None
        state.is_locked = False
        self.gui.ui_state.clear_history()
        self.gui.show_menu("main")
