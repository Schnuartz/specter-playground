"""Adapter that gives every Schnuartz page the shared top bar."""

import lvgl as lv

from ..basic.templates.specter_gui_base import SpecterGuiElement
from ..basic.top_bar import TopBar
from ..basic.ui_consts import SCREEN_HEIGHT, NAV_BAR_HEIGHT, TOP_BAR_HEIGHT


class Page(SpecterGuiElement):
    """Host a concrete reference screen below the persistent 56 px top bar."""

    def __init__(self, parent, screen_class, screen_id=None):
        super().__init__(parent)
        self.set_size(lv.pct(100), lv.pct(100))
        self.set_style_bg_opa(lv.OPA.TRANSP, 0)
        self.set_style_border_width(0, 0)
        self.set_style_radius(0, 0)
        self.set_style_pad_all(0, 0)
        self.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)

        self.top_bar = TopBar(self.gui, self)

        self.body = lv.obj(self)
        self.body.set_size(
            lv.pct(100),
            SCREEN_HEIGHT - NAV_BAR_HEIGHT - TOP_BAR_HEIGHT,
        )
        self.body.set_pos(0, TOP_BAR_HEIGHT)
        self.body.set_style_bg_opa(lv.OPA.TRANSP, 0)
        self.body.set_style_border_width(0, 0)
        self.body.set_style_radius(0, 0)
        self.body.set_style_pad_all(0, 0)

        if screen_class is None:
            self.screen = lv.obj(self.body)
            self.screen.set_size(lv.pct(100), lv.pct(100))
            self.screen.set_style_bg_opa(lv.OPA.TRANSP, 0)
            self.screen.set_style_border_width(0, 0)
            label = lv.label(self.screen)
            words = (screen_id or "").replace("_", " ").split()
            label.set_text(" ".join(word[:1].upper() + word[1:] for word in words))
            label.center()
        else:
            self.screen = screen_class(self.gui, self.body)

    def refresh(self):
        self.top_bar.refresh(self.device_state)
        refresh = getattr(self.screen, "refresh", None)
        if refresh is not None:
            refresh()


def page_factory(screen_id):
    """Return a lazy one-argument factory suitable for AppScreen."""
    def build(parent):
        from . import get_screen_class
        screen_class = get_screen_class(screen_id)
        return Page(parent, screen_class, screen_id)
    return build
