import pytest

from MockUI.stubs.device_state import DeviceState
from MockUI.stubs.seed import Seed


MNEMONIC = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"


def test_seed_uses_real_bip39_fingerprint():
    seed = Seed("Test", mnemonic=MNEMONIC)
    assert seed.mnemonic == MNEMONIC
    assert seed.fingerprint == "73c5da0a"


def test_seed_rejects_invalid_mnemonic():
    with pytest.raises(ValueError, match="Invalid BIP39"):
        Seed("Broken", mnemonic="abandon " * 12)


def test_live_peripheral_flags_replace_mock_fixtures():
    class Storage:
        def sd_present(self):
            return True

        def list_sd_seeds(self):
            return ["specterdiy00000000.seed"]

        def card_present(self):
            return True

        def card_status(self):
            return {"has_seed": False, "pin_set": True}

    state = DeviceState()
    state._storage = Storage()
    state.refresh_peripherals()

    assert state._detectedSD is True
    assert state._SD_hasSeed is True
    # Locked cards do not reveal their secret, but initialized cards must still
    # expose the PIN-protected import action.
    assert state._detectedSmartCard is True
    assert state._SmartCard_hasSeed is True
