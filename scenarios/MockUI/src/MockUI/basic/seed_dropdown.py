"""Seed dropdown: shows active seed name centered, tap to switch or add wallet."""
import lvgl as lv
from .templates.specter_gui_base import t as _tr
from .ui_consts import (
    theme_color, theme_font, FONT_TITLE_THEME, FONT_TEXT_THEME, FONT_SMALL_THEME, FONT_CAPTION_THEME,
    SEED_DROPDOWN_HEIGHT, SCREEN_WIDTH, PAD_MD, PAD_SM, ROW_HEIGHT, ROW_ICON_ZOOM,
    BG_BLACK_HEX, BG_CARD_HEX, BG_ELEVATED_HEX,
    WHITE_HEX, GREY_LIGHT_HEX, CYAN_HEX, CYAN_DARK_HEX, GREEN_HEX, ORANGE_HEX, PAD_LG,
)
from .symbol_lib import BTC_ICONS
from .modal_overlay import ModalOverlay


class SeedDropdown(lv.obj):
    """Dropdown showing the currently active seed (centered). Tap to switch seeds or add wallet.

    Reused both on the main dashboard and inside the Wallet Menu screen — pass
    ``parent`` to mount it somewhere other than directly on ``gui``, and
    ``on_change`` to be notified (in addition to the dashboard refresh) when
    the active seed changes, so the host screen can rebuild its own content.
    """

    def __init__(self, gui, parent=None, on_change=None):
        super().__init__(parent if parent is not None else gui)
        self.gui = gui
        self.on_change = on_change
        self._dropdown_open = False
        self._modal = None

        self.set_size(SCREEN_WIDTH, SEED_DROPDOWN_HEIGHT)
        self.set_style_bg_color(theme_color(BG_BLACK_HEX), 0)
        self.set_style_bg_opa(lv.OPA.COVER, 0)
        self.set_style_border_width(0, 0)
        self.set_style_radius(0, 0)
        self.set_style_pad_all(0, 0)

        # Seed name label — CENTERED
        self.seed_label = lv.label(self)
        self.seed_label.set_style_text_font(theme_font(FONT_TEXT_THEME), 0)
        self.seed_label.set_style_text_color(theme_color(CYAN_HEX), 0)

        # Dropdown arrow (next to label)
        self.arrow = lv.label(self)
        self.arrow.set_text(lv.SYMBOL.DOWN)
        self.arrow.set_style_text_color(theme_color(GREY_LIGHT_HEX), 0)
        self.arrow.set_style_text_font(theme_font(FONT_SMALL_THEME), 0)

        # Make whole bar clickable
        self.add_flag(lv.obj.FLAG.CLICKABLE)
        self.add_event_cb(self._toggle_dropdown, lv.EVENT.CLICKED, None)

        self.refresh()

    def refresh(self):
        """Update displayed seed name, centered."""
        state = self.gui.specter_state
        if state.active_seed:
            name = state.active_seed.label
            if state.active_seed.passphrase:
                name = name + " + Passphrase"
            self.seed_label.set_text(name)
        elif state.loaded_seeds:
            self.seed_label.set_text(_tr("SCHN_SELECT_SEED"))
        else:
            self.seed_label.set_text(_tr("SCHN_NO_SEED_LOADED"))

        # Center the label + arrow
        self.seed_label.align(lv.ALIGN.CENTER, -10, 0)
        self.arrow.align_to(self.seed_label, lv.ALIGN.OUT_RIGHT_MID, 6, 0)

    def _toggle_dropdown(self, e):
        if e.get_code() != lv.EVENT.CLICKED:
            return
        if self._dropdown_open:
            self._close_dropdown()
        else:
            self._open_dropdown()

    def _open_dropdown(self):
        self._dropdown_open = True
        state = self.gui.specter_state

        self._modal = ModalOverlay(bg_opa=180)
        overlay = self._modal.overlay

        dropdown = lv.obj(overlay)
        dropdown.set_size(SCREEN_WIDTH - 2 * PAD_MD, lv.SIZE_CONTENT)
        dropdown.set_style_bg_color(theme_color(BG_CARD_HEX), 0)
        dropdown.set_style_bg_opa(lv.OPA.COVER, 0)
        dropdown.set_style_border_width(1, 0)
        dropdown.set_style_border_color(theme_color(CYAN_DARK_HEX), 0)
        dropdown.set_style_radius(8, 0)
        dropdown.set_style_pad_all(PAD_SM, 0)
        dropdown.set_style_pad_row(PAD_SM, 0)
        dropdown.set_layout(lv.LAYOUT.FLEX)
        dropdown.set_flex_flow(lv.FLEX_FLOW.COLUMN)
        dropdown.align(lv.ALIGN.TOP_MID, 0, self._abs_y() + self.get_height() + 8)

        # Currently selected seed's fingerprint — shown big, once, above the
        # list (not squeezed into the always-visible collapsed bar). Icon
        # matches the fingerprint-icon convention from the Marko fork.
        if state.active_seed:
            fp_row = lv.obj(dropdown)
            fp_row.set_size(lv.pct(100), lv.SIZE_CONTENT)
            fp_row.set_style_bg_opa(lv.OPA.TRANSP, 0)
            fp_row.set_style_border_width(0, 0)
            fp_row.set_style_pad_all(0, 0)
            fp_row.set_layout(lv.LAYOUT.FLEX)
            fp_row.set_flex_flow(lv.FLEX_FLOW.ROW)
            fp_row.set_flex_align(lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER)
            fp_row.set_style_pad_column(PAD_SM, 0)

            fp_icon = lv.image(fp_row)
            BTC_ICONS.RELAY(theme_color(CYAN_HEX)).add_to_parent(fp_icon, zoom=ROW_ICON_ZOOM)

            fp_header = lv.label(fp_row)
            fp_header.set_text(state.active_seed.fingerprint[:8])
            fp_header.set_style_text_font(theme_font(FONT_TITLE_THEME), 0)
            fp_header.set_style_text_color(theme_color(CYAN_HEX), 0)

        # Seed list
        if state.loaded_seeds:
            for seed in state.loaded_seeds:
                is_active = state.active_seed is seed
                btn = lv.button(dropdown)
                btn.set_size(lv.pct(100), ROW_HEIGHT)
                btn.set_style_bg_color(theme_color(BG_ELEVATED_HEX) if is_active else theme_color(BG_CARD_HEX), 0)
                btn.set_style_bg_opa(lv.OPA.COVER, 0)
                btn.set_style_radius(8, 0)
                btn.set_style_border_width(0, 0)
                btn.set_style_shadow_width(0, 0)

                btn.set_layout(lv.LAYOUT.FLEX)
                btn.set_flex_flow(lv.FLEX_FLOW.ROW)
                btn.set_flex_align(lv.FLEX_ALIGN.START, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER)
                btn.set_style_pad_column(PAD_SM, 0)
                derived = seed.bip85_depth > 0
                btn.set_style_pad_left(PAD_MD + (PAD_LG if derived else 0), 0)
                if derived:
                    btn.set_width(lv.pct(92))
                    btn.set_style_margin_left(PAD_LG, 0)

                ico = lv.image(btn)
                if derived:
                    derived_color = ORANGE_HEX if seed.bip85_depth > 1 else GREEN_HEX
                    BTC_ICONS.SHARED_WALLET(theme_color(derived_color)).add_to_parent(ico, zoom=ROW_ICON_ZOOM)
                else:
                    BTC_ICONS.KEY(theme_color(CYAN_HEX) if is_active else theme_color(GREY_LIGHT_HEX)).add_to_parent(ico, zoom=ROW_ICON_ZOOM)

                lbl = lv.label(btn)
                name = seed.label
                if seed.passphrase:
                    name = name + " + PP"
                lbl.set_text(name)
                lbl.set_style_text_font(theme_font(FONT_TEXT_THEME), 0)
                lbl.set_style_text_color(theme_color(CYAN_HEX) if is_active else theme_color(WHITE_HEX), 0)
                lbl.set_flex_grow(1)

                # Fingerprint — always shown so seeds are unambiguous
                fp = lv.label(btn)
                fp.set_text(seed.fingerprint[:8])
                fp.set_style_text_font(theme_font(FONT_SMALL_THEME), 0)
                fp.set_style_text_color(theme_color(GREY_LIGHT_HEX), 0)

                if is_active:
                    check = lv.label(btn)
                    check.set_text(lv.SYMBOL.OK)
                    check.set_style_text_font(theme_font(FONT_TEXT_THEME), 0)
                    check.set_style_text_color(theme_color(GREEN_HEX), 0)

                btn.add_event_cb(lambda e, s=seed: self._select_seed(s), lv.EVENT.CLICKED, None)

        # Divider
        divider = lv.obj(dropdown)
        divider.set_size(lv.pct(100), 1)
        divider.set_style_bg_color(theme_color(CYAN_DARK_HEX), 0)
        divider.set_style_bg_opa(lv.OPA.COVER, 0)
        divider.set_style_border_width(0, 0)

        # "Add New Seed Phrase" button
        add_btn = lv.button(dropdown)
        add_btn.set_size(lv.pct(100), ROW_HEIGHT)
        add_btn.set_style_bg_color(theme_color(BG_CARD_HEX), 0)
        add_btn.set_style_bg_opa(lv.OPA.COVER, 0)
        add_btn.set_style_radius(8, 0)
        add_btn.set_style_border_width(0, 0)
        add_btn.set_style_shadow_width(0, 0)

        add_btn.set_layout(lv.LAYOUT.FLEX)
        add_btn.set_flex_flow(lv.FLEX_FLOW.ROW)
        add_btn.set_flex_align(lv.FLEX_ALIGN.START, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER)
        add_btn.set_style_pad_column(PAD_SM, 0)
        add_btn.set_style_pad_left(PAD_MD, 0)

        add_ico = lv.image(add_btn)
        BTC_ICONS.PLUS(theme_color(CYAN_HEX)).add_to_parent(add_ico, zoom=ROW_ICON_ZOOM)

        add_lbl = lv.label(add_btn)
        add_lbl.set_text("Add New Seed Phrase")
        add_lbl.set_style_text_font(theme_font(FONT_TEXT_THEME), 0)
        add_lbl.set_style_text_color(theme_color(CYAN_HEX), 0)

        add_btn.add_event_cb(self._add_seed, lv.EVENT.CLICKED, None)

        # Tap outside to close
        overlay.add_flag(lv.obj.FLAG.CLICKABLE)
        overlay.add_event_cb(lambda e: self._close_dropdown(), lv.EVENT.CLICKED, None)

    def _abs_y(self):
        """Walk up the parent chain to get this widget's absolute screen y.

        Needed because the popup is parented to layer_top (absolute screen
        coordinates) while this widget may be mounted anywhere (dashboard,
        or embedded inside a fullscreen sub-screen like the Wallet Menu).
        """
        y = self.get_y()
        obj = self.get_parent()
        while obj is not None:
            y += obj.get_y()
            obj = obj.get_parent()
        return y

    def _select_seed(self, seed):
        self.gui.specter_state.set_active_seed(seed)
        self._close_dropdown()
        self.refresh()
        if hasattr(self.gui, 'refresh_dashboard'):
            self.gui.refresh_dashboard()
        if self.on_change:
            self.on_change()

    def _add_seed(self, e):
        self._close_dropdown()
        self.gui.show_menu("seed_menu")

    def _close_dropdown(self):
        self._dropdown_open = False
        if self._modal:
            self._modal.close()
            self._modal = None
