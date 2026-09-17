import sys
import json
from types import ModuleType

import pytest
import lvgl as lv

from MockUI.stubs.device_state import DeviceState
from MockUI.stubs.seed import Seed
from MockUI.stubs.wallet import Wallet
from MockUI.storage import SeedStorage, StorageError
from MockUI.basic.utils.keyboard_layouts import _number_layout
from MockUI.basic.utils.keyboard_manager import Layout


MNEMONIC = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"


def test_smartcard_pin_uses_numeric_keyboard_layout(monkeypatch):
    for name, value in (("OK", "OK"), ("BACKSPACE", "BS"), ("LEFT", "<"), ("RIGHT", ">")):
        monkeypatch.setattr(lv.SYMBOL, name, value, raising=False)
    assert Layout.NUMBER not in (Layout.ALNUM, Layout.FULL)
    lower, upper, special, controls, special_controls = _number_layout()
    assert lower == upper == special
    assert tuple(value for value in lower if len(value) == 1 and value in "0123456789") == tuple("1234567890")
    assert len(controls) == len(special_controls) == 14


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


def test_javacard_transport_import_does_not_initialize_flash_backend(tmp_path, monkeypatch):
    connection = object()

    class Reader:
        def __init__(self, **kwargs):
            pass

        def createConnection(self):
            return connection

    uscard = ModuleType("uscard")
    uscard.Reader = Reader
    uscard.SmartcardException = Exception
    pyb = ModuleType("pyb")
    pyb.Pin = type("Pin", (), {"cpu": type("CPU", (), {
        "A2": "A2", "A4": "A4", "G10": "G10", "C2": "C2", "C5": "C5",
    })})
    monkeypatch.setitem(sys.modules, "uscard", uscard)
    monkeypatch.setitem(sys.modules, "pyb", pyb)
    for module in ("keystore", "keystore.javacard", "keystore.javacard.util"):
        monkeypatch.delitem(sys.modules, module, raising=False)

    flash = tmp_path / "flash"
    flash.mkdir()
    storage = SeedStorage(str(flash), str(tmp_path))

    assert storage._get_connection() is connection
    assert "keystore.flash" not in sys.modules


def test_sd_files_are_classified_by_content(tmp_path, monkeypatch):
    flash = tmp_path / "flash"
    card = tmp_path / "sd"
    flash.mkdir()
    card.mkdir()
    storage = SeedStorage(str(flash), str(card))
    monkeypatch.setattr(storage, "sd_present", lambda: True)

    (card / "public-seed.txt").write_text(MNEMONIC + "\n", encoding="utf-8")
    (card / "wallet.json").write_text(json.dumps({
        "label": "Test wallet",
        "descriptor": "wpkh([73c5da0a/84h/1h/0h]tpub-example/0/*)",
    }), encoding="utf-8")
    (card / "payment.psbt").write_bytes(b"psbt\xfftest")
    (card / "README.txt").write_text("Public demo files", encoding="utf-8")

    entries = {entry["name"]: entry for entry in storage.list_sd_entries()}

    assert entries["public-seed.txt"]["kind"] == storage.SD_SEED
    assert entries["public-seed.txt"]["word_count"] == 12
    assert entries["wallet.json"]["kind"] == storage.SD_WALLET
    assert entries["wallet.json"]["label"] == "Test wallet"
    assert entries["payment.psbt"]["kind"] == storage.SD_TRANSACTION
    assert entries["README.txt"]["kind"] == storage.SD_OTHER
    assert storage.load_sd_mnemonic("public-seed.txt") == MNEMONIC
    assert storage.load_sd_wallet("wallet.json")["descriptor"].startswith("wpkh(")


def test_descriptor_metadata_is_extracted_for_wallet_import():
    from MockUI.screens.sd_card_screen import SDCardScreen

    descriptor = (
        "wsh(sortedmulti(2,[73c5da0a/48h/1h/0h/2h]tpub-a/0/*,"
        "[f00dbabe/48h/1h/0h/2h]tpub-b/0/*))"
    )

    assert SDCardScreen._descriptor_fingerprints(descriptor) == ["73c5da0a", "f00dbabe"]
    assert SDCardScreen._descriptor_threshold(descriptor) == 2


def test_imported_wallet_records_sd_source():
    state = DeviceState()
    wallet = Wallet("Imported", descriptor="wpkh(xpub-example)")

    state.register_wallet(wallet, imported=True, source="SD card")

    assert state.active_wallet is wallet
    assert wallet.has_been_exported is True
    assert wallet.shared_with == ["SD card"]
