"""MemoryCard management using Specter-DIY's real secure applet protocol."""

import lvgl as lv

from ..basic.utils.keyboard_manager import Layout
from ..basic.ui_consts import (
    theme_color, theme_font, FONT_TITLE_THEME, FONT_TEXT_THEME, FONT_SMALL_THEME,
    PAD_MD, PAD_SM, BG_BLACK_HEX, BG_CARD_HEX, WHITE_HEX, GREY_LIGHT_HEX,
    CYAN_HEX, GREEN_HEX, RED_HEX,
)
from ..stubs.seed import Seed


class SmartcardScreen(lv.obj):
    def __init__(self, gui, parent):
        super().__init__(parent)
        self.gui = gui
        self.storage = gui.specter_state.storage
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
        title.set_text("Smartcard storage")
        title.set_style_text_font(theme_font(FONT_TITLE_THEME), 0)
        title.set_style_text_color(theme_color(WHITE_HEX), 0)

        self.message = lv.label(self)
        self.message.set_width(lv.pct(100))
        self.message.set_style_text_font(theme_font(FONT_SMALL_THEME), 0)
        self.message.set_style_text_color(theme_color(GREY_LIGHT_HEX), 0)

        if not self.storage.card_present():
            self.message.set_text("Please insert a Specter MemoryCard")
            return

        try:
            status = self.storage.card_status()
            if status["pin_set"]:
                detail = "Card %s · PIN locked · %d/%d attempts" % (
                    status["fingerprint"], status["attempts"], status["attempts_max"])
            else:
                detail = "Blank card %s · choose a PIN before saving" % status["fingerprint"]
            self.message.set_text(detail)
        except Exception as exc:
            self.message.set_text(str(exc))
            self.message.set_style_text_color(theme_color(RED_HEX), 0)
            return

        pin_row = lv.obj(self)
        pin_row.set_size(lv.pct(100), 54)
        pin_row.set_style_bg_opa(lv.OPA.TRANSP, 0)
        pin_row.set_style_border_width(0, 0)
        pin_row.set_style_pad_all(0, 0)
        pin_row.set_layout(lv.LAYOUT.FLEX)
        pin_row.set_flex_flow(lv.FLEX_FLOW.ROW)
        pin_row.set_style_pad_column(PAD_SM, 0)
        pin_label = lv.label(pin_row)
        pin_label.set_text("PIN")
        pin_label.set_style_text_font(theme_font(FONT_TEXT_THEME), 0)
        pin_label.set_style_text_color(theme_color(WHITE_HEX), 0)
        self.pin = lv.textarea(pin_row)
        self.pin.set_one_line(True)
        self.pin.set_password_mode(True)
        self.pin.set_accepted_chars("0123456789")
        self.pin.set_max_length(32)
        self.pin.set_flex_grow(1)
        self.pin.set_height(48)
        self.pin.add_event_cb(lambda event: gui.keyboard_manager.bind(self.pin, Layout.NUMBER),
                              lv.EVENT.CLICKED, None)

        portable_row = lv.obj(self)
        portable_row.set_size(lv.pct(100), 44)
        portable_row.set_style_bg_color(theme_color(BG_CARD_HEX), 0)
        portable_row.set_style_bg_opa(lv.OPA.COVER, 0)
        portable_row.set_style_border_width(0, 0)
        portable_row.set_style_radius(8, 0)
        portable_row.set_layout(lv.LAYOUT.FLEX)
        portable_row.set_flex_flow(lv.FLEX_FLOW.ROW)
        portable_row.set_flex_align(lv.FLEX_ALIGN.SPACE_BETWEEN, lv.FLEX_ALIGN.CENTER,
                                    lv.FLEX_ALIGN.CENTER)
        portable_text = lv.label(portable_row)
        portable_text.set_text("Portable plaintext after PIN")
        portable_text.set_style_text_font(theme_font(FONT_SMALL_THEME), 0)
        portable_text.set_style_text_color(theme_color(WHITE_HEX), 0)
        self.portable = lv.switch(portable_row)

        active = gui.specter_state.active_seed
        if active is not None and active.mnemonic:
            self._button("Save active seed", GREEN_HEX, self._save)
        self._button("Load seed from card", CYAN_HEX, self._load)
        self._button("Delete seed from card", RED_HEX, self._delete)

    def _button(self, text, color_key, callback):
        button = lv.button(self)
        button.set_size(lv.pct(100), 54)
        button.set_style_bg_color(theme_color(color_key), 0)
        button.set_style_radius(10, 0)
        button.set_style_border_width(0, 0)
        label = lv.label(button)
        label.set_text(text)
        label.set_style_text_font(theme_font(FONT_TEXT_THEME), 0)
        label.set_style_text_color(theme_color(WHITE_HEX), 0)
        label.center()
        button.add_event_cb(callback, lv.EVENT.CLICKED, None)

    def _pin_value(self):
        value = self.pin.get_text()
        if not value:
            raise ValueError("Enter the Smartcard PIN")
        return value

    def _result(self, text, error=False):
        self.message.set_text(text)
        self.message.set_style_text_color(theme_color(RED_HEX if error else GREEN_HEX), 0)

    def _save(self, event):
        try:
            seed = self.gui.specter_state.active_seed
            encrypt = not self.portable.has_state(lv.STATE.CHECKED)
            self.storage.save_card_seed(seed.mnemonic, self._pin_value(), encrypt=encrypt)
            self.gui.specter_state._SmartCard_hasSeed = True
            self._result("Recovery phrase saved to Smartcard")
        except Exception as exc:
            self._result(str(exc), True)

    def _load(self, event):
        try:
            mnemonic = self.storage.load_card_seed(self._pin_value())
            status = self.storage.card_status()
            seed = Seed(label="Smartcard %s" % status["fingerprint"], mnemonic=mnemonic)
            self.gui.specter_state.add_seed(seed)
            self.gui.specter_state._SmartCard_hasSeed = True
            self._result("Recovery phrase loaded")
            self.gui.show_menu("seed_detail")
        except Exception as exc:
            self._result(str(exc), True)

    def _delete(self, event):
        try:
            self.storage.delete_card_seed(self._pin_value())
            self.gui.specter_state._SmartCard_hasSeed = False
            self._result("Recovery phrase deleted from Smartcard")
        except Exception as exc:
            self._result(str(exc), True)
