"""Bottom navigation bar: Seed Management | Home | Back."""
import lvgl as lv
from .ui_consts import (
    theme_color, theme_font, FONT_TITLE_THEME, FONT_TEXT_THEME, FONT_SMALL_THEME, FONT_CAPTION_THEME,
    NAV_BAR_HEIGHT, SCREEN_WIDTH, NAV_BTN_SIZE,
    BG_DARK_HEX, BG_BLACK_HEX, WHITE_HEX, CYAN_HEX, GREY_HEX,
    PAD_MD,
)
from .symbol_lib import BTC_ICONS


class NavBar(lv.obj):
    """Bottom navigation bar with 3 icon-only buttons."""

    def __init__(self, gui):
        super().__init__(gui)
        self.gui = gui

        self.set_size(SCREEN_WIDTH, NAV_BAR_HEIGHT)
        self.set_style_bg_color(theme_color(BG_DARK_HEX), 0)
        self.set_style_bg_opa(lv.OPA.COVER, 0)
        self.set_style_border_width(0, 0)
        self.set_style_radius(0, 0)
        self.set_style_pad_all(0, 0)
        self.align(lv.ALIGN.BOTTOM_LEFT, 0, 0)

        # Use flex row layout with space-around
        self.set_layout(lv.LAYOUT.FLEX)
        self.set_flex_flow(lv.FLEX_FLOW.ROW)
        self.set_flex_align(
            lv.FLEX_ALIGN.SPACE_AROUND, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER
        )

        # Left: Seed Management (key icon)
        self.seed_btn = self._make_nav_btn(BTC_ICONS.KEY, self._seed_cb)

        # Center: Home
        self.home_btn = self._make_nav_btn(BTC_ICONS.HOME, self._home_cb)

        # Right: Back (arrow left)
        self.back_btn = self._make_nav_btn(BTC_ICONS.ARROW_LEFT, self._back_cb)

    def _make_nav_btn(self, icon, callback):
        btn = lv.button(self)
        btn.set_size(NAV_BTN_SIZE + 20, NAV_BTN_SIZE)
        btn.set_style_bg_opa(lv.OPA.TRANSP, 0)
        btn.set_style_border_width(0, 0)
        btn.set_style_shadow_width(0, 0)

        ico = lv.image(btn)
        icon(theme_color(WHITE_HEX)).add_to_parent(ico, zoom=180)
        ico.center()

        btn.add_event_cb(callback, lv.EVENT.CLICKED, None)
        return btn

    def _seed_cb(self, e):
        if e.get_code() == lv.EVENT.CLICKED:
            self.gui.show_menu("seed_management")

    def _home_cb(self, e):
        if e.get_code() == lv.EVENT.CLICKED:
            self.gui.ui_state.clear_history()
            self.gui.show_menu("main")

    def _back_cb(self, e):
        if e.get_code() == lv.EVENT.CLICKED:
            self.gui.show_menu(None)  # pop history

    def refresh(self):
        """Navigation icons are intentionally stable in the reference UI."""
        pass
