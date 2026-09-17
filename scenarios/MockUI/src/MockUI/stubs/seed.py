"""Seed placeholder used by the MockUI state.

Represents a loaded MasterKey (seedphrase) in memory.
Ephemeral — never persisted across power cycles in working memory.
"""
import urandom

try:
    from embit import bip32, bip39
except ImportError:
    bip32 = None
    bip39 = None

class Seed:
    """Tiny seed placeholder used by DeviceState.

    Attributes:
        label: user-given display name (e.g., "My Key")
        fingerprint: master fingerprint hex string (e.g., "a1b2c3d4")
        passphrase: optional BIP-39 passphrase (None if not set)
    """

    def __init__(self, label, fingerprint=None, passphrase=None, mnemonic=None,
                 passphrase_active=False, is_backed_up=False, has_been_synched=False):
        self.label = label
        self.mnemonic = mnemonic.strip() if mnemonic else None
        self.fingerprint = fingerprint or self._fingerprint_from_mnemonic() or self._generate_dummy_fingerprint()
        self.passphrase = passphrase
        self.passphrase_active = passphrase_active
        self.is_backed_up = is_backed_up
        self.has_been_synched = has_been_synched #used to log synching of default wallet per seed
        # Populated by DeviceState.sort_bip85_seeds() after SD imports.
        self.bip85_parent_fingerprint = None
        self.bip85_index = None
        self.bip85_depth = 0

    def _fingerprint_from_mnemonic(self):
        """Return the real BIP32 master fingerprint when seed words are available."""
        if not self.mnemonic or bip39 is None or bip32 is None:
            return None
        if not bip39.mnemonic_is_valid(self.mnemonic):
            raise ValueError("Invalid BIP39 recovery phrase")
        root = bip32.HDKey.from_seed(bip39.mnemonic_to_seed(self.mnemonic, ""))
        return root.child(0).fingerprint.hex()

    @staticmethod
    def _generate_dummy_fingerprint():
        """Generate a fake fingerprint for mock purposes."""
        h = hex(urandom.getrandbits(32))[:]
        return h
    
    def get_fingerprint(self):
        """Return the fingerprint of this seed."""
        if self.passphrase is not None and self.passphrase_active:
            # In a real implementation, the fingerprint would change if a passphrase is active.
            # For this mock, we'll just reverse the hex digits (keeping any 0x prefix).
            # Note: MicroPython does not support step=-1 slices, so use reversed().
            fp = self.fingerprint
            if fp.startswith("0x") or fp.startswith("0X"):
                return fp[:2] + "".join(reversed(fp[2:]))
            return "".join(reversed(fp))
        else:   
            return self.fingerprint

    @staticmethod
    def get_fingerprints(seeds):
        """Return list of fingerprints for a list of seeds."""
        return [seed.get_fingerprint() for seed in seeds]
