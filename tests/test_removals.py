"""Regression guards for behaviour that was deliberately removed.

These lock in three properties that are easy to lose again when merging from
upstream: the add-on opens no window on its own, it embeds no remote web
content, and it contacts no host other than the sync server.
"""
import importlib
import inspect
import re
import unittest
from pathlib import Path

from tests import mock_aqt

aqt, mw = mock_aqt.install()

import addon.constants
import addon.main
import addon.options_dialog
import addon.tabs.support_tab

ADDON_DIR = Path(__file__).resolve().parent.parent / "addon"


def addon_sources():
    """(path, text) for every Python source shipped in the add-on."""
    return [(p, p.read_text(encoding="utf-8")) for p in sorted(ADDON_DIR.rglob("*.py"))]


class HookRegistrationTests(unittest.TestCase):
    """The add-on must never open a window by itself."""

    def setUp(self):
        aqt.gui_hooks.profile_did_open.append.reset_mock()
        importlib.reload(addon.main)
        self.calls = aqt.gui_hooks.profile_did_open.append.call_args_list

    def test_profile_did_open_registers_exactly_one_callback(self):
        self.assertEqual(
            len(self.calls),
            1,
            f"expected only init(); got {[c.args[0] for c in self.calls]}",
        )

    def test_the_only_registered_callback_is_init(self):
        self.assertIs(self.calls[0].args[0], addon.main.init)

    def test_no_registered_callback_mentions_support(self):
        for call in self.calls:
            name = getattr(call.args[0], "__name__", "")
            self.assertNotIn("support", name.lower())


class RemovedSymbolTests(unittest.TestCase):
    def test_support_tab_has_no_nag_helpers(self):
        for name in (
            "should_open_after_update",
            "_current_version",
            "_load_supporter_state",
            "_on_supporter_check_toggled",
        ):
            with self.subTest(name=name):
                self.assertFalse(hasattr(addon.tabs.support_tab, name))

    def test_support_tab_does_not_import_a_webview(self):
        self.assertFalse(hasattr(addon.tabs.support_tab, "AnkiWebView"))

    def test_constants_has_no_addon_package(self):
        self.assertFalse(hasattr(addon.constants, "ADDON_PACKAGE"))

    def test_dialog_takes_no_initial_tab(self):
        params = inspect.signature(
            addon.options_dialog.AutoSyncOptionsDialog.__init__
        ).parameters
        self.assertNotIn("initial_tab", params)

    def test_on_options_call_takes_no_initial_tab(self):
        params = inspect.signature(addon.options_dialog.on_options_call).parameters
        self.assertNotIn("initial_tab", params)


class SourceGuardTests(unittest.TestCase):
    """Grep-level guards: cheap, and they catch a bad merge immediately."""

    def test_no_external_urls_in_addon_sources(self):
        """The shipped add-on references no external URL at all.

        If a future change legitimately needs one, add it to `allowed` on
        purpose - do not delete this test.
        """
        allowed: set[str] = set()
        found = {}
        for path, text in addon_sources():
            for host in re.findall(r"https?://([A-Za-z0-9.\-]+)", text):
                if host not in allowed:
                    found.setdefault(host, []).append(path.name)
        self.assertEqual(found, {}, f"unexpected external URLs: {found}")

    def test_no_embedded_web_content(self):
        """No remote script, no webview, no HTML injected into one."""
        for token in ("AnkiWebView", "setHtml", "<script", "ko-fi", "kofi", "Widget_2"):
            for path, text in addon_sources():
                with self.subTest(token=token, file=path.name):
                    self.assertNotIn(token.lower(), text.lower())

    def test_no_third_party_reachability_probe(self):
        for path, text in addon_sources():
            with self.subTest(file=path.name):
                self.assertNotIn("8.8.8.8", text)

    def test_no_update_nag_tokens(self):
        for token in (
            "should_open_after_update",
            "supporter_opt_out",
            "last_seen_version",
        ):
            for path, text in addon_sources():
                with self.subTest(token=token, file=path.name):
                    self.assertNotIn(token, text)

    def test_sources_were_actually_scanned(self):
        """Guard against the guards: an empty file list would pass everything."""
        sources = addon_sources()
        self.assertGreaterEqual(len(sources), 8)
        self.assertIn("sync_routine.py", [p.name for p, _ in sources])


if __name__ == "__main__":
    unittest.main()
