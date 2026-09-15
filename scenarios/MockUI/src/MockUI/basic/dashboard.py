"""Schnuartz dashboard composed from reusable, theme-aware components."""

import lvgl as lv

from .action_buttons import ActionButtons
from .seed_dropdown import SeedDropdown
from .top_bar import TopBar
from .wallet_list import WalletList
from .templates.specter_gui_base import SpecterGuiElement
from .ui_consts import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    NAV_BAR_HEIGHT,
    TOP_BAR_HEIGHT,
    SEED_DROPDOWN_HEIGHT,
    WALLET_SECTION_HEIGHT,
)


class Dashboard(SpecterGuiElement):
    """The 480×744 dashboard shown above the permanent bottom navigation."""

    def __init__(self, parent):
        super().__init__(parent)
        self.set_size(lv.pct(100), lv.pct(100))
        self.set_style_border_width(0, 0)
        self.set_style_radius(0, 0)
        self.set_style_pad_all(0, 0)
        self.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)

        self.top_bar = TopBar(self.gui, self)

        self.seed_dropdown = SeedDropdown(self.gui, self)
        self.seed_dropdown.set_pos(0, TOP_BAR_HEIGHT)

        self.wallet_list = WalletList(self.gui, self)
        self.wallet_list.set_pos(0, TOP_BAR_HEIGHT + SEED_DROPDOWN_HEIGHT)

        self.action_area = lv.obj(self)
        self.action_area.set_size(
            SCREEN_WIDTH,
            SCREEN_HEIGHT
            - NAV_BAR_HEIGHT
            - TOP_BAR_HEIGHT
            - SEED_DROPDOWN_HEIGHT
            - WALLET_SECTION_HEIGHT,
        )
        self.action_area.set_pos(
            0,
            TOP_BAR_HEIGHT + SEED_DROPDOWN_HEIGHT + WALLET_SECTION_HEIGHT,
        )
        self.action_area.set_style_bg_opa(lv.OPA.TRANSP, 0)
        self.action_area.set_style_border_width(0, 0)
        self.action_area.set_style_radius(0, 0)
        self.action_area.set_style_pad_all(0, 0)

        self.actions = ActionButtons(self.gui, self.action_area)
        self.actions.align(lv.ALIGN.CENTER, 0, 0)

    def refresh(self):
        self.top_bar.refresh(self.device_state)
        self.seed_dropdown.refresh()
        self.wallet_list.refresh()

    def hint_scroll(self):
        self.wallet_list.hint_scroll()
