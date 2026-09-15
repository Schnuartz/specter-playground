"""Rename wallet screen."""
import lvgl as lv
from ..basic.templates.specter_gui_base import t as _tr
from ..basic.ui_consts import (
    theme_color, theme_font, FONT_TITLE_THEME, FONT_TEXT_THEME, FONT_SMALL_THEME, FONT_CAPTION_THEME,
    PAD_MD, PAD_LG,
    BG_BLACK_HEX, BG_CARD_HEX,
    WHITE_HEX, GREY_LIGHT_HEX, CYAN_HEX, GREEN_HEX,
)
from ..basic.keyboard_manager import Layout


class RenameWalletScreen(lv.obj):
    """Rename the active wallet."""

    def __init__(self, gui, parent):
        super().__init__(parent)
        self.gui = gui
        self.wallet = gui.specter_state.active_wallet

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

        title = lv.label(self)
        title.set_text(_tr("SCHN_RENAME_WALLET"))
        title.set_style_text_font(theme_font(FONT_TITLE_THEME), 0)
        title.set_style_text_color(theme_color(WHITE_HEX), 0)

        # Name input
        self.name_ta = lv.textarea(self)
        self.name_ta.set_text(self.wallet.label if self.wallet else "")
        self.name_ta.set_width(lv.pct(100))
        self.name_ta.set_height(60)
        self.name_ta.set_style_text_font(theme_font(FONT_TEXT_THEME), 0)

        def _on_commit(new_name):
            if self.wallet and new_name:
                self.wallet.label = new_name
            gui.refresh_dashboard()
            gui.show_menu(None)

        kb = lambda e: gui.keyboard_manager.bind(self.name_ta, Layout.FULL, _on_commit)
        self.name_ta.add_event_cb(kb, lv.EVENT.CLICKED, None)

        info = lv.label(self)
        info.set_text(_tr("SCHN_RENAME_HINT"))
        info.set_style_text_font(theme_font(FONT_CAPTION_THEME), 0)
        info.set_style_text_color(theme_color(GREY_LIGHT_HEX), 0)
