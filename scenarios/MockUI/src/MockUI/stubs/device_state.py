"""Simple in-memory state holder for the mock UI.

Lightweight and runtime-friendly: avoids typing imports and annotations so
it works cleanly in the MicroPython host/simulator environment.
"""


from .wallet import Wallet
from .seed import Seed


class DeviceState:
    """Mutable application state used by the mock UI.

    All attributes are intentionally public and mutable for simplicity.
    """

    def __init__(self):

       # device features
        self.has_battery = False
        self.battery_pct = None
        self.is_charging = False
        
        self.is_locked = False
        self.pin = None

        # Seed related — ephemeral, cleared on power cycle
        self.loaded_seeds = []
        self.active_seed = None

        # Wallet (descriptor) related — persisted in flash
        self.registered_wallets = []
        self.active_wallet = None
        self.pending_psbt = None

        #KeyStores
        self._SmartCard_hasSeed = False
        self._SD_hasSeed = False
        self._Flash_hasSeed = False

        # peripherals        
        self._hasQR = False
        self._enabledQR = False

        self._hasSD = False
        self._enabledSD = False
        self._detectedSD = False

        self._hasUSB = True
        self._enabledUSB = False

        self._hasSmartCard = False
        self._enabledSmartCard = False
        self._detectedSmartCard = False
        self._storage = None

        # misc
        self.language = "eng"
        self.fw_version = "1.0"

    
    # ── Interface for UI state queries ───────────────────────────────
    def hasSmartCard(self):
        return self._hasSmartCard
    def SmartCard_enabled(self):
        return self.hasSmartCard() and self._enabledSmartCard
    def SmartCard_detected(self):
        self.refresh_peripherals()
        return self.SmartCard_enabled() and self._detectedSmartCard
    def SmartCard_hasSeed(self):
        return self.SmartCard_detected() and self._SmartCard_hasSeed
    def hasSD(self):
        return self._hasSD
    def SD_enabled(self):
        return self.hasSD() and self._enabledSD
    def SD_detected(self):
        self.refresh_peripherals()
        return self.SD_enabled() and self._detectedSD
    def SD_hasSeed(self):
        return self.SD_detected() and self._SD_hasSeed
    def hasQR(self):
        return self._hasQR
    def QR_enabled(self):
        return self.hasQR() and self._enabledQR
    def Flash_hasSeed(self):
        return self._Flash_hasSeed
    def hasUSB(self):
        return self._hasUSB
    def USB_enabled(self):
        return self.hasUSB() and self._enabledUSB

    # ── Interface enable setters ─────────────────────────────────────
    def set_QR_enabled(self, enabled):
        self._enabledQR = bool(enabled)
    def set_USB_enabled(self, enabled):
        self._enabledUSB = bool(enabled)
    def set_SD_enabled(self, enabled):
        self._enabledSD = bool(enabled)
    def set_SmartCard_enabled(self, enabled):
        self._enabledSmartCard = bool(enabled)

    @property
    def storage(self):
        if self._storage is None:
            from ..storage import SeedStorage
            self._storage = SeedStorage()
        return self._storage

    def refresh_peripherals(self):
        """Synchronize UI flags with the physical or browser peripherals."""
        if self._storage is None:
            return
        try:
            self._detectedSD = self.storage.sd_present()
            self._SD_hasSeed = bool(self.storage.list_sd_seeds()) if self._detectedSD else False
        except Exception as exc:
            print("SD status:", exc)
            self._detectedSD = False
            self._SD_hasSeed = False
        try:
            self._detectedSmartCard = self.storage.card_present()
            if self._detectedSmartCard:
                status = self.storage.card_status()
                # A locked JavaCard intentionally does not reveal its secret.
                # Keep the import entry available for any initialized card;
                # the PIN-protected load operation determines whether it is empty.
                self._SmartCard_hasSeed = bool(status["has_seed"] or status["pin_set"])
            else:
                self._SmartCard_hasSeed = False
        except Exception as exc:
            print("Smartcard status:", exc)
            self._detectedSmartCard = False
            self._SmartCard_hasSeed = False

    # ── Seed helpers ─────────────────────────────────────────────────
    def add_seed(self, seed):
        """Load a seed, select it, and ensure the shared default wallet."""
        self.loaded_seeds.append(seed)
        wallet = self._ensure_default_wallet()
        self.set_active_seed(seed)
        if self.active_wallet is None:
            self.set_active_wallet(wallet)
        return wallet

    def set_active_seed(self, seed):
        self.active_seed = seed
        if seed is not None and not self.seed_matches_wallet(seed, self.active_wallet):
            self.active_wallet = self._ensure_default_wallet()

    def remove_seed(self, seed):
        """Remove a seed from loaded seeds."""
        if seed in self.loaded_seeds:
            self.loaded_seeds.remove(seed)
        if self.active_seed is seed:
            self.active_seed = self.loaded_seeds[0] if self.loaded_seeds else None

    def wallets_for_seed(self, seed):
        """Return wallets that match this seed (including the shared Default Wallet)."""
        if seed is None:
            return None
        fp = seed.get_fingerprint()
        return [wallet for wallet in self.registered_wallets
                if wallet.is_default_wallet() or fp in wallet.required_fingerprints]

    def seed_matches_wallet(self, seed, wallet):
        """Check if a seed's fingerprint is in the wallet's required signers."""
        if not seed or not wallet:
            return False
        return wallet in self.wallets_for_seed(seed)

    # ── Wallet helpers ───────────────────────────────────────────────
    def register_wallet(self, wallet, imported=False, source="SD card"):
        """Register a wallet descriptor. Returns the wallet.

        Args:
            wallet: Wallet instance to register.
            imported: If True, mark has_been_exported=True because the
                wallet was received from a companion app (QR scan / SD card)
                and therefore already "connected".
        """
        if imported:
            wallet.mark_shared(source)
        self.registered_wallets.append(wallet)
        self.set_active_wallet(wallet)
        return wallet

    def set_active_wallet(self, wallet):
        self.active_wallet = wallet

    def remove_wallet(self, wallet):
        """Remove a wallet descriptor."""
        if wallet in self.registered_wallets:
            self.registered_wallets.remove(wallet)
        if self.active_wallet is wallet:
            candidates = (self.wallets_for_seed(self.active_seed)
                          if self.active_seed is not None
                          else self.registered_wallets)
            self.active_wallet = candidates[0] if candidates else None

    def _ensure_default_wallet(self):
        """Ensure the shared Default Wallet exists.
        There is only ONE Default Wallet that fits any loaded key."""
        for wallet in self.registered_wallets:
            if wallet.is_default_wallet():
                return wallet
        # Create the singleton Default Wallet
        wallet = Wallet(
            label="Default",
            descriptor="default",
            isMultiSig=False,
            net="mainnet",
            required_fingerprints=[],
        )
        self.registered_wallets.append(wallet)
        return wallet

    def seeds_for_wallet(self, wallet):
        """Return seeds that match this wallet (including the shared Default Wallet)."""
        if wallet is None:
            return None
        if wallet.is_default_wallet():
            # Default wallet matches any seed
            return self.loaded_seeds
        
        fps = set(wallet.required_fingerprints)
        return [seed for seed in self.loaded_seeds
                if seed.get_fingerprint() in fps] 

    def signing_match_count(self, wallet):
        """Return (matched_count, required_count) for the given wallet."""
        if not wallet:
            return (0, 0)
        # Default wallet: 1-of-1 whenever any seed is loaded
        if wallet.is_default_wallet():
            return (1, 1) if self.loaded_seeds else (0, 1)

        if wallet.is_standard():
            loaded_fps = set(seed.get_fingerprint() for seed in self.loaded_seeds)
            matched = len(loaded_fps & set(wallet.required_fingerprints))
            return (matched, len(wallet.required_fingerprints))
        else:
            # For non-standard wallets, we can't analyze the descriptor, so just return dummy values
            return (1, 1) if self.loaded_seeds else (0, 1)

    # ── Lock helpers ─────────────────────────────────────────────────
    def lock(self):
        self.is_locked = True

    def unlock(self, pin=None):
        # naive PIN check for mock; in real code use secure compare
        if self.pin is None or pin == self.pin:
            self.is_locked = False
            return True
        return False

    # ── Debug helpers ────────────────────────────────────────────────
    def debug_cycle_battery(self):
        """Advance the simulated battery level by one step (for testing).

        TODO: DUMMY CODE — replace with actual device battery read logic.
        """
        if self.has_battery:
            if self.is_charging:
                self.battery_pct = min(100, self.battery_pct + 10)
                if self.battery_pct == 100:
                    self.is_charging = False
            else:
                self.battery_pct = max(0, self.battery_pct - 10)
                if self.battery_pct == 0:
                    self.is_charging = True
