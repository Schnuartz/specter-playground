"""Lock screen with PIN entry."""
import lvgl as lv
from ..basic.templates.specter_gui_base import t as _tr
from ..basic.ui_consts import (
    theme_color, theme_font, FONT_TITLE_THEME, FONT_TEXT_THEME, FONT_SMALL_THEME, FONT_CAPTION_THEME,
    PAD_MD, PAD_SM, PAD_LG, PAD_XL,
    PIN_BTN_HEIGHT, PIN_BTN_WIDTH,
    BG_BLACK_HEX, BG_CARD_HEX, BG_ELEVATED_HEX,
    WHITE_HEX, GREY_LIGHT_HEX, CYAN_HEX, RED_HEX,
)
from ..basic.symbol_lib import BTC_ICONS


class LockedScreen(lv.obj):
    """PIN entry lock screen."""

    def __init__(self, gui, parent):
        super().__init__(parent)
        self.gui = gui
        self._pin_buffer = ""

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

        # Lock icon
        lock_img = lv.image(self)
        BTC_ICONS.LOCK(theme_color(CYAN_HEX)).add_to_parent(lock_img, zoom=300)

        # Title
        title = lv.label(self)
        title.set_text(_tr("SCHN_DEVICE_LOCKED"))
        title.set_style_text_font(theme_font(FONT_TITLE_THEME), 0)
        title.set_style_text_color(theme_color(WHITE_HEX), 0)

        # PIN display
        self.pin_display = lv.label(self)
        self.pin_display.set_text("")
        self.pin_display.set_style_text_font(theme_font(FONT_TITLE_THEME), 0)
        self.pin_display.set_style_text_color(theme_color(CYAN_HEX), 0)
        self.pin_display.set_style_text_letter_space(8, 0)

        # Error label (hidden by default)
        self.error_label = lv.label(self)
        self.error_label.set_text("")
        self.error_label.set_style_text_font(theme_font(FONT_CAPTION_THEME), 0)
        self.error_label.set_style_text_color(theme_color(RED_HEX), 0)

        # PIN pad
        pad = lv.obj(self)
        pad.set_size(3 * (PIN_BTN_WIDTH + PAD_SM) + PAD_SM, 4 * (PIN_BTN_HEIGHT + PAD_SM) + PAD_SM)
        pad.set_style_bg_opa(lv.OPA.TRANSP, 0)
        pad.set_style_border_width(0, 0)
        pad.set_style_pad_all(0, 0)
        pad.set_layout(lv.LAYOUT.FLEX)
        pad.set_flex_flow(lv.FLEX_FLOW.ROW_WRAP)
        pad.set_flex_align(lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER)
        pad.set_style_pad_row(PAD_SM, 0)
        pad.set_style_pad_column(PAD_SM, 0)

        # Number buttons 1-9
        for n in range(1, 10):
            self._add_pin_btn(pad, str(n))

        # Bottom row: clear, 0, OK
        self._add_pin_btn(pad, lv.SYMBOL.BACKSPACE, is_action=True)
        self._add_pin_btn(pad, "0")
        self._add_pin_btn(pad, lv.SYMBOL.OK, is_action=True)

    def _add_pin_btn(self, parent, text, is_action=False):
        btn = lv.button(parent)
        btn.set_size(PIN_BTN_WIDTH, PIN_BTN_HEIGHT)
        btn.set_style_bg_color(theme_color(BG_ELEVATED_HEX) if is_action else theme_color(BG_CARD_HEX), 0)
        btn.set_style_bg_opa(lv.OPA.COVER, 0)
        btn.set_style_radius(8, 0)
        btn.set_style_border_width(0, 0)
        btn.set_style_shadow_width(0, 0)

        lbl = lv.label(btn)
        lbl.set_text(text)
        lbl.set_style_text_font(theme_font(FONT_TEXT_THEME), 0)
        lbl.set_style_text_color(theme_color(WHITE_HEX), 0)
        lbl.center()

        btn.add_event_cb(lambda e, t=text: self._pin_input(t), lv.EVENT.CLICKED, None)

    def _pin_input(self, key):
        if key == lv.SYMBOL.BACKSPACE:
            if self._pin_buffer:
                self._pin_buffer = self._pin_buffer[:-1]
        elif key == lv.SYMBOL.OK:
            self._try_unlock()
            return
        else:
            self._pin_buffer += key

        # Show dots for each digit
        self.pin_display.set_text("*" * len(self._pin_buffer))
        self.error_label.set_text("")

    def _try_unlock(self):
        if self.gui.specter_state.unlock(self._pin_buffer):
            self.gui.show_menu("main")
        else:
            self.error_label.set_text(_tr("SCHN_WRONG_PIN"))
            self._pin_buffer = ""
            self.pin_display.set_text("")
