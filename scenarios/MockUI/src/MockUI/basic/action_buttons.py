"""Three main action buttons: Scan (large, centered), Receive, SD Card."""
import lvgl as lv
from .templates.specter_gui_base import t as _tr
from .ui_consts import (
    theme_color, theme_font, FONT_TITLE_THEME, FONT_TEXT_THEME, FONT_SMALL_THEME, FONT_CAPTION_THEME,
    SCREEN_WIDTH, BTN_SMALL_HEIGHT, BTN_MED_HEIGHT, BTN_LARGE_HEIGHT, BTN_RADIUS,
    PAD_MD, PAD_SM, PAD_LG,
    BG_BLACK_HEX, BG_CARD_HEX, CYAN_HEX, CYAN_DARK_HEX, WHITE_HEX,
    BTC_ICON_ZOOM,
)
from .symbol_lib import BTC_ICONS


class ActionButtons(lv.obj):
    """Three vertically stacked action buttons: Scan (largest, on top/centered),
    Receive (below Scan), SD Card. All sized up for readability."""

    def __init__(self, gui, parent):
        super().__init__(parent)
        self.gui = gui

        self.set_width(SCREEN_WIDTH)
        self.set_height(lv.SIZE_CONTENT)
        self.set_style_bg_opa(lv.OPA.TRANSP, 0)
        self.set_style_border_width(0, 0)
        self.set_style_radius(0, 0)
        self.set_style_pad_left(PAD_MD, 0)
        self.set_style_pad_right(PAD_MD, 0)
        self.set_style_pad_top(PAD_SM, 0)
        self.set_style_pad_bottom(PAD_SM, 0)

        self.set_layout(lv.LAYOUT.FLEX)
        self.set_flex_flow(lv.FLEX_FLOW.COLUMN)
        self.set_flex_align(lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER)
        self.set_style_pad_row(PAD_MD, 0)

        # Scan button (LARGEST, on top so it sits centered in the action area)
        self._make_btn(
            _tr("SCHN_SCAN"),
            BTC_ICONS.QR_CODE,
            BTN_LARGE_HEIGHT,
            self._scan_cb,
            is_primary=True,
            icon_zoom=480,
        )

        # Receive button (below Scan, a notch smaller than Scan)
        self._make_btn(
            _tr("SCHN_RECEIVE"),
            BTC_ICONS.RECEIVE,
            BTN_MED_HEIGHT,
            self._receive_cb,
            icon_zoom=300,
        )

        # SD Card button
        self._make_btn(
            _tr("SCHN_SD_CARD"),
            BTC_ICONS.SD_CARD,
            BTN_SMALL_HEIGHT,
            self._sd_cb,
            icon_zoom=260,
        )

    def _make_btn(self, text, icon, height, callback, is_primary=False, icon_zoom=380):
        btn = lv.button(self)
        btn.set_size(SCREEN_WIDTH - 2 * PAD_MD, height)
        btn.set_style_radius(BTN_RADIUS, 0)
        btn.set_style_border_width(0, 0)
        btn.set_style_shadow_width(0, 0)

        if is_primary:
            btn.set_style_bg_color(theme_color(CYAN_HEX), 0)
            btn.set_style_bg_color(theme_color(CYAN_DARK_HEX), lv.PART.MAIN | lv.STATE.PRESSED)
            txt_color = theme_color(WHITE_HEX)
        else:
            btn.set_style_bg_color(theme_color(BG_CARD_HEX), 0)
            txt_color = theme_color(WHITE_HEX)

        btn.set_style_bg_opa(lv.OPA.COVER, 0)

        # Layout: icon + text centered
        btn.set_layout(lv.LAYOUT.FLEX)
        btn.set_flex_flow(lv.FLEX_FLOW.ROW)
        btn.set_flex_align(lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER)
        btn.set_style_pad_column(PAD_MD, 0)

        ico = lv.image(btn)
        icon(txt_color).add_to_parent(ico, zoom=icon_zoom)

        lbl = lv.label(btn)
        lbl.set_text(text)
        font = theme_font(FONT_TITLE_THEME) if is_primary else theme_font(FONT_TEXT_THEME)
        lbl.set_style_text_font(font, 0)
        lbl.set_style_text_color(txt_color, 0)

        btn.add_event_cb(callback, lv.EVENT.CLICKED, None)
        return btn

    def _receive_cb(self, e):
        if e.get_code() == lv.EVENT.CLICKED:
            self.gui.show_menu("receive")

    def _scan_cb(self, e):
        if e.get_code() == lv.EVENT.CLICKED:
            self.gui.show_menu("scan")

    def _sd_cb(self, e):
        if e.get_code() == lv.EVENT.CLICKED:
            self.gui.show_menu("sd_card")
