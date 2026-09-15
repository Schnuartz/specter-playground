import lvgl as lv

from .utils import (
    GUI_REFRESH_MS,
    KeyboardManager,
    slide_x, slide_y, GUIAnimations,
    set_scroll, set_size, set_pos, get_size,
    set_layout,
)
from .ui_state import UIState, Context
from .i18n import I18nManager
from .theming import ThemeManager, apply_style
from .tour import GuidedTour, INTRO_TOUR_STEPS
from .components import NavigationBar, AppScreen
from .templates.specter_gui_base import bind_gui
from .templates.rebuildable import RebuildableObj
from .dashboard import Dashboard
from ..screens import get_view_factory

from ..stubs import DeviceState

_REFERENCE_SCREEN_IDS = (
    "locked", "seed_management", "seed_detail", "generate_seed",
    "set_passphrase", "show_seed_words", "enter_seed_words",
    "wallet_info", "wallet_menu", "wallet_details", "add_wallet",
    "rename_wallet", "connect_app", "export", "receive", "address_qr",
    "scan", "sd_card", "signing", "settings", "security_settings",
    "interfaces", "language_settings", "theme_settings", "import_language",
    "import_theme", "wipe_device",
    "xpub_export", "firmware_info", "backup", "verify_address",
)

_VIEW_MAP = {screen_id: get_view_factory(screen_id)
             for screen_id in _REFERENCE_SCREEN_IDS}
_VIEW_MAP.update({
    "main": Dashboard,
    "start_intro_tour": Dashboard,
    # Compatibility aliases for existing scenarios and device tests.
    "manage_wallet": get_view_factory("wallet_menu"),
    "view_signers": get_view_factory("wallet_details"),
    "manage_security_settings": get_view_factory("security_settings"),
    "manage_backups": get_view_factory("backup"),
    "manage_firmware": get_view_factory("firmware_info"),
    "connect_sw_wallet": get_view_factory("connect_app"),
    "add_seed": get_view_factory("seed_management"),
    "manage_security_features": get_view_factory("security_settings"),
    "manage_seedphrase": get_view_factory("seed_detail"),
    "related_wallets_for_seed": get_view_factory("seed_detail"),
    "store_seedphrase": get_view_factory("seed_detail"),
    "clear_seedphrase": get_view_factory("seed_detail"),
    "generate_seedphrase": get_view_factory("generate_seed"),
    "create_custom_wallet": get_view_factory("add_wallet"),
    "manage_storage": get_view_factory("sd_card"),
    "select_language": get_view_factory("language_settings"),
    "select_theme": get_view_factory("theme_settings"),
    "manage_preferences": get_view_factory("settings"),
    "manage_settings": get_view_factory("settings"),
})


class SpecterGui(RebuildableObj):

    # Ordered list: _init_grid() builds children top-to-bottom in list order.
    # MicroPython dicts do NOT preserve insertion order!
    _SUBELEMENTS = [
        ("app_screen",     AppScreen),
        ("navigation_bar", NavigationBar),
    ]

    def __init__(self, specter_state=None, ui_state=None):
        #disable LVGL's built-in theme; we'll use our own theming system instead
        lv.display_get_default().set_theme(None)
        #register the global GUI instance before calling super().__init__ 
        # so that any early calls to get_gui() (e.g. from widget constructors) succeed
        bind_gui(self)

        if specter_state and isinstance(specter_state, DeviceState):
            self.device_state = specter_state
        else:
            self.device_state = DeviceState()

        if ui_state and isinstance(ui_state, UIState):
            self.ui_state = ui_state
        else:
            self.ui_state = UIState()

        # Reference-layout components historically called this object
        # ``specter_state``. Keep one state instance and expose that name as an
        # API alias while the clean controller continues to own UIState.
        self.specter_state = self.device_state
        self.ui_state.set_active_seed(self.device_state.active_seed)
        self.ui_state.set_active_wallet(self.device_state.active_wallet)
        
        # Initialize non visible children/elements
        self.i18n = I18nManager()
        self.theme = ThemeManager.get_instance()
        self.keyboard_manager = KeyboardManager(self)

        self.on_navigate = self.navigate_to

        # Resolve the initial view class before _init_grid runs (AppScreen reads it via ui_state).
        self.ui_state.view_class = _VIEW_MAP.get(self.ui_state.current_menu_id)

        # create SpecterGui as new screen object and create subelements 
        # (app_screen, navigation_bar) as children of self
        super().__init__(parent=None)

    #gets called during call to superclass constructor before subelements are built
    def setup_self(self):
        apply_style(self, "CONTAINER.SCREEN")
        set_scroll(self, horizontal=False, vertical=False)

    #gets called during call to superclass constructor after subelements are built
    def post_init(self):
        # Initial view was already built by _init_grid (AppScreen reads ui_state.view_class).
        # Just refresh to sync nav bar highlights etc.
        self.navigate_to(self.ui_state.current_menu_id)

        # Periodic refresh (e.g. to update battery level)
        def _tick(timer):
            self.device_state.debug_cycle_battery()
            self.refresh_ui()
        lv.timer_create(_tick, GUI_REFRESH_MS, None)

        # load SpecterGui as the active screen
        lv.screen_load(self)

        

    def change_language(self, lang_code):
        """Change the active language and rebuild the current screen."""
        self.i18n.set_language(lang_code)
        self.rebuild_all()

    def change_theme(self, theme_name, mode=None):
        """Change the active theme (and optionally mode) and rebuild the current screen."""
        self.theme.set_theme(theme_name, mode)
        self.rebuild_all()

    def change_mode(self, mode):
        """Toggle dark/light mode and rebuild the current screen."""
        self.theme.set_mode(mode)
        self.rebuild_all()

    def show_menu(self, target_menu_id=None):
        """Reference-layout navigation API."""
        return self.navigate_to(target_menu_id)

    def refresh_dashboard(self):
        """Refresh dashboard data after an in-place seed/wallet change."""
        if self.app_screen and self.app_screen.view:
            refresh = getattr(self.app_screen.view, "refresh", None)
            if refresh is not None:
                refresh()

    def refresh_ui(self):
        """Centralized refresh method for all UI components."""
        # Animated widgets own their geometry until the transition cleanup.
        # Defer periodic and event-driven refreshes so they cannot rebuild or
        # relayout any visible component halfway through an animation.
        if self.ui_state._is_animating:
            return
        if self.app_screen:
            self.app_screen.refresh()
        if self.navigation_bar:
            self.navigation_bar.refresh()

    def navigate_to(self, target_menu_id=None, target_seed="unset", target_wallet="unset"):
        # Drop all input while animating
        if self.ui_state._is_animating:
            return
        
        if target_menu_id == "main" and self.ui_state.is_run_tour_on_startup:
            target_menu_id = "start_intro_tour"

        if target_menu_id == "locked":
            self.device_state.lock()
        if self.device_state.is_locked:
            target_menu_id = "locked"

        # Capture selections changed by dashboard components before UIState
        # creates the history snapshot for this navigation.
        if target_seed == "unset":
            self.ui_state.set_active_seed(self.device_state.active_seed)
        if target_wallet == "unset":
            self.ui_state.set_active_wallet(self.device_state.active_wallet)

        going_back = target_menu_id in [None, "back"]

        # Update UIState navigation history
        if target_menu_id in ["start_intro_tour", "main", "locked"]:
            anim = self.ui_state.clear_history()
            self.ui_state.current_menu_id = target_menu_id
        elif going_back:
            anim = self.ui_state.pop_menu()
        else:
            anim = self.ui_state.push_menu(target_menu_id)

        if target_seed != "unset":
            self.ui_state.set_active_seed(target_seed)
        if target_wallet != "unset":
            self.ui_state.set_active_wallet(target_wallet)

        self.device_state.active_seed = self.ui_state.active_seed
        self.device_state.active_wallet = self.ui_state.active_wallet

        # Resolve the view class for the new menu before any rebuild or transition.
        self.ui_state.view_class = _VIEW_MAP.get(self.ui_state.current_menu_id)

        if anim is not None and self.ui_state.are_animations_enabled:
            self._do_transition(anim)
        else:
            self.rebuild_slot("app_screen")
            self.refresh_ui()

        if self.ui_state.current_menu_id == "start_intro_tour":
            self.ui_state.current_menu_id = "main"
            if self.navigation_bar:
                self.navigation_bar.refresh()
            GuidedTour(self, GuidedTour.resolve_steps(INTRO_TOUR_STEPS, self)).start()

    def _do_transition(self, anim_type):
        """Animate from the current screen to a freshly-built new screen.

        Dispatches to one of two cases:
          • Case 3 (within SEED/WALLET context, context bar stays): animate
            only the view widget horizontally inside ``screen.content``.
          • Cases 1/2 (between contexts, or context without bar): animate the
            entire Screen unit (bar + battery + content move together).
        """
        self.ui_state._is_animating = True

        ctx = self.ui_state.active_context  # already updated by navigate_to
        ctx_has_bar = self.app_screen.context_bar is not None
        is_horizontal = anim_type in (
            GUIAnimations.horizontal_slide_in,
            GUIAnimations.horizontal_slide_out,
            GUIAnimations.horizontal_push_in,
            GUIAnimations.horizontal_push_out,
        )
        within_ctx_with_bar = (
            ctx_has_bar
            and is_horizontal
            and (ctx == Context.SEED or ctx == Context.WALLET)
        )

        if within_ctx_with_bar:
            self._transition_within_context(anim_type)
        else:
            self._transition_full_screen(anim_type)

    def _transition_within_context(self, anim_type):
        """Case 3: slide only the view widget inside the existing screen.content."""
        screen = self.app_screen
        transition_data = screen.begin_view_transition(self.ui_state.view_class)
        if transition_data is None:
            # An invalid view must not leave navigation locked.  Rebuild the
            # active app screen without animation, which also resets any
            # partially prepared view/layout state.
            self.rebuild_slot("app_screen")
            self._end_animation()
            return

        old_view, new_view, W, _ = transition_data

        def _cleanup():
            screen.finish_view_transition(old_view)
            self._end_animation()

        anims = []
        if anim_type == GUIAnimations.horizontal_slide_in:
            anims.append(slide_x(new_view, W, 0,
                                 on_done_cb=lambda a: _cleanup()))
        elif anim_type == GUIAnimations.horizontal_slide_out:
            old_view.move_foreground()
            anims.append(slide_x(old_view, 0, W,
                                 on_done_cb=lambda a: _cleanup()))

        self.ui_state._anim_refs = anims
        for a in anims:
            a.start()

    def _transition_full_screen(self, anim_type):
        """Cases 1/2: slide the entire Screen unit (bar + content) via a clip container."""
        old_screen = self.app_screen
        W, H = get_size(old_screen)
        app_screen_index = old_screen.get_index()

        # The clip temporarily occupies the active app-screen slot in the root
        # flex layout.  Constructing the new screen inside it avoids a second
        # flex-growing AppScreen splitting the visible viewport in half.
        anim_clip = lv.obj(self)
        set_size(anim_clip, W, H)
        set_scroll(anim_clip, horizontal=False, vertical=False)
        set_layout(anim_clip, lv.LAYOUT.NONE)

        # Reparent the old screen, then put the clip in its former root slot so
        # the navigation bar remains the only other flex child.
        old_screen.set_parent(anim_clip)
        anim_clip.move_to_index(app_screen_index)
        set_pos(old_screen, 0, 0)
        set_size(old_screen, W, H)

        new_screen = AppScreen(anim_clip)  # reads ui_state.view_class
        set_pos(new_screen, 0, 0)
        set_size(new_screen, W, H)
        new_screen.update_layout()
        self.app_screen = new_screen

        def _cleanup_whole():
            # Reparent new_screen back to SpecterGui before deleting the
            # clip (which would otherwise take new_screen with it).
            new_screen.set_parent(self)
            new_screen.move_to_index(app_screen_index)
            anim_clip.delete()   # also deletes old_screen
            self.update_layout()
            self._end_animation()

        anims = []

        if anim_type == GUIAnimations.horizontal_slide_in:
            anims.append(slide_x(new_screen, W, 0,
                                on_done_cb=lambda a: _cleanup_whole()))
        elif anim_type == GUIAnimations.horizontal_slide_out:
            old_screen.move_foreground()   # old on top within anim_clip
            anims.append(slide_x(old_screen, 0, W,
                                on_done_cb=lambda a: _cleanup_whole()))
        elif anim_type == GUIAnimations.horizontal_push_in:
            anims.append(slide_x(new_screen, W, 0))
            anims.append(slide_x(old_screen, 0, -W,
                                on_done_cb=lambda a: _cleanup_whole()))
        elif anim_type == GUIAnimations.horizontal_push_out:
            anims.append(slide_x(new_screen, -W, 0))
            anims.append(slide_x(old_screen, 0, W,
                                on_done_cb=lambda a: _cleanup_whole()))
        elif anim_type == GUIAnimations.vertical_slide_in:
            anims.append(slide_y(new_screen, H, 0,
                                on_done_cb=lambda a: _cleanup_whole()))
        elif anim_type == GUIAnimations.vertical_slide_out:
            old_screen.move_foreground()   # old on top within anim_clip
            anims.append(slide_y(old_screen, 0, H,
                                on_done_cb=lambda a: _cleanup_whole()))

        self.ui_state._anim_refs = anims
        for a in anims:
            a.start()

    def _end_animation(self):
        self.ui_state._anim_refs = None
        self.ui_state._is_animating = False
        self.refresh_ui()
