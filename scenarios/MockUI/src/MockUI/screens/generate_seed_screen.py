"""Generate seed screen: name input, fingerprint preview, create button."""
import lvgl as lv
from ..basic.templates.specter_gui_base import t as _tr
import urandom
from ..basic.ui_consts import (
    theme_color, theme_font, FONT_TITLE_THEME, FONT_TEXT_THEME, FONT_SMALL_THEME, FONT_CAPTION_THEME,
    PAD_MD, PAD_SM, PAD_LG, PAD_XL,
    BG_BLACK_HEX, BG_CARD_HEX, BG_ELEVATED_HEX,
    WHITE_HEX, GREY_LIGHT_HEX, CYAN_HEX, CYAN_DARK_HEX, GREEN_HEX,
)
from ..basic.symbol_lib import BTC_ICONS
from ..basic.keyboard_manager import Layout
from ..stubs.seed import Seed


class GenerateSeedScreen(lv.obj):
    """Dedicated screen for generating a new seed with name input."""

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
        self.set_flex_align(lv.FLEX_ALIGN.START, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER)
        self.set_style_pad_row(PAD_LG, 0)

        # Title
        title = lv.label(self)
        title.set_text(_tr("SCHN_GENERATE_NEW_SEED"))
        title.set_style_text_font(theme_font(FONT_TITLE_THEME), 0)
        title.set_style_text_color(theme_color(WHITE_HEX), 0)

        # Name input row
        name_row = lv.obj(self)
        name_row.set_size(lv.pct(100), 70)
        name_row.set_style_bg_opa(lv.OPA.TRANSP, 0)
        name_row.set_style_border_width(0, 0)
        name_row.set_style_pad_all(0, 0)
        name_row.set_layout(lv.LAYOUT.FLEX)
        name_row.set_flex_flow(lv.FLEX_FLOW.ROW)
        name_row.set_flex_align(lv.FLEX_ALIGN.START, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER)

        name_lbl = lv.label(name_row)
        name_lbl.set_text(_tr("SCHN_NAME"))
        name_lbl.set_width(lv.pct(25))
        name_lbl.set_style_text_font(theme_font(FONT_TEXT_THEME), 0)
        name_lbl.set_style_text_color(theme_color(WHITE_HEX), 0)

        self.name_ta = lv.textarea(name_row)
        self.name_ta.set_text(_tr("SCHN_KEY_NAME_PREFIX") + str(urandom.randint(1, 99)))
        self.name_ta.set_width(lv.pct(70))
        self.name_ta.set_height(50)
        self.name_ta.set_style_text_font(theme_font(FONT_TEXT_THEME), 0)

        kb_bind = lambda e: gui.keyboard_manager.bind(self.name_ta, Layout.FULL)
        self.name_ta.add_event_cb(kb_bind, lv.EVENT.CLICKED, None)

        # Generated fingerprint preview
        self.generated_fp = Seed.generate_dummy_fingerprint()

        fp_card = lv.obj(self)
        fp_card.set_size(lv.pct(100), 70)
        fp_card.set_style_bg_color(theme_color(BG_CARD_HEX), 0)
        fp_card.set_style_bg_opa(lv.OPA.COVER, 0)
        fp_card.set_style_radius(8, 0)
        fp_card.set_style_border_width(0, 0)
        fp_card.set_style_pad_all(PAD_MD, 0)

        fp_title = lv.label(fp_card)
        fp_title.set_text(_tr("SCHN_FINGERPRINT"))
        fp_title.set_style_text_font(theme_font(FONT_CAPTION_THEME), 0)
        fp_title.set_style_text_color(theme_color(GREY_LIGHT_HEX), 0)
        fp_title.align(lv.ALIGN.TOP_LEFT, 0, 0)

        fp_val = lv.label(fp_card)
        fp_val.set_text(self.generated_fp)
        fp_val.set_style_text_font(theme_font(FONT_TEXT_THEME), 0)
        fp_val.set_style_text_color(theme_color(CYAN_HEX), 0)
        fp_val.align(lv.ALIGN.BOTTOM_LEFT, 0, 0)

        # Info text
        info = lv.label(self)
        info.set_text(_tr("SCHN_NEW_KEY_WARNING"))
        info.set_width(lv.pct(90))
        info.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
        info.set_style_text_font(theme_font(FONT_SMALL_THEME), 0)
        info.set_style_text_color(theme_color(GREY_LIGHT_HEX), 0)

        # Create button
        create_btn = lv.button(self)
        create_btn.set_size(lv.pct(100), 60)
        create_btn.set_style_bg_color(theme_color(GREEN_HEX), 0)
        create_btn.set_style_bg_opa(lv.OPA.COVER, 0)
        create_btn.set_style_radius(12, 0)
        create_btn.set_style_border_width(0, 0)
        create_btn.set_style_shadow_width(0, 0)

        create_lbl = lv.label(create_btn)
        create_lbl.set_text(_tr("SCHN_GENERATE_KEY"))
        create_lbl.set_style_text_font(theme_font(FONT_TEXT_THEME), 0)
        create_lbl.set_style_text_color(theme_color(WHITE_HEX), 0)
        create_lbl.center()

        create_btn.add_event_cb(self._on_create, lv.EVENT.CLICKED, None)

    def _on_create(self, e):
        if e.get_code() != lv.EVENT.CLICKED:
            return
        name = self.name_ta.get_text()
        seed = Seed(label=name, fingerprint=self.generated_fp)
        self.gui.specter_state.add_seed(seed)
        self.gui.ui_state.clear_history()
        self.gui.show_menu("main")
