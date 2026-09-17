"""Seed management menu: clean list of actions and loaded seeds.
Tapping a seed navigates to a dedicated seed detail page."""
import lvgl as lv
from ..basic.templates.specter_gui_base import t as _tr
from ..basic.ui_consts import (
    theme_color, theme_font, FONT_TITLE_THEME, FONT_TEXT_THEME, FONT_SMALL_THEME, FONT_CAPTION_THEME,
    PAD_MD, PAD_SM, PAD_LG, ROW_HEIGHT, ROW_ICON_ZOOM,
    WALLET_ROW_HEIGHT, WALLET_ROW_HEIGHT_ACTIVE,
    BG_BLACK_HEX, BG_CARD_HEX, BG_ELEVATED_HEX,
    WHITE_HEX, GREY_LIGHT_HEX, GREY_DARK_HEX, CYAN_HEX, CYAN_DARK_HEX, GREEN_HEX, ORANGE_HEX,
)
from ..basic.symbol_lib import BTC_ICONS


class SeedMenu(lv.obj):
    """Full-screen seed management — actions + loaded seed list."""

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
        self.set_style_pad_row(PAD_SM, 0)

        # Title
        title = lv.label(self)
        title.set_text(_tr("SCHN_SEED_MANAGEMENT"))
        title.set_style_text_font(theme_font(FONT_TITLE_THEME), 0)
        title.set_style_text_color(theme_color(WHITE_HEX), 0)

        # Action buttons
        self._add_nav_btn(_tr("SCHN_GENERATE_NEW_SEED"), BTC_ICONS.MAGIC_WAND, "generate_seed")
        self._add_nav_btn(_tr("SCHN_IMPORT_QR"), BTC_ICONS.QR_CODE, "scan")
        self._add_nav_btn(_tr("SCHN_IMPORT_SD"), BTC_ICONS.SD_CARD, "sd_card")
        self._add_nav_btn(_tr("SCHN_ENTER_MANUALLY"), BTC_ICONS.MNEMONIC, "enter_seed_words")

        # Loaded seeds section
        state = gui.specter_state
        if state.loaded_seeds:
            # Divider
            divider = lv.obj(self)
            divider.set_size(lv.pct(100), 1)
            divider.set_style_bg_color(theme_color(GREY_DARK_HEX), 0)
            divider.set_style_bg_opa(lv.OPA.COVER, 0)
            divider.set_style_border_width(0, 0)

            seeds_title = lv.label(self)
            seeds_title.set_text(_tr("SCHN_LOADED_SEEDS"))
            seeds_title.set_style_text_font(theme_font(FONT_TEXT_THEME), 0)
            seeds_title.set_style_text_color(theme_color(GREY_LIGHT_HEX), 0)
            seeds_title.set_style_pad_top(PAD_SM, 0)

            for seed in state.loaded_seeds:
                self._add_seed_row(seed)

    def _add_nav_btn(self, text, icon, target):
        """Navigation button that goes to a dedicated page."""
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
        icon(theme_color(CYAN_HEX)).add_to_parent(ico, zoom=ROW_ICON_ZOOM)

        lbl = lv.label(btn)
        lbl.set_text(text)
        lbl.set_style_text_font(theme_font(FONT_TEXT_THEME), 0)
        lbl.set_style_text_color(theme_color(WHITE_HEX), 0)
        lbl.set_flex_grow(1)

        # Arrow
        arrow = lv.label(btn)
        arrow.set_text(lv.SYMBOL.RIGHT)
        arrow.set_style_text_font(theme_font(FONT_SMALL_THEME), 0)
        arrow.set_style_text_color(theme_color(GREY_LIGHT_HEX), 0)

        btn.add_event_cb(lambda e, t=target: self.gui.show_menu(t), lv.EVENT.CLICKED, None)

    def _add_seed_row(self, seed):
        """Seed row — tap navigates to seed detail page."""
        state = self.gui.specter_state
        is_active = state.active_seed is seed

        btn = lv.button(self)
        btn.set_size(lv.pct(100), WALLET_ROW_HEIGHT_ACTIVE if is_active else WALLET_ROW_HEIGHT)
        btn.set_style_bg_color(theme_color(BG_ELEVATED_HEX) if is_active else theme_color(BG_CARD_HEX), 0)
        btn.set_style_bg_opa(lv.OPA.COVER, 0)
        btn.set_style_radius(10, 0)
        btn.set_style_shadow_width(0, 0)
        if is_active:
            btn.set_style_border_width(2, 0)
            btn.set_style_border_side(lv.BORDER_SIDE.FULL, 0)
            btn.set_style_border_color(theme_color(CYAN_HEX), 0)
        else:
            # Left accent bar marks these as a selectable list (same
            # treatment as wallet rows on the dashboard).
            btn.set_style_border_width(4, 0)
            btn.set_style_border_side(lv.BORDER_SIDE.LEFT, 0)
            btn.set_style_border_color(theme_color(CYAN_DARK_HEX), 0)

        btn.set_layout(lv.LAYOUT.FLEX)
        btn.set_flex_flow(lv.FLEX_FLOW.ROW)
        btn.set_flex_align(lv.FLEX_ALIGN.START, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER)
        btn.set_style_pad_column(PAD_SM, 0)
        derived = seed.bip85_depth > 0
        btn.set_style_pad_left(PAD_MD + (PAD_LG if derived else 0), 0)

        # BIP85 descendants use the derivation icon.  Grandchildren stay at
        # the same indentation but switch color to expose the second level.
        ico = lv.image(btn)
        if derived:
            derived_color = ORANGE_HEX if seed.bip85_depth > 1 else GREEN_HEX
            BTC_ICONS.SHARED_WALLET(theme_color(derived_color)).add_to_parent(ico, zoom=ROW_ICON_ZOOM)
        else:
            BTC_ICONS.KEY(theme_color(CYAN_HEX) if is_active else theme_color(GREY_LIGHT_HEX)).add_to_parent(ico, zoom=ROW_ICON_ZOOM)

        # Seed name
        name = lv.label(btn)
        label_text = seed.label
        if seed.passphrase:
            label_text = label_text + " + PP"
        name.set_text(label_text)
        name.set_style_text_font(theme_font(FONT_TEXT_THEME), 0)
        name.set_style_text_color(theme_color(CYAN_HEX) if is_active else theme_color(WHITE_HEX), 0)
        name.set_flex_grow(1)

        # Fingerprint
        fp = lv.label(btn)
        fp.set_text(seed.fingerprint[:8])
        fp.set_style_text_font(theme_font(FONT_SMALL_THEME), 0)
        fp.set_style_text_color(theme_color(GREY_LIGHT_HEX), 0)

        # Arrow
        arrow = lv.label(btn)
        arrow.set_text(lv.SYMBOL.RIGHT)
        arrow.set_style_text_font(theme_font(FONT_SMALL_THEME), 0)
        arrow.set_style_text_color(theme_color(GREY_LIGHT_HEX), 0)

        def _on_tap(e, s=seed):
            if e.get_code() == lv.EVENT.CLICKED:
                self.gui.specter_state.set_active_seed(s)
                self.gui.show_menu("seed_detail")

        btn.add_event_cb(_on_tap, lv.EVENT.CLICKED, None)
