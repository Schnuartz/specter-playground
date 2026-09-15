"""Show seed words screen — displays mnemonic words with security warning."""
import lvgl as lv
from ..basic.templates.specter_gui_base import t as _tr
from ..basic.ui_consts import (
    theme_color, theme_font, FONT_TITLE_THEME, FONT_TEXT_THEME, FONT_SMALL_THEME, FONT_CAPTION_THEME,
    PAD_MD, PAD_SM, PAD_LG,
    BG_BLACK_HEX, BG_CARD_HEX, BG_ELEVATED_HEX, BG_WARN_HEX,
    WHITE_HEX, GREY_LIGHT_HEX, CYAN_HEX, RED_HEX, ORANGE_HEX, YELLOW_HEX,
)
from ..basic.symbol_lib import BTC_ICONS


# Mock 12-word mnemonic for demonstration
_MOCK_WORDS = [
    "abandon", "ability", "able", "about",
    "above", "absent", "absorb", "abstract",
    "absurd", "abuse", "access", "accident",
]


class ShowSeedWordsScreen(lv.obj):
    """Display seed mnemonic words with security warnings."""

    def __init__(self, gui, parent):
        super().__init__(parent)
        self.gui = gui
        self.seed = gui.specter_state.active_seed
        self._revealed = False

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
        title.set_text(_tr("SCHN_SEED_WORDS"))
        title.set_style_text_font(theme_font(FONT_TITLE_THEME), 0)
        title.set_style_text_color(theme_color(WHITE_HEX), 0)

        if self.seed:
            seed_lbl = lv.label(self)
            seed_lbl.set_text(self.seed.label)
            seed_lbl.set_style_text_font(theme_font(FONT_SMALL_THEME), 0)
            seed_lbl.set_style_text_color(theme_color(CYAN_HEX), 0)

        # Security warning
        warn_card = lv.obj(self)
        warn_card.set_size(lv.pct(100), 60)
        warn_card.set_style_bg_color(theme_color(BG_WARN_HEX), 0)
        warn_card.set_style_bg_opa(lv.OPA.COVER, 0)
        warn_card.set_style_radius(8, 0)
        warn_card.set_style_border_width(1, 0)
        warn_card.set_style_border_color(theme_color(ORANGE_HEX), 0)
        warn_card.set_style_pad_all(PAD_SM, 0)

        warn_ico = lv.image(warn_card)
        BTC_ICONS.ALERT(theme_color(ORANGE_HEX)).add_to_parent(warn_ico, zoom=130)
        warn_ico.align(lv.ALIGN.LEFT_MID, 4, 0)

        warn_txt = lv.label(warn_card)
        warn_txt.set_text(_tr("SCHN_SEED_WARNING"))
        warn_txt.set_style_text_font(theme_font(FONT_CAPTION_THEME), 0)
        warn_txt.set_style_text_color(theme_color(ORANGE_HEX), 0)
        warn_txt.align(lv.ALIGN.LEFT_MID, 50, 0)

        # Word container (initially hidden)
        self.word_container = lv.obj(self)
        self.word_container.set_size(lv.pct(100), lv.SIZE_CONTENT)
        self.word_container.set_style_bg_opa(lv.OPA.TRANSP, 0)
        self.word_container.set_style_border_width(0, 0)
        self.word_container.set_style_pad_all(0, 0)
        self.word_container.set_layout(lv.LAYOUT.FLEX)
        self.word_container.set_flex_flow(lv.FLEX_FLOW.ROW_WRAP)
        self.word_container.set_style_pad_row(PAD_SM, 0)
        self.word_container.set_style_pad_column(PAD_SM, 0)
        self.word_container.add_flag(lv.obj.FLAG.HIDDEN)

        for i, word in enumerate(_MOCK_WORDS):
            chip = lv.obj(self.word_container)
            chip.set_size(lv.SIZE_CONTENT, 32)
            chip.set_style_bg_color(theme_color(BG_CARD_HEX), 0)
            chip.set_style_bg_opa(lv.OPA.COVER, 0)
            chip.set_style_radius(6, 0)
            chip.set_style_border_width(0, 0)
            chip.set_style_pad_left(PAD_SM, 0)
            chip.set_style_pad_right(PAD_SM, 0)
            chip.set_style_pad_top(4, 0)
            chip.set_style_pad_bottom(4, 0)

            lbl = lv.label(chip)
            lbl.set_text(str(i + 1) + ". " + word)
            lbl.set_style_text_font(theme_font(FONT_SMALL_THEME), 0)
            lbl.set_style_text_color(theme_color(WHITE_HEX), 0)

        # Reveal / Hide button
        self.reveal_btn = lv.button(self)
        self.reveal_btn.set_size(lv.pct(100), 50)
        self.reveal_btn.set_style_bg_color(theme_color(CYAN_HEX), 0)
        self.reveal_btn.set_style_bg_opa(lv.OPA.COVER, 0)
        self.reveal_btn.set_style_radius(10, 0)
        self.reveal_btn.set_style_border_width(0, 0)
        self.reveal_btn.set_style_shadow_width(0, 0)

        self.reveal_lbl = lv.label(self.reveal_btn)
        self.reveal_lbl.set_text(_tr("SCHN_REVEAL_SEED"))
        self.reveal_lbl.set_style_text_font(theme_font(FONT_TEXT_THEME), 0)
        self.reveal_lbl.set_style_text_color(theme_color(WHITE_HEX), 0)
        self.reveal_lbl.center()

        self.reveal_btn.add_event_cb(self._toggle_reveal, lv.EVENT.CLICKED, None)

    def _toggle_reveal(self, e):
        if e.get_code() != lv.EVENT.CLICKED:
            return
        self._revealed = not self._revealed
        if self._revealed:
            self.word_container.remove_flag(lv.obj.FLAG.HIDDEN)
            self.reveal_lbl.set_text(_tr("SCHN_HIDE_SEED"))
        else:
            self.word_container.add_flag(lv.obj.FLAG.HIDDEN)
            self.reveal_lbl.set_text(_tr("SCHN_REVEAL_SEED"))
