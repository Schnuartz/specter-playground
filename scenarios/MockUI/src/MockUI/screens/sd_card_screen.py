"""Live SD-card browser backed by Specter-compatible storage."""

import os
import lvgl as lv

from ..basic.templates.specter_gui_base import t as _tr
from ..basic.ui_consts import (
    theme_color, theme_font, FONT_TITLE_THEME, FONT_TEXT_THEME, FONT_SMALL_THEME,
    PAD_MD, PAD_SM, BG_BLACK_HEX, BG_CARD_HEX, WHITE_HEX, GREY_LIGHT_HEX,
    CYAN_HEX, ORANGE_HEX, GREEN_HEX, RED_HEX,
)
from ..basic.symbol_lib import BTC_ICONS
from ..stubs.seed import Seed
from ..stubs.wallet import (
    Wallet, ADDR_NATIVE_SEGWIT, ADDR_NESTED_SEGWIT, ADDR_LEGACY, ADDR_TAPROOT,
)


def _format_size(size):
    if size < 1024:
        return "%d B" % size
    if size < 1024 * 1024:
        return "%.1f KB" % (size / 1024)
    return "%.1f MB" % (size / (1024 * 1024))


class SDCardScreen(lv.obj):
    """Browse the inserted card and manage encrypted Specter seed files."""

    def __init__(self, gui, parent):
        super().__init__(parent)
        self.gui = gui
        self.storage = gui.specter_state.storage
        self.set_size(lv.pct(100), lv.pct(100))
        self.set_style_bg_color(theme_color(BG_BLACK_HEX), 0)
        self.set_style_bg_opa(lv.OPA.COVER, 0)
        self.set_style_border_width(0, 0)
        self.set_style_radius(0, 0)
        self.set_style_pad_all(PAD_MD, 0)
        self.set_layout(lv.LAYOUT.FLEX)
        self.set_flex_flow(lv.FLEX_FLOW.COLUMN)
        self.set_style_pad_row(PAD_SM, 0)

        title = lv.label(self)
        title.set_text(_tr("SCHN_SD_CARD"))
        title.set_style_text_font(theme_font(FONT_TITLE_THEME), 0)
        title.set_style_text_color(theme_color(WHITE_HEX), 0)

        self.message = lv.label(self)
        self.message.set_width(lv.pct(100))
        self.message.set_style_text_font(theme_font(FONT_SMALL_THEME), 0)
        self.message.set_style_text_color(theme_color(GREY_LIGHT_HEX), 0)

        if not self.storage.sd_present():
            self.message.set_text("No SD card inserted")
            return

        active = self.gui.specter_state.active_seed
        if active is not None and active.mnemonic:
            self._add_action(
                "Save active seed to SD card", GREEN_HEX,
                self._save_active_seed, BTC_ICONS.SD_CARD,
            )

        entries = self.storage.list_sd_entries()
        counts = {}
        for entry in entries:
            counts[entry["kind"]] = counts.get(entry["kind"], 0) + 1
        self.message.set_text(
            "%d seed phrase(s) | %d transaction(s) | %d wallet descriptor(s)" % (
                counts.get(self.storage.SD_SEED, 0),
                counts.get(self.storage.SD_TRANSACTION, 0),
                counts.get(self.storage.SD_WALLET, 0),
            )
        )
        importable_count = (
            counts.get(self.storage.SD_SEED, 0)
            + counts.get(self.storage.SD_WALLET, 0)
        )
        if importable_count:
            self._add_action(
                "Import all seed phrases and wallets",
                CYAN_HEX,
                self._import_all,
                BTC_ICONS.RECEIVE,
            )
        if not entries:
            self._add_info("The SD card is empty")

        categories = (
            (self.storage.SD_SEED, "Seed phrases", BTC_ICONS.MNEMONIC, GREEN_HEX),
            (self.storage.SD_TRANSACTION, "Bitcoin transactions", BTC_ICONS.TRANSACTIONS, ORANGE_HEX),
            (self.storage.SD_WALLET, "Wallet descriptors", BTC_ICONS.WALLET, CYAN_HEX),
            (self.storage.SD_OTHER, "Other files", BTC_ICONS.FILE, WHITE_HEX),
        )
        for kind, heading, icon, color_key in categories:
            group = [entry for entry in entries if entry["kind"] == kind]
            if not group:
                continue
            self._add_category(heading, len(group), icon, color_key)
            for entry in group:
                self._add_file_row(entry, icon, color_key)

    def _add_info(self, text):
        label = lv.label(self)
        label.set_text(text)
        label.set_style_text_font(theme_font(FONT_SMALL_THEME), 0)
        label.set_style_text_color(theme_color(GREY_LIGHT_HEX), 0)

    def _add_action(self, text, color_key, callback, icon):
        button = lv.button(self)
        button.set_size(lv.pct(100), 64)
        button.set_style_min_height(64, 0)
        button.set_style_bg_color(theme_color(BG_CARD_HEX), 0)
        button.set_style_bg_opa(lv.OPA.COVER, 0)
        button.set_style_radius(10, 0)
        button.set_style_border_width(2, 0)
        button.set_style_border_color(theme_color(color_key), 0)
        button.set_layout(lv.LAYOUT.FLEX)
        button.set_flex_flow(lv.FLEX_FLOW.ROW)
        button.set_flex_align(lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER)
        button.set_style_pad_column(PAD_SM, 0)
        image = lv.image(button)
        icon(theme_color(color_key)).add_to_parent(image, zoom=180)
        label = lv.label(button)
        label.set_text(text)
        label.set_style_text_font(theme_font(FONT_TEXT_THEME), 0)
        label.set_style_text_color(theme_color(color_key), 0)
        button.add_event_cb(callback, lv.EVENT.CLICKED, None)

    def _add_category(self, text, count, icon, color_key):
        heading = lv.obj(self)
        heading.set_size(lv.pct(100), 38)
        heading.set_style_bg_opa(lv.OPA.TRANSP, 0)
        heading.set_style_border_width(0, 0)
        heading.set_style_pad_all(0, 0)
        heading.set_layout(lv.LAYOUT.FLEX)
        heading.set_flex_flow(lv.FLEX_FLOW.ROW)
        heading.set_flex_align(lv.FLEX_ALIGN.START, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER)
        heading.set_style_pad_column(PAD_SM, 0)
        image = lv.image(heading)
        icon(theme_color(color_key)).add_to_parent(image, zoom=150)
        label = lv.label(heading)
        label.set_text("%s (%d)" % (text, count))
        label.set_style_text_font(theme_font(FONT_TEXT_THEME), 0)
        label.set_style_text_color(theme_color(color_key), 0)

    def _add_file_row(self, entry, icon, color_key):
        row_color = theme_color(color_key)
        if entry["kind"] == self.storage.SD_SEED:
            imported = self._seed_is_imported(entry)
            row_color = lv.color_hex(0x66BB6A if imported else 0x2E7D32)
            entry = dict(entry)
            entry["detail"] += " | " + ("Imported" if imported else "Not imported")
        row = lv.button(self)
        row.set_size(lv.pct(100), 76)
        row.set_style_bg_color(theme_color(BG_CARD_HEX), 0)
        row.set_style_bg_opa(lv.OPA.COVER, 0)
        row.set_style_radius(10, 0)
        row.set_style_border_width(4, 0)
        row.set_style_border_side(lv.BORDER_SIDE.LEFT, 0)
        row.set_style_border_color(row_color, 0)
        row.set_layout(lv.LAYOUT.FLEX)
        row.set_flex_flow(lv.FLEX_FLOW.ROW)
        row.set_flex_align(lv.FLEX_ALIGN.START, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER)
        row.set_style_pad_column(PAD_MD, 0)

        image = lv.image(row)
        icon(row_color).add_to_parent(image, zoom=190)
        info = lv.obj(row)
        info.set_size(lv.SIZE_CONTENT, lv.SIZE_CONTENT)
        info.set_flex_grow(1)
        info.set_style_bg_opa(lv.OPA.TRANSP, 0)
        info.set_style_border_width(0, 0)
        info.set_style_pad_all(0, 0)
        info.remove_flag(lv.obj.FLAG.CLICKABLE)
        name = lv.label(info)
        name.set_text(entry["label"])
        name.set_style_text_font(theme_font(FONT_SMALL_THEME), 0)
        name.set_style_text_color(theme_color(WHITE_HEX), 0)
        detail = lv.label(info)
        detail.set_text("%s | %s" % (entry["detail"], _format_size(entry["size"])))
        detail.set_style_text_font(theme_font(FONT_SMALL_THEME), 0)
        detail.set_style_text_color(row_color, 0)
        detail.align_to(name, lv.ALIGN.OUT_BOTTOM_LEFT, 0, 3)
        row.add_event_cb(lambda event, item=entry: self._open_file(item), lv.EVENT.CLICKED, None)
        row.add_event_cb(lambda event, name=entry["name"]: self._delete_file(name), lv.EVENT.LONG_PRESSED, None)

    def _seed_is_imported(self, entry):
        try:
            mnemonic = self.storage.load_sd_mnemonic(entry["name"])
        except Exception:
            return False
        return any(seed.mnemonic == mnemonic
                   for seed in self.gui.specter_state.loaded_seeds)

    def _show_result(self, text, error=False):
        self.message.set_text(text)
        self.message.set_style_text_color(theme_color(RED_HEX if error else GREEN_HEX), 0)

    def _save_active_seed(self, event):
        seed = self.gui.specter_state.active_seed
        try:
            filename = self.storage.save_sd_seed(seed.mnemonic, seed.label)
            self.gui.specter_state._SD_hasSeed = True
            self._show_result("Saved as %s" % filename)
            self.gui.show_menu("sd_card")
        except Exception as exc:
            self._show_result(str(exc), True)

    def _open_file(self, entry):
        filename = entry["name"]
        if entry["kind"] == self.storage.SD_SEED:
            try:
                self._import_seed(filename, entry["label"])
                self.gui.show_menu("seed_detail")
            except Exception as exc:
                self._show_result(str(exc), True)
        elif entry["kind"] == self.storage.SD_TRANSACTION:
            self.gui.specter_state.pending_psbt = filename
            self.gui.show_menu("signing")
        elif entry["kind"] == self.storage.SD_WALLET:
            try:
                self._import_wallet(filename, entry["label"])
            except Exception as exc:
                self._show_result(str(exc), True)

    def _import_seed(self, filename, label, sort=True):
        mnemonic = self.storage.load_sd_mnemonic(filename)
        state = self.gui.specter_state
        seed = next((item for item in state.loaded_seeds
                     if item.mnemonic == mnemonic), None)
        imported = seed is None
        if imported:
            seed = Seed(label=label, mnemonic=mnemonic)
            state.add_seed(seed)
        else:
            state.set_active_seed(seed)
        if sort:
            state.sort_bip85_seeds()
        return seed, imported

    def _import_all(self, event):
        imported_seeds = 0
        imported_wallets = 0
        failures = 0
        for entry in self.storage.list_sd_entries():
            try:
                if entry["kind"] == self.storage.SD_SEED:
                    _, imported = self._import_seed(
                        entry["name"], entry["label"], sort=False
                    )
                    imported_seeds += 1 if imported else 0
                elif entry["kind"] == self.storage.SD_WALLET:
                    _, imported = self._import_wallet(
                        entry["name"], entry["label"], navigate=False
                    )
                    imported_wallets += 1 if imported else 0
            except Exception as exc:
                failures += 1
                print("SD bulk import:", entry["name"], exc)

        self.gui.specter_state.sort_bip85_seeds()

        result = "Imported %d seed phrase(s) and %d wallet(s)" % (
            imported_seeds, imported_wallets
        )
        if failures:
            result += " | %d failed" % failures
        elif imported_seeds == 0 and imported_wallets == 0:
            result = "All seed phrases and wallets are already imported"
        self._show_result(result, failures > 0)

    @staticmethod
    def _descriptor_fingerprints(descriptor):
        fingerprints = []
        position = 0
        hex_chars = "0123456789abcdefABCDEF"
        while True:
            start = descriptor.find("[", position)
            if start < 0:
                break
            end = descriptor.find("]", start + 1)
            if end < 0:
                break
            origin = descriptor[start + 1:end]
            fingerprint = origin.split("/", 1)[0]
            if len(fingerprint) == 8 and all(char in hex_chars for char in fingerprint):
                fingerprint = fingerprint.lower()
                if fingerprint not in fingerprints:
                    fingerprints.append(fingerprint)
            position = end + 1
        return fingerprints

    @staticmethod
    def _descriptor_threshold(descriptor):
        for marker in ("sortedmulti(", "multi("):
            start = descriptor.find(marker)
            if start >= 0:
                value = descriptor[start + len(marker):].split(",", 1)[0]
                try:
                    return int(value)
                except ValueError:
                    return None
        return None

    def _import_wallet(self, filename, fallback_label, navigate=True):
        payload = self.storage.load_sd_wallet(filename)
        descriptor = payload["descriptor"].strip()
        state = self.gui.specter_state
        wallet = next((item for item in state.registered_wallets
                       if item.descriptor == descriptor), None)
        imported = wallet is None
        if wallet is None:
            fingerprints = self._descriptor_fingerprints(descriptor)
            threshold = self._descriptor_threshold(descriptor)
            is_multisig = threshold is not None
            if is_multisig and len(fingerprints) < threshold:
                raise ValueError("Wallet descriptor does not contain enough signer fingerprints")
            lower = descriptor.lower()
            if lower.startswith("tr("):
                address_type = ADDR_TAPROOT
            elif lower.startswith("pkh("):
                address_type = ADDR_LEGACY
            elif lower.startswith("sh(wpkh("):
                address_type = ADDR_NESTED_SEGWIT
            else:
                address_type = ADDR_NATIVE_SEGWIT
            testnet_markers = ("tpub", "upub", "vpub", "tb1", "[1/")
            network = "testnet" if any(marker in lower for marker in testnet_markers) else "mainnet"
            wallet = Wallet(
                label=payload.get("label") or fallback_label,
                descriptor=descriptor,
                isMultiSig=is_multisig,
                net=network,
                required_fingerprints=fingerprints,
                threshold=threshold,
                address_type=address_type,
            )
            state.register_wallet(wallet, imported=True, source="SD card")
        else:
            state.set_active_wallet(wallet)
        if navigate:
            self.gui.show_menu("wallet_info")
        return wallet, imported

    def _delete_file(self, filename):
        try:
            if filename.lower().startswith(self.storage.sd_prefix.lower()):
                self.storage.delete_sd_seed(filename)
            else:
                os.remove(self.storage.sd_root + "/" + filename)
            self.gui.show_menu("sd_card")
        except Exception as exc:
            self._show_result(str(exc), True)
