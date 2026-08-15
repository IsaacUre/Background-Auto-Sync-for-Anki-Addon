import sys
import unittest
from unittest import mock

from tests import mock_aqt

mock_aqt.install()

from addon.config import AutoSyncConfigManager
from addon.constants import (
    CONFIG_CONFLICT_RESOLUTION,
    CONFIG_DEFAULT_CONFIG,
    CONFLICT_PROMPT,
    CONFLICT_DOWNLOAD,
    CONFLICT_UPLOAD,
)


def make_config(raw=None, version=6):
    mw = mock.Mock()
    mw.col.get_config = mock.Mock(return_value=raw if raw is not None else {})
    mw.col.set_config = mock.Mock()
    if raw is not None:
        pass
    return AutoSyncConfigManager(mw)


class ConfigMigrationTest(unittest.TestCase):
    def test_old_config_gets_conflict_key(self):
        # version 5 config (no conflict key) should gain the prompt default
        old = {"config version": 5, "sync timeout": 1}
        cfg = make_config(old)
        self.assertEqual(cfg.get(CONFIG_CONFLICT_RESOLUTION), CONFLICT_PROMPT)

    def test_default_has_conflict_prompt(self):
        cfg = make_config()
        self.assertEqual(cfg.get(CONFIG_CONFLICT_RESOLUTION), CONFLICT_PROMPT)


class ConfigSanitizeTest(unittest.TestCase):
    def test_valid_values_kept(self):
        for val in (CONFLICT_PROMPT, CONFLICT_DOWNLOAD, CONFLICT_UPLOAD):
            cfg = make_config({CONFIG_CONFLICT_RESOLUTION: val, "config version": 6})
            self.assertEqual(cfg.get(CONFIG_CONFLICT_RESOLUTION), val)

    def test_invalid_value_reset_to_prompt(self):
        cfg = make_config({CONFIG_CONFLICT_RESOLUTION: "bogus", "config version": 6})
        self.assertEqual(cfg.get(CONFIG_CONFLICT_RESOLUTION), CONFLICT_PROMPT)

    def test_set_valid_value(self):
        cfg = make_config()
        cfg.set(CONFIG_CONFLICT_RESOLUTION, CONFLICT_DOWNLOAD)
        self.assertEqual(cfg.get(CONFIG_CONFLICT_RESOLUTION), CONFLICT_DOWNLOAD)

    def test_int_keys_exclude_str_key(self):
        self.assertNotIn(CONFIG_CONFLICT_RESOLUTION, AutoSyncConfigManager._INT_CONFIG_KEYS)
        self.assertIn(CONFIG_CONFLICT_RESOLUTION, AutoSyncConfigManager._STR_CONFIG_KEYS)

    def test_defaults_are_saved(self):
        cfg = make_config()
        # set_config should have been called with a dict containing the conflict key
        saved = cfg._save.call_args if hasattr(cfg._save, "call_args") else None
        mw = cfg.mw
        args, _ = mw.col.set_config.call_args
        self.assertEqual(args[0], "auto_sync_config")
        self.assertIn(CONFIG_CONFLICT_RESOLUTION, args[1])
        self.assertEqual(args[1][CONFIG_CONFLICT_RESOLUTION], CONFIG_DEFAULT_CONFIG[CONFIG_CONFLICT_RESOLUTION])


if __name__ == "__main__":
    unittest.main()
