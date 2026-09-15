"""Screen registry for the Specter DIY UI."""


def get_screen_class(screen_id):
    """Lazily import and return the screen class for a given ID."""
    # Seed screens
    if screen_id == "seed_management":
        from .seed_menu import SeedMenu
        return SeedMenu
    elif screen_id == "seed_detail":
        from .seed_detail_screen import SeedDetailScreen
        return SeedDetailScreen
    elif screen_id == "generate_seed":
        from .generate_seed_screen import GenerateSeedScreen
        return GenerateSeedScreen
    elif screen_id == "set_passphrase":
        from .passphrase_screen import PassphraseScreen
        return PassphraseScreen
    elif screen_id == "show_seed_words":
        from .show_seed_words_screen import ShowSeedWordsScreen
        return ShowSeedWordsScreen
    elif screen_id == "enter_seed_words":
        from .enter_seed_screen import EnterSeedScreen
        return EnterSeedScreen

    # Wallet screens
    elif screen_id == "wallet_info":
        from .wallet_info_screen import WalletInfoScreen
        return WalletInfoScreen
    elif screen_id == "wallet_menu":
        from .wallet_menu import WalletMenu
        return WalletMenu
    elif screen_id == "wallet_details":
        from .wallet_details import WalletDetails
        return WalletDetails
    elif screen_id == "add_wallet":
        from .add_wallet_screen import AddWalletScreen
        return AddWalletScreen
    elif screen_id == "rename_wallet":
        from .rename_wallet_screen import RenameWalletScreen
        return RenameWalletScreen
    elif screen_id == "connect_app":
        from .connect_app_screen import ConnectAppScreen
        return ConnectAppScreen
    elif screen_id == "export":
        from .export_menu import ExportMenu
        return ExportMenu

    # Action screens
    elif screen_id == "receive":
        from .receive_screen import ReceiveScreen
        return ReceiveScreen
    elif screen_id == "address_qr":
        from .address_qr_screen import AddressQRScreen
        return AddressQRScreen
    elif screen_id == "scan":
        from .scan_screen import ScanScreen
        return ScanScreen
    elif screen_id == "sd_card":
        from .sd_card_screen import SDCardScreen
        return SDCardScreen
    elif screen_id == "signing":
        from .signing_screen import SigningScreen
        return SigningScreen

    # Settings screens
    elif screen_id == "settings":
        from .settings_menu import SettingsMenu
        return SettingsMenu
    elif screen_id == "security_settings":
        from .security_settings_screen import SecuritySettingsScreen
        return SecuritySettingsScreen
    elif screen_id == "interfaces":
        from .interfaces_screen import InterfacesScreen
        return InterfacesScreen
    elif screen_id == "language_settings":
        from .language_screen import LanguageScreen
        return LanguageScreen
    elif screen_id == "theme_settings":
        from .theme_screen import ThemeScreen
        return ThemeScreen
    elif screen_id == "import_language":
        from .settings_import_screen import LanguageImportScreen
        return LanguageImportScreen
    elif screen_id == "import_theme":
        from .settings_import_screen import ThemeImportScreen
        return ThemeImportScreen
    elif screen_id == "wipe_device":
        from .confirm_wipe_screen import ConfirmWipeScreen
        return ConfirmWipeScreen
    elif screen_id == "xpub_export":
        from .xpub_export_screen import XPubExportScreen
        return XPubExportScreen
    elif screen_id == "firmware_info":
        from .firmware_screen import FirmwareScreen
        return FirmwareScreen

    # Lock screen
    elif screen_id == "locked":
        from .locked_screen import LockedScreen
        return LockedScreen

    return None


def get_view_factory(screen_id):
    """Return a one-argument AppScreen factory for a reference page."""
    from .page import page_factory
    return page_factory(screen_id)
