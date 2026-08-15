import sys
import unittest
from unittest import mock

from tests import mock_aqt

aqt, mw = mock_aqt.install()

import aqt as aqt_mod
from addon.constants import CONFLICT_PROMPT, CONFLICT_DOWNLOAD, CONFLICT_UPLOAD
from addon.sync_routine import SyncRoutine


def make_routine(conflict=CONFLICT_PROMPT, config_extra=None):
    config = mock.Mock()
    config.get = mock.Mock(
        side_effect=lambda key: {
            "sync timeout": 1,
            "idle sync timeout": 0,
            "strictly avoid interruptions": True,
            "sync on change only": True,
            "idle before sync": 2,
            "disable internet check": False,
            "on conflict": conflict,
            **(config_extra or {}),
        }[key]
    )
    log = mock.Mock()
    return SyncRoutine(config, log)


class ConflictResolutionTest(unittest.TestCase):
    def setUp(self):
        aqt.sync.full_sync.reset_mock()
        aqt.sync.full_download.reset_mock()
        aqt.sync.full_upload.reset_mock()

    def _out(self, required):
        return mock_aqt.FakeSyncOutput(required=required)

    def test_prompt_ambiguous_calls_full_sync(self):
        r = make_routine(CONFLICT_PROMPT)
        out = self._out(mock_aqt.FakeSyncOutput.CONFLICT)
        r._resolve_conflict(mw, out, None)
        aqt.sync.full_sync.assert_called_once()
        aqt.sync.full_download.assert_not_called()
        aqt.sync.full_upload.assert_not_called()

    def test_forced_download_ambiguous(self):
        r = make_routine(CONFLICT_DOWNLOAD)
        out = self._out(mock_aqt.FakeSyncOutput.CONFLICT)
        r._resolve_conflict(mw, out, None)
        aqt.sync.full_download.assert_called_once()
        aqt.sync.full_sync.assert_not_called()

    def test_forced_upload_ambiguous(self):
        r = make_routine(CONFLICT_UPLOAD)
        out = self._out(mock_aqt.FakeSyncOutput.CONFLICT)
        r._resolve_conflict(mw, out, None)
        aqt.sync.full_upload.assert_called_once()
        aqt.sync.full_sync.assert_not_called()

    def test_full_download_respected_even_if_forced_upload(self):
        # Anki decided local is empty -> must download regardless of forced direction
        r = make_routine(CONFLICT_UPLOAD)
        out = self._out(mock_aqt.FakeSyncOutput.FULL_DOWNLOAD)
        r._resolve_conflict(mw, out, None)
        aqt.sync.full_download.assert_called_once()
        aqt.sync.full_upload.assert_not_called()

    def test_full_upload_respected_even_if_forced_download(self):
        r = make_routine(CONFLICT_DOWNLOAD)
        out = self._out(mock_aqt.FakeSyncOutput.FULL_UPLOAD)
        r._resolve_conflict(mw, out, None)
        aqt.sync.full_upload.assert_called_once()
        aqt.sync.full_download.assert_not_called()

    def test_prompt_full_download_goes_through_full_sync(self):
        # In prompt mode preserve Anki's confirm behavior via full_sync
        r = make_routine(CONFLICT_PROMPT)
        out = self._out(mock_aqt.FakeSyncOutput.FULL_DOWNLOAD)
        r._resolve_conflict(mw, out, None)
        aqt.sync.full_sync.assert_called_once()

    def test_server_usn_passed_when_media_enabled(self):
        r = make_routine(CONFLICT_DOWNLOAD)
        out = self._out(mock_aqt.FakeSyncOutput.CONFLICT)
        r._resolve_conflict(mw, out, None)
        args, kwargs = aqt.sync.full_download.call_args
        self.assertEqual(args[1], 5)  # server_usn


class ChangeDetectionTest(unittest.TestCase):
    def test_no_changes_returns_false(self):
        r = make_routine()
        r._last_synced_mod = 100
        mw.col.mod = 100
        self.assertFalse(r._has_changes_since_last_sync())

    def test_change_returns_true(self):
        r = make_routine()
        r._last_synced_mod = 100
        mw.col.mod = 101
        self.assertTrue(r._has_changes_since_last_sync())

    def test_exception_returns_true(self):
        r = make_routine()
        mw.col.mod = 100
        with mock.patch.object(mw.col, "mod", side_effect=Exception("boom")):
            self.assertTrue(r._has_changes_since_last_sync())


class BlockedReasonThrottleTest(unittest.TestCase):
    def test_same_reason_only_logged_once(self):
        r = make_routine()
        r._last_blocked_reason = None
        r.is_good_state()
        count_after_first = r.log_manager.write.call_count
        r.is_good_state()
        self.assertEqual(r.log_manager.write.call_count, count_after_first)


class SyncOnCloseTest(unittest.TestCase):
    def setUp(self):
        mw.col.sync_collection = mock.Mock()
        aqt.sync.full_sync.reset_mock()
        aqt.sync.full_download.reset_mock()
        aqt.sync.full_upload.reset_mock()

    def test_skips_when_no_changes_and_change_only(self):
        r = make_routine()
        r._last_synced_mod = 100
        mw.col.mod = 100
        r.sync_on_close()
        mw.col.sync_collection.assert_not_called()

    def test_syncs_when_changes_present(self):
        r = make_routine()
        r._last_synced_mod = 100
        mw.col.mod = 999
        mw.col.sync_collection = mock.Mock(return_value=mock_aqt.FakeSyncOutput(required=0))
        r.sync_on_close()
        mw.col.sync_collection.assert_called_once()

    def test_skips_conflict(self):
        r = make_routine()
        r._last_synced_mod = 100
        mw.col.mod = 999
        mw.col.sync_collection = mock.Mock(
            return_value=mock_aqt.FakeSyncOutput(required=mock_aqt.FakeSyncOutput.CONFLICT)
        )
        r.sync_on_close()
        aqt.sync.full_sync.assert_not_called()

    def test_resets_sync_in_progress_on_error(self):
        r = make_routine()
        r._last_synced_mod = 100
        mw.col.mod = 999
        mw.col.sync_collection = mock.Mock(side_effect=RuntimeError("net down"))
        r.sync_on_close()
        self.assertFalse(r.sync_in_progress)


class WindowStateRestoreGateTest(unittest.TestCase):
    def test_restore_runs_for_background_sync(self):
        r = make_routine()
        r._preserve_window_state = True
        with mock.patch.object(r, "_restore_window_state") as restore:
            r.sync_finished()
        restore.assert_called_once()
        self.assertFalse(r._preserve_window_state)

    def test_no_restore_for_manual_sync(self):
        # A manual Sync-button press never sets the flag -> no window restore
        r = make_routine()
        r._preserve_window_state = False
        with mock.patch.object(r, "_restore_window_state") as restore:
            r.sync_finished()
        restore.assert_not_called()


if __name__ == "__main__":
    unittest.main()
