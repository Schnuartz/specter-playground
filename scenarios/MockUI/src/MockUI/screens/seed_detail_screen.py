"""Seed detail screen: dedicated page for a specific seed's options."""
import lvgl as lv
from ..basic.templates.specter_gui_base import t as _tr
from ..basic.ui_consts import (
    theme_color, theme_font, FONT_TITLE_THEME, FONT_TEXT_THEME, FONT_SMALL_THEME, FONT_CAPTION_THEME,
    PAD_MD, PAD_SM, PAD_LG, ROW_HEIGHT, ROW_ICON_ZOOM,
    BG_BLACK_HEX, BG_CARD_HEX, BG_ELEVATED_HEX,
    WHITE_HEX, GREY_LIGHT_HEX, CYAN_HEX, RED_HEX, GREEN_HEX,
)
from ..basic.symbol_lib import BTC_ICONS


class SeedDetailScreen(lv.obj):
    """Dedicated page showing details and options for the active seed."""

    def __init__(self, gui, parent):
        super().__init__(parent)
        self.gui = gui
        self.seed = gui.specter_state.active_seed

        self.set_size(lv.pct(100), lv.pct(100))
        self.set_style_bg_color(theme_color(BG_BLACK_HEX), 0)
        self.set_style_bg_opa(lv.OPA.COVER, 0)
        self.set_style_border_width(0, 0)
        self.set_style_radius(0, 0)
        self.set_style_pad_all(PAD_MD, 0)

        self.set_layout(lv.LAYOUT.FLEX)
        self.set_flex_flow(lv.FLEX_FLOW.COLUMN)
        self.set_style_pad_row(PAD_SM, 0)

        if not self.seed:
            lbl = lv.label(self)
            lbl.set_text(_tr("SCHN_NO_SEED_SELECTED"))
            lbl.set_style_text_color(theme_color(GREY_LIGHT_HEX), 0)
            return

        # Seed info card
        info_card = lv.obj(self)
        info_card.set_size(lv.pct(100), 90)
        info_card.set_style_bg_color(theme_color(BG_CARD_HEX), 0)
        info_card.set_style_bg_opa(lv.OPA.COVER, 0)
        info_card.set_style_radius(12, 0)
        info_card.set_style_border_width(1, 0)
        info_card.set_style_border_color(theme_color(CYAN_HEX), 0)
        info_card.set_style_pad_all(PAD_MD, 0)

        # Key icon + name
        key_ico = lv.image(info_card)
        BTC_ICONS.KEY(theme_color(CYAN_HEX)).add_to_parent(key_ico, zoom=180)
        key_ico.align(lv.ALIGN.LEFT_MID, 0, -10)

        name_lbl = lv.label(info_card)
        name_lbl.set_text(self.seed.label)
        name_lbl.set_style_text_font(theme_font(FONT_TITLE_THEME), 0)
        name_lbl.set_style_text_color(theme_color(WHITE_HEX), 0)
        name_lbl.align(lv.ALIGN.LEFT_MID, 55, -10)

        fp_lbl = lv.label(info_card)
        fp_lbl.set_text(_tr("SCHN_FINGERPRINT_PREFIX") + self.seed.fingerprint[:8])
        fp_lbl.set_style_text_font(theme_font(FONT_CAPTION_THEME), 0)
        fp_lbl.set_style_text_color(theme_color(GREY_LIGHT_HEX), 0)
        fp_lbl.align(lv.ALIGN.LEFT_MID, 55, 14)

        # Passphrase status
        if self.seed.passphrase:
            pp_lbl = lv.label(info_card)
            pp_lbl.set_text(_tr("SCHN_PASSPHRASE_ACTIVE"))
            pp_lbl.set_style_text_font(theme_font(FONT_CAPTION_THEME), 0)
            pp_lbl.set_style_text_color(theme_color(GREEN_HEX), 0)
            pp_lbl.align(lv.ALIGN.RIGHT_MID, 0, 0)

        # Go to Dashboard with this seed
        dash_btn = lv.button(self)
        dash_btn.set_size(lv.pct(100), ROW_HEIGHT)
        dash_btn.set_style_bg_color(theme_color(CYAN_HEX), 0)
        dash_btn.set_style_bg_opa(lv.OPA.COVER, 0)
        dash_btn.set_style_radius(10, 0)
        dash_btn.set_style_border_width(0, 0)
        dash_btn.set_style_shadow_width(0, 0)

        dash_btn.set_layout(lv.LAYOUT.FLEX)
        dash_btn.set_flex_flow(lv.FLEX_FLOW.ROW)
        dash_btn.set_flex_align(lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER)
        dash_btn.set_style_pad_column(PAD_SM, 0)

        d_ico = lv.image(dash_btn)
        BTC_ICONS.HOME(theme_color(WHITE_HEX)).add_to_parent(d_ico, zoom=ROW_ICON_ZOOM)

        d_lbl = lv.label(dash_btn)
        d_lbl.set_text(_tr("SCHN_GO_DASHBOARD"))
        d_lbl.set_style_text_font(theme_font(FONT_TEXT_THEME), 0)
        d_lbl.set_style_text_color(theme_color(WHITE_HEX), 0)

        dash_btn.add_event_cb(self._go_dashboard, lv.EVENT.CLICKED, None)

        # Action options - each is a proper navigable item
        self._add_option(_tr("SCHN_SET_PASSPHRASE"), BTC_ICONS.PASSWORD, "set_passphrase")
        self._add_option(_tr("SCHN_SHOW_SEED_WORDS"), BTC_ICONS.VISIBLE, "show_seed_words")
        self._add_option(_tr("SCHN_BIP85"), BTC_ICONS.KEY, "bip85")
        self._add_option(_tr("SCHN_BACKUP_SEED"), BTC_ICONS.SAFE, "backup")
        self._add_option(_tr("SCHN_STORE_SEED"), BTC_ICONS.SD_CARD, "store_seed")

        # Spacer
        spacer = lv.obj(self)
        spacer.set_size(lv.pct(100), 10)
        spacer.set_style_bg_opa(lv.OPA.TRANSP, 0)
        spacer.set_style_border_width(0, 0)

        # Delete (danger)
        self._add_option(_tr("SCHN_DELETE_SEED"), BTC_ICONS.TRASH, "delete_seed", color=theme_color(RED_HEX))

    def _add_option(self, text, icon, target, color=None):
        btn = lv.button(self)
        btn.set_size(lv.pct(100), ROW_HEIGHT)
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
        txt_color = color if color else theme_color(CYAN_HEX)
        icon(txt_color).add_to_parent(ico, zoom=ROW_ICON_ZOOM)

        lbl = lv.label(btn)
        lbl.set_text(text)
        lbl.set_style_text_font(theme_font(FONT_TEXT_THEME), 0)
        lbl.set_style_text_color(color if color else theme_color(WHITE_HEX), 0)
        lbl.set_flex_grow(1)

        # Arrow indicator
        arrow = lv.label(btn)
        arrow.set_text(lv.SYMBOL.RIGHT)
        arrow.set_style_text_font(theme_font(FONT_SMALL_THEME), 0)
        arrow.set_style_text_color(theme_color(GREY_LIGHT_HEX), 0)

        btn.add_event_cb(lambda e, t=target: self._navigate(t), lv.EVENT.CLICKED, None)

    def _go_dashboard(self, e):
        """Switch to this seed and go to dashboard."""
        if e.get_code() != lv.EVENT.CLICKED:
            return
        self.gui.specter_state.set_active_seed(self.seed)
        self.gui.ui_state.clear_history()
        self.gui.show_menu("main")

    def _navigate(self, target):
        if target == "delete_seed":
            self.gui.specter_state.remove_seed(self.seed)
            self.gui.show_menu("seed_management")
        else:
            self.gui.show_menu(target)
