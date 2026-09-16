"""Enter seed manually — word-by-word mnemonic input with BIP39 suggestions."""
import lvgl as lv
from ..basic.templates.specter_gui_base import t as _tr
from ..basic.ui_consts import (
    theme_color, theme_font, FONT_TITLE_THEME, FONT_TEXT_THEME, FONT_SMALL_THEME, FONT_CAPTION_THEME,
    PAD_MD, PAD_SM, PAD_LG, PAD_XS,
    BG_BLACK_HEX, BG_CARD_HEX, BG_ELEVATED_HEX,
    WHITE_HEX, GREY_LIGHT_HEX, CYAN_HEX, GREEN_HEX, RED_HEX,
)
from ..basic.symbol_lib import BTC_ICONS
from ..basic.keyboard_manager import Layout
from ..stubs.seed import Seed
from embit import bip39


# First few BIP39 words for suggestion (mock subset)
_BIP39_SAMPLE = [
    "abandon", "ability", "able", "about", "above", "absent", "absorb",
    "abstract", "absurd", "abuse", "access", "accident", "account",
    "accuse", "achieve", "acid", "acoustic", "acquire", "across", "act",
    "action", "actor", "actual", "adapt", "add", "addict", "address",
]


class EnterSeedScreen(lv.obj):
    """Word-by-word seed entry with autocomplete suggestions."""

    def __init__(self, gui, parent):
        super().__init__(parent)
        self.gui = gui
        self._words = []
        self._target_count = 12

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
        title.set_text(_tr("SCHN_ENTER_SEED_WORDS"))
        title.set_style_text_font(theme_font(FONT_TITLE_THEME), 0)
        title.set_style_text_color(theme_color(WHITE_HEX), 0)

        # Word count selector
        count_row = lv.obj(self)
        count_row.set_size(lv.pct(100), 36)
        count_row.set_style_bg_opa(lv.OPA.TRANSP, 0)
        count_row.set_style_border_width(0, 0)
        count_row.set_style_pad_all(0, 0)
        count_row.set_layout(lv.LAYOUT.FLEX)
        count_row.set_flex_flow(lv.FLEX_FLOW.ROW)
        count_row.set_flex_align(lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER)
        count_row.set_style_pad_column(PAD_SM, 0)

        for n in [12, 24]:
            btn = lv.button(count_row)
            btn.set_size(80, 32)
            is_selected = n == self._target_count
            btn.set_style_bg_color(theme_color(CYAN_HEX) if is_selected else theme_color(BG_CARD_HEX), 0)
            btn.set_style_bg_opa(lv.OPA.COVER, 0)
            btn.set_style_radius(6, 0)
            btn.set_style_border_width(0, 0)
            btn.set_style_shadow_width(0, 0)
            lbl = lv.label(btn)
            lbl.set_text(str(n) + " words")
            lbl.set_style_text_font(theme_font(FONT_CAPTION_THEME), 0)
            lbl.set_style_text_color(theme_color(WHITE_HEX), 0)
            lbl.center()
            btn.add_event_cb(lambda e, count=n: self._set_count(count), lv.EVENT.CLICKED, None)

        # Progress
        self.progress_lbl = lv.label(self)
        self.progress_lbl.set_style_text_font(theme_font(FONT_CAPTION_THEME), 0)
        self.progress_lbl.set_style_text_color(theme_color(GREY_LIGHT_HEX), 0)
        self._update_progress()

        # Word display area
        self.word_display = lv.obj(self)
        self.word_display.set_size(lv.pct(100), 80)
        self.word_display.set_style_bg_color(theme_color(BG_CARD_HEX), 0)
        self.word_display.set_style_bg_opa(lv.OPA.COVER, 0)
        self.word_display.set_style_radius(8, 0)
        self.word_display.set_style_border_width(0, 0)
        self.word_display.set_style_pad_all(PAD_SM, 0)
        self.word_display.set_layout(lv.LAYOUT.FLEX)
        self.word_display.set_flex_flow(lv.FLEX_FLOW.ROW_WRAP)
        self.word_display.set_style_pad_row(PAD_XS, 0)
        self.word_display.set_style_pad_column(PAD_XS, 0)

        # Word input row
        input_row = lv.obj(self)
        input_row.set_size(lv.pct(100), 50)
        input_row.set_style_bg_opa(lv.OPA.TRANSP, 0)
        input_row.set_style_border_width(0, 0)
        input_row.set_style_pad_all(0, 0)
        input_row.set_layout(lv.LAYOUT.FLEX)
        input_row.set_flex_flow(lv.FLEX_FLOW.ROW)
        input_row.set_flex_align(lv.FLEX_ALIGN.START, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER)
        input_row.set_style_pad_column(PAD_SM, 0)

        self.word_ta = lv.textarea(input_row)
        self.word_ta.set_text("")
        self.word_ta.set_placeholder_text("Type word...")
        self.word_ta.set_width(lv.pct(60))
        self.word_ta.set_height(46)
        self.word_ta.set_style_text_font(theme_font(FONT_TEXT_THEME), 0)
        self.word_ta.set_accepted_chars("abcdefghijklmnopqrstuvwxyz")

        def _on_word_commit(text):
            text = text.strip().lower()
            if text:
                self._words.append(text)
                self._refresh_words()
            if len(self._words) >= self._target_count:
                self._finish()

        kb = lambda e: gui.keyboard_manager.bind(self.word_ta, Layout.FULL, _on_word_commit)
        self.word_ta.add_event_cb(kb, lv.EVENT.CLICKED, None)

        # Add button
        add_btn = lv.button(input_row)
        add_btn.set_size(80, 46)
        add_btn.set_style_bg_color(theme_color(CYAN_HEX), 0)
        add_btn.set_style_radius(8, 0)
        add_btn.set_style_border_width(0, 0)
        add_btn.set_style_shadow_width(0, 0)
        add_lbl = lv.label(add_btn)
        add_lbl.set_text(_tr("SCHN_ADD"))
        add_lbl.set_style_text_font(theme_font(FONT_SMALL_THEME), 0)
        add_lbl.set_style_text_color(theme_color(WHITE_HEX), 0)
        add_lbl.center()
        add_btn.add_event_cb(self._add_word_btn, lv.EVENT.CLICKED, None)

        # Suggestion chips
        self.suggestion_row = lv.obj(self)
        self.suggestion_row.set_size(lv.pct(100), 36)
        self.suggestion_row.set_style_bg_opa(lv.OPA.TRANSP, 0)
        self.suggestion_row.set_style_border_width(0, 0)
        self.suggestion_row.set_style_pad_all(0, 0)
        self.suggestion_row.set_layout(lv.LAYOUT.FLEX)
        self.suggestion_row.set_flex_flow(lv.FLEX_FLOW.ROW)
        self.suggestion_row.set_style_pad_column(PAD_XS, 0)

        # Show some sample suggestions
        for word in _BIP39_SAMPLE[:5]:
            chip = lv.button(self.suggestion_row)
            chip.set_size(lv.SIZE_CONTENT, 30)
            chip.set_style_bg_color(theme_color(BG_ELEVATED_HEX), 0)
            chip.set_style_radius(4, 0)
            chip.set_style_border_width(0, 0)
            chip.set_style_shadow_width(0, 0)
            chip.set_style_pad_left(PAD_SM, 0)
            chip.set_style_pad_right(PAD_SM, 0)
            cl = lv.label(chip)
            cl.set_text(word)
            cl.set_style_text_font(theme_font(FONT_CAPTION_THEME), 0)
            cl.set_style_text_color(theme_color(CYAN_HEX), 0)
            chip.add_event_cb(lambda e, w=word: self._use_suggestion(w), lv.EVENT.CLICKED, None)

        # Finish button (hidden until enough words)
        self.finish_btn = lv.button(self)
        self.finish_btn.set_size(lv.pct(100), 50)
        self.finish_btn.set_style_bg_color(theme_color(GREEN_HEX), 0)
        self.finish_btn.set_style_bg_opa(lv.OPA.COVER, 0)
        self.finish_btn.set_style_radius(10, 0)
        self.finish_btn.set_style_border_width(0, 0)
        self.finish_btn.set_style_shadow_width(0, 0)
        fin_lbl = lv.label(self.finish_btn)
        fin_lbl.set_text(_tr("SCHN_IMPORT_SEED"))
        fin_lbl.set_style_text_font(theme_font(FONT_TEXT_THEME), 0)
        fin_lbl.set_style_text_color(theme_color(WHITE_HEX), 0)
        fin_lbl.center()
        self.finish_btn.add_event_cb(lambda e: self._finish(), lv.EVENT.CLICKED, None)
        self.finish_btn.add_flag(lv.obj.FLAG.HIDDEN)

    def _set_count(self, count):
        self._target_count = count
        self._words.clear()
        self._refresh_words()

    def _add_word_btn(self, e):
        if e.get_code() != lv.EVENT.CLICKED:
            return
        text = self.word_ta.get_text().strip().lower()
        if text:
            self._words.append(text)
            self.word_ta.set_text("")
            self._refresh_words()

    def _use_suggestion(self, word):
        self._words.append(word)
        self.word_ta.set_text("")
        self._refresh_words()

    def _refresh_words(self):
        self.word_display.clean()
        for i, word in enumerate(self._words):
            chip = lv.obj(self.word_display)
            chip.set_size(lv.SIZE_CONTENT, 26)
            chip.set_style_bg_color(theme_color(BG_ELEVATED_HEX), 0)
            chip.set_style_bg_opa(lv.OPA.COVER, 0)
            chip.set_style_radius(4, 0)
            chip.set_style_border_width(0, 0)
            chip.set_style_pad_left(PAD_XS, 0)
            chip.set_style_pad_right(PAD_XS, 0)
            chip.set_style_pad_top(2, 0)
            chip.set_style_pad_bottom(2, 0)
            lbl = lv.label(chip)
            lbl.set_text(str(i + 1) + "." + word)
            lbl.set_style_text_font(theme_font(FONT_CAPTION_THEME), 0)
            lbl.set_style_text_color(theme_color(WHITE_HEX), 0)

        self._update_progress()

        if len(self._words) >= self._target_count:
            self.finish_btn.remove_flag(lv.obj.FLAG.HIDDEN)
        else:
            self.finish_btn.add_flag(lv.obj.FLAG.HIDDEN)

    def _update_progress(self):
        self.progress_lbl.set_text(
            _tr("SCHN_WORD_PREFIX") + str(len(self._words) + 1)
            + _tr("SCHN_OF_INFIX") + str(self._target_count)
        )

    def _finish(self):
        mnemonic = " ".join(self._words[:self._target_count])
        if not bip39.mnemonic_is_valid(mnemonic):
            self.progress_lbl.set_text("Invalid BIP39 recovery phrase")
            self.progress_lbl.set_style_text_color(theme_color(RED_HEX), 0)
            return
        seed = Seed(label=_tr("SCHN_IMPORTED_KEY"), mnemonic=mnemonic)
        self.gui.specter_state.add_seed(seed)
        self.gui.ui_state.clear_history()
        self.gui.show_menu("main")
