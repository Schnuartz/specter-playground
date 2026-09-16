from .core import KeyStoreError, PinError


def __getattr__(name):
    """Keep JavaCard submodules usable without booting the flash backend.

    Importing ``keystore.javacard`` must not initialize hardware-only modules.
    Preserve the historical ``keystore.FlashKeyStore`` export lazily for code
    that explicitly requests it.
    """
    if name == "FlashKeyStore":
        from .flash import FlashKeyStore
        return FlashKeyStore
    raise AttributeError(name)
