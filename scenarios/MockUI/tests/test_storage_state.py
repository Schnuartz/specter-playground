import pytest

from MockUI.stubs.device_state import DeviceState
from MockUI.stubs.seed import Seed
from MockUI.storage import SeedStorage, StorageError


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


def test_sd_seed_roundtrip_uses_device_specific_encryption(tmp_path, monkeypatch):
    flash = tmp_path / "flash"
    card = tmp_path / "sd"
    flash.mkdir()
    card.mkdir()
    storage = SeedStorage(str(flash), str(card))
    monkeypatch.setattr(storage, "sd_present", lambda: True)

    filename = storage.save_sd_seed(MNEMONIC, "Test seed")
    payload = (card / filename).read_bytes()

    assert filename == "%s.Test_seed" % storage.sd_prefix
    assert MNEMONIC.encode() not in payload
    assert storage.load_sd_seed(filename) == MNEMONIC

    other_flash = tmp_path / "other-flash"
    other_flash.mkdir()
    other = SeedStorage(str(other_flash), str(card))
    monkeypatch.setattr(other, "sd_present", lambda: True)
    with pytest.raises(StorageError, match="was not found"):
        other.load_sd_seed(filename)
    other_filename = "%s.Test_seed" % other.sd_prefix
    (card / other_filename).write_bytes(payload)
    with pytest.raises(StorageError, match="another device or is damaged"):
        other.load_sd_seed(other_filename)

    storage.delete_sd_seed(filename)
    assert storage.list_sd_seeds() == []


def test_smartcard_seed_roundtrip_supports_bound_and_portable_modes(tmp_path):
    first_flash = tmp_path / "first"
    second_flash = tmp_path / "second"
    first_flash.mkdir()
    second_flash.mkdir()
    first = SeedStorage(str(first_flash), str(tmp_path))
    second = SeedStorage(str(second_flash), str(tmp_path))

    bound = first._serialize_card_seed(MNEMONIC, encrypt=True)
    portable = first._serialize_card_seed(MNEMONIC, encrypt=False)

    assert MNEMONIC.encode() not in bound
    assert first._parse_card_seed(bound) == MNEMONIC
    with pytest.raises(StorageError, match="another device"):
        second._parse_card_seed(bound)
    assert second._parse_card_seed(portable) == MNEMONIC
