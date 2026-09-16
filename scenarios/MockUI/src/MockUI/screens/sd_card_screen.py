"""Live SD-card browser backed by Specter-compatible storage."""

import os
import lvgl as lv

from ..basic.templates.specter_gui_base import t as _tr
from ..basic.ui_consts import (
    theme_color, theme_font, FONT_TITLE_THEME, FONT_TEXT_THEME, FONT_SMALL_THEME,
    PAD_MD, PAD_SM, BG_BLACK_HEX, BG_CARD_HEX, WHITE_HEX, GREY_LIGHT_HEX,
    CYAN_HEX, ORANGE_HEX, GREEN_HEX, RED_HEX,
)
from ..basic.symbol_lib import BTC_ICONS
from ..stubs.seed import Seed


def _format_size(size):
    if size < 1024:
        return "%d B" % size
    if size < 1024 * 1024:
        return "%.1f KB" % (size / 1024)
    return "%.1f MB" % (size / (1024 * 1024))


class SDCardScreen(lv.obj):
    """Browse the inserted card and manage encrypted Specter seed files."""

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
        title.set_text(_tr("SCHN_SD_CARD"))
        title.set_style_text_font(theme_font(FONT_TITLE_THEME), 0)
        title.set_style_text_color(theme_color(WHITE_HEX), 0)

        self.message = lv.label(self)
        self.message.set_width(lv.pct(100))
        self.message.set_style_text_font(theme_font(FONT_SMALL_THEME), 0)
        self.message.set_style_text_color(theme_color(GREY_LIGHT_HEX), 0)

        if not self.storage.sd_present():
            self.message.set_text("No SD card inserted")
            return

        active = self.gui.specter_state.active_seed
        if active is not None and active.mnemonic:
            self._add_action("Save active seed to SD card", GREEN_HEX, self._save_active_seed)

        files = self.storage.list_sd_files()
        self.message.set_text("%d file(s) · seed files are encrypted for this device" % len(files))
        if not files:
            self._add_info("The SD card is empty")
        for filename, size in files:
            self._add_file_row(filename, size)

    def _add_info(self, text):
        label = lv.label(self)
        label.set_text(text)
        label.set_style_text_font(theme_font(FONT_SMALL_THEME), 0)
        label.set_style_text_color(theme_color(GREY_LIGHT_HEX), 0)

    def _add_action(self, text, color_key, callback):
        button = lv.button(self)
        button.set_size(lv.pct(100), 58)
        button.set_style_bg_color(theme_color(color_key), 0)
        button.set_style_radius(10, 0)
        button.set_style_border_width(0, 0)
        label = lv.label(button)
        label.set_text(text)
        label.set_style_text_font(theme_font(FONT_TEXT_THEME), 0)
        label.set_style_text_color(theme_color(WHITE_HEX), 0)
        label.center()
        button.add_event_cb(callback, lv.EVENT.CLICKED, None)

    def _classify(self, filename):
        lower = filename.lower()
        if lower.startswith(self.storage.sd_prefix.lower()):
            return BTC_ICONS.KEY, GREEN_HEX, "Encrypted recovery phrase"
        if lower.endswith(".psbt"):
            return BTC_ICONS.TRANSACTIONS, ORANGE_HEX, "Bitcoin transaction"
        if lower.endswith(".json"):
            return BTC_ICONS.WALLET, CYAN_HEX, "Wallet descriptor"
        return BTC_ICONS.FILE, WHITE_HEX, "File"

    def _add_file_row(self, filename, size):
        icon, color_key, kind = self._classify(filename)
        row = lv.button(self)
        row.set_size(lv.pct(100), 76)
        row.set_style_bg_color(theme_color(BG_CARD_HEX), 0)
        row.set_style_bg_opa(lv.OPA.COVER, 0)
        row.set_style_radius(10, 0)
        row.set_style_border_width(0, 0)
        row.set_layout(lv.LAYOUT.FLEX)
        row.set_flex_flow(lv.FLEX_FLOW.ROW)
        row.set_flex_align(lv.FLEX_ALIGN.START, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER)
        row.set_style_pad_column(PAD_MD, 0)

        image = lv.image(row)
        icon(theme_color(color_key)).add_to_parent(image, zoom=190)
        info = lv.obj(row)
        info.set_size(lv.SIZE_CONTENT, lv.SIZE_CONTENT)
        info.set_flex_grow(1)
        info.set_style_bg_opa(lv.OPA.TRANSP, 0)
        info.set_style_border_width(0, 0)
        info.set_style_pad_all(0, 0)
        name = lv.label(info)
        name.set_text(filename)
        name.set_style_text_font(theme_font(FONT_SMALL_THEME), 0)
        name.set_style_text_color(theme_color(WHITE_HEX), 0)
        detail = lv.label(info)
        detail.set_text("%s · %s" % (kind, _format_size(size)))
        detail.set_style_text_font(theme_font(FONT_SMALL_THEME), 0)
        detail.set_style_text_color(theme_color(color_key), 0)
        detail.align_to(name, lv.ALIGN.OUT_BOTTOM_LEFT, 0, 3)
        row.add_event_cb(lambda event, name=filename: self._open_file(name), lv.EVENT.CLICKED, None)
        row.add_event_cb(lambda event, name=filename: self._delete_file(name), lv.EVENT.LONG_PRESSED, None)

    def _show_result(self, text, error=False):
        self.message.set_text(text)
        self.message.set_style_text_color(theme_color(RED_HEX if error else GREEN_HEX), 0)

    def _save_active_seed(self, event):
        seed = self.gui.specter_state.active_seed
        try:
            filename = self.storage.save_sd_seed(seed.mnemonic, seed.label)
            self.gui.specter_state._SD_hasSeed = True
            self._show_result("Saved as %s" % filename)
            self.gui.show_menu("sd_card")
        except Exception as exc:
            self._show_result(str(exc), True)

    def _open_file(self, filename):
        if filename.lower().startswith(self.storage.sd_prefix.lower()):
            try:
                mnemonic = self.storage.load_sd_seed(filename)
                label = filename.split(".", 1)[-1].replace("_", " ")
                seed = Seed(label=label, mnemonic=mnemonic)
                self.gui.specter_state.add_seed(seed)
                self._show_result("Recovery phrase loaded")
                self.gui.show_menu("seed_detail")
            except Exception as exc:
                self._show_result(str(exc), True)
        elif filename.lower().endswith(".psbt"):
            self.gui.show_menu("signing")
        elif filename.lower().endswith(".json"):
            self.gui.show_menu("add_wallet")

    def _delete_file(self, filename):
        try:
            if filename.lower().startswith(self.storage.sd_prefix.lower()):
                self.storage.delete_sd_seed(filename)
            else:
                os.remove(self.storage.sd_root + "/" + filename)
            self.gui.show_menu("sd_card")
        except Exception as exc:
            self._show_result(str(exc), True)
