"""Specter-compatible SD and MemoryCard storage for the Schnuartz UI.

This module deliberately uses the firmware's existing cryptography and
JavaCard host implementation.  The browser supplies ``uscard`` and the
physical build supplies the real reader, so both targets exercise the same
``MemoryCardApplet`` protocol used by Specter-DIY.
"""

import os
import json
from binascii import a2b_base64, hexlify
from io import BytesIO

from embit import bip39
from helpers import aead_decrypt, aead_encrypt, tagged_hash
from rng import get_random_bytes


class StorageError(Exception):
    pass


class CardMissingError(StorageError):
    pass


class CardPinError(StorageError):
    pass


class SeedStorage:
    MAGIC = b"sdiy\x00"
    KEYS = {b"\x01": "enc", b"\x02": "entropy"}
    SD_SEED = "seed"
    SD_TRANSACTION = "transaction"
    SD_WALLET = "wallet"
    SD_OTHER = "other"

    def __init__(self, flash_root="/flash", sd_root="/sd", connection=None):
        if sd_root == "/sd":
            try:
                os.stat("/state/sd")
                sd_root = "/state/sd"
            except OSError:
                pass
        self.flash_root = flash_root.rstrip("/") or "/"
        self.sd_root = sd_root.rstrip("/") or "/"
        self._connection = connection
        self._applet = None
        self._connected_slot = None
        self._ensure_dir(self.flash_root)
        self.device_secret = self._load_or_create_secret()
        self.sd_encryption_key = self._load_or_create_sd_key()

    @staticmethod
    def _ensure_dir(path):
        try:
            os.mkdir(path)
        except OSError:
            pass

    def _load_or_create_secret(self):
        path = self.flash_root + "/mockui-device-secret"
        try:
            with open(path, "rb") as stream:
                secret = stream.read()
            if len(secret) == 32:
                return secret
        except OSError:
            pass
        secret = get_random_bytes(32)
        with open(path, "wb") as stream:
            stream.write(secret)
        return secret

    def _load_or_create_sd_key(self):
        """Mirror SDKeyStore's independent ``enc_secret`` key material."""
        path = self.flash_root + "/mockui-enc-secret"
        try:
            with open(path, "rb") as stream:
                secret = stream.read()
            if len(secret) == 32:
                return secret
        except OSError:
            pass
        secret = get_random_bytes(32)
        with open(path, "wb") as stream:
            stream.write(secret)
        return secret

    @property
    def encryption_key(self):
        return tagged_hash("scenc", self.device_secret)

    @property
    def sd_prefix(self):
        card_id = hexlify(tagged_hash("sdid", self.device_secret)[:4]).decode()
        return "specterdiy" + card_id

    def sd_present(self):
        """Detect the browser marker first, then the hardware SD driver."""
        try:
            with open("/bridge/sd-inserted", "rb") as marker:
                return marker.read(1) in (b"1", b"\x01")
        except OSError:
            pass
        try:
            import platform
            return bool(platform.sdcard.is_present)
        except (ImportError, AttributeError):
            try:
                os.stat(self.sd_root)
                return True
            except OSError:
                return False

    @staticmethod
    def _safe_name(name):
        clean = "".join(c for c in (name or "seed") if c.isalnum() or c in "-_ ").strip()
        return clean.replace(" ", "_") or "seed"

    def list_sd_seeds(self):
        if not self.sd_present():
            return []
        try:
            names = [entry[0] for entry in os.ilistdir(self.sd_root)]
        except AttributeError:
            names = os.listdir(self.sd_root)
        except OSError:
            return []
        return sorted(name for name in names if name.lower().startswith(self.sd_prefix.lower()))

    def list_sd_files(self):
        if not self.sd_present():
            return []
        try:
            names = [entry[0] for entry in os.ilistdir(self.sd_root)
                     if len(entry) < 2 or entry[1] != 0x4000]
        except AttributeError:
            names = [name for name in os.listdir(self.sd_root)
                     if not os.path.isdir(self.sd_root + "/" + name)]
        except OSError:
            return []
        files = []
        for name in sorted(names):
            try:
                size = os.stat(self.sd_root + "/" + name)[6]
            except OSError:
                size = 0
            files.append((name, size))
        return files

    def _read_sd_file(self, filename):
        if not filename or "/" in filename or "\\" in filename:
            raise StorageError("Invalid SD card filename")
        try:
            with open(self.sd_root + "/" + filename, "rb") as stream:
                return stream.read()
        except OSError as exc:
            raise StorageError("SD card file could not be read") from exc

    @staticmethod
    def _text_payload(data):
        try:
            text = data.decode().strip()
        except (UnicodeError, ValueError):
            return None
        if text.startswith("\ufeff"):
            text = text[1:].strip()
        return text

    @staticmethod
    def _mnemonic_from_text(text):
        if not text:
            return None
        mnemonic = " ".join(text.split())
        try:
            return mnemonic if bip39.mnemonic_is_valid(mnemonic) else None
        except Exception:
            return None

    @staticmethod
    def _wallet_from_text(text):
        if not text:
            return None
        try:
            payload = json.loads(text)
        except (ValueError, TypeError):
            payload = None
        if isinstance(payload, dict) and isinstance(payload.get("descriptor"), str):
            return payload

        descriptor_prefixes = ("pkh(", "wpkh(", "sh(", "wsh(", "tr(", "combo(")
        if text.startswith(descriptor_prefixes):
            return {"descriptor": text}
        return None

    @staticmethod
    def _is_psbt(data, text):
        if data.startswith(b"psbt\xff"):
            return True
        if text and text.startswith("cHNidP"):
            try:
                return a2b_base64(text).startswith(b"psbt\xff")
            except Exception:
                return False
        return False

    @staticmethod
    def _display_name(filename):
        name = filename.rsplit(".", 1)[0].replace("_", " ").replace("-", " ")
        parts = name.split()
        if parts and parts[0].isdigit():
            parts = parts[1:]
        return " ".join(parts) or filename

    def classify_sd_file(self, filename, size=None):
        """Inspect an SD file and return display metadata for the browser UI."""
        if size is None:
            try:
                size = os.stat(self.sd_root + "/" + filename)[6]
            except OSError:
                size = 0

        if filename.lower().startswith(self.sd_prefix.lower()):
            return {
                "name": filename, "size": size, "kind": self.SD_SEED,
                "label": self._display_name(filename.split(".", 1)[-1]),
                "detail": "Encrypted seed phrase", "word_count": None,
                "encrypted": True,
            }

        try:
            data = self._read_sd_file(filename)
        except StorageError:
            data = b""
        text = self._text_payload(data)
        mnemonic = self._mnemonic_from_text(text)
        if mnemonic:
            words = len(mnemonic.split())
            return {
                "name": filename, "size": size, "kind": self.SD_SEED,
                "label": self._display_name(filename),
                "detail": "Seed phrase · %d words" % words,
                "word_count": words, "encrypted": False,
            }

        if self._is_psbt(data, text) or filename.lower().endswith(".psbt"):
            return {
                "name": filename, "size": size, "kind": self.SD_TRANSACTION,
                "label": self._display_name(filename),
                "detail": "Bitcoin transaction · PSBT",
            }

        wallet = self._wallet_from_text(text)
        if wallet:
            return {
                "name": filename, "size": size, "kind": self.SD_WALLET,
                "label": wallet.get("label") or self._display_name(filename),
                "detail": "Wallet descriptor",
            }

        return {
            "name": filename, "size": size, "kind": self.SD_OTHER,
            "label": self._display_name(filename), "detail": "Other file",
        }

    def list_sd_entries(self):
        return [self.classify_sd_file(filename, size)
                for filename, size in self.list_sd_files()]

    def load_sd_mnemonic(self, filename):
        if filename.lower().startswith(self.sd_prefix.lower()):
            return self.load_sd_seed(filename)
        mnemonic = self._mnemonic_from_text(self._text_payload(self._read_sd_file(filename)))
        if not mnemonic:
            raise StorageError("File does not contain a valid BIP39 seed phrase")
        return mnemonic

    def load_sd_wallet(self, filename):
        payload = self._wallet_from_text(self._text_payload(self._read_sd_file(filename)))
        if not payload:
            raise StorageError("File does not contain a wallet descriptor")
        return payload

    def save_sd_seed(self, mnemonic, name):
        if not self.sd_present():
            raise StorageError("SD card is not inserted")
        if not bip39.mnemonic_is_valid(mnemonic):
            raise StorageError("Recovery phrase is not valid BIP39")
        filename = "%s.%s" % (self.sd_prefix, self._safe_name(name))
        path = self.sd_root + "/" + filename
        payload = aead_encrypt(self.sd_encryption_key, b"", mnemonic.encode())
        with open(path, "wb") as stream:
            stream.write(payload)
        return filename

    def load_sd_seed(self, filename):
        if filename not in self.list_sd_seeds():
            raise StorageError("Seed file was not found on this SD card")
        with open(self.sd_root + "/" + filename, "rb") as stream:
            payload = stream.read()
        try:
            _, plaintext = aead_decrypt(payload, self.sd_encryption_key)
            mnemonic = plaintext.decode()
        except Exception as exc:
            raise StorageError("Seed file belongs to another device or is damaged") from exc
        if not bip39.mnemonic_is_valid(mnemonic):
            raise StorageError("Stored recovery phrase is invalid")
        return mnemonic

    def delete_sd_seed(self, filename):
        if filename not in self.list_sd_seeds():
            raise StorageError("Seed file was not found on this SD card")
        os.remove(self.sd_root + "/" + filename)

    def _get_connection(self):
        if self._connection is None:
            from keystore.javacard.util import get_connection
            self._connection = get_connection()
        return self._connection

    def card_present(self):
        try:
            return bool(self._get_connection().isCardInserted())
        except Exception:
            return False

    def _connect_card(self):
        connection = self._get_connection()
        if not connection.isCardInserted():
            self._applet = None
            raise CardMissingError("Smartcard is not inserted")
        # Recreate the applet for every operation.  This prevents stale secure
        # channel state after the browser moves another card into the reader.
        from keystore.javacard.applets.memorycard import MemoryCardApplet
        try:
            connection.connect(connection.T1_protocol)
            applet = MemoryCardApplet(connection)
            applet.select()
            applet.open_secure_channel()
            applet.get_pin_status()
        except Exception as exc:
            self._applet = None
            raise StorageError("Failed to connect to the MemoryCard") from exc
        self._applet = applet
        return applet

    def card_status(self):
        if not self.card_present():
            return {"present": False, "pin_set": False, "locked": True, "attempts": 0,
                    "attempts_max": 10, "has_seed": False, "fingerprint": None}
        applet = self._connect_card()
        locked = applet.is_locked
        has_seed = False
        if not locked:
            has_seed = len(applet.get_secret()) > 0
        card_id = hexlify(tagged_hash("smartcard/pubkey", applet.card_pubkey)[:4]).decode()
        return {"present": True, "pin_set": applet.is_pin_set, "locked": locked,
                "attempts": applet.pin_attempts_left, "attempts_max": applet.pin_attempts_max,
                "has_seed": has_seed, "fingerprint": card_id}

    def unlock_card(self, pin, set_if_missing=False):
        applet = self._connect_card()
        try:
            if not applet.is_pin_set:
                if not set_if_missing:
                    raise CardPinError("Choose a PIN for this blank Smartcard")
                applet.set_pin(pin)
            elif applet.is_locked:
                applet.unlock(pin)
        except CardPinError:
            raise
        except Exception as exc:
            attempts = applet.pin_attempts_left
            if attempts <= 0:
                raise CardPinError("Smartcard is locked after too many wrong PIN attempts") from exc
            raise CardPinError("Wrong PIN; %d of %d attempts remain" %
                               (attempts, applet.pin_attempts_max)) from exc
        return applet

    def _serialize_card_seed(self, mnemonic, encrypt):
        entropy = bip39.mnemonic_to_bytes(mnemonic)
        raw = b"\x02" + bytes([len(entropy)]) + entropy
        if encrypt:
            fingerprint = tagged_hash("scid", self.device_secret)[:4]
            key = self.encryption_key
        else:
            fingerprint = b"\x00" * 4
            key = b"\xcc" * 32
        return aead_encrypt(key, self.MAGIC + fingerprint, raw)

    def _parse_card_seed(self, payload):
        marker_len = len(self.MAGIC) + 4
        prefix = payload[:marker_len + 1]
        local = bytes([marker_len]) + self.MAGIC + tagged_hash("scid", self.device_secret)[:4]
        portable = bytes([marker_len]) + self.MAGIC + b"\x00" * 4
        if prefix == local:
            key = self.encryption_key
        elif prefix == portable:
            key = b"\xcc" * 32
        else:
            raise StorageError("Smartcard data belongs to another device")
        try:
            _, plaintext = aead_decrypt(payload, key)
            stream = BytesIO(plaintext)
            while True:
                tag = stream.read(1)
                if not tag:
                    break
                length = stream.read(1)[0]
                value = stream.read(length)
                if tag == b"\x02":
                    return bip39.mnemonic_from_bytes(value)
        except StorageError:
            raise
        except Exception as exc:
            raise StorageError("Smartcard seed data is damaged") from exc
        raise StorageError("Smartcard does not contain a recovery phrase")

    def save_card_seed(self, mnemonic, pin, encrypt=True):
        if not bip39.mnemonic_is_valid(mnemonic):
            raise StorageError("Recovery phrase is not valid BIP39")
        applet = self.unlock_card(pin, set_if_missing=True)
        applet.save_secret(self._serialize_card_seed(mnemonic, encrypt))

    def load_card_seed(self, pin):
        applet = self.unlock_card(pin)
        payload = applet.get_secret()
        if not payload:
            raise StorageError("Smartcard does not contain a recovery phrase")
        return self._parse_card_seed(payload)

    def delete_card_seed(self, pin):
        self.unlock_card(pin).save_secret(b"")
