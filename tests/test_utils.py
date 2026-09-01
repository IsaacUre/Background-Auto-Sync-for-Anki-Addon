import unittest
from unittest import mock

from tests import mock_aqt

aqt, mw = mock_aqt.install()

from addon.utils import (
    DEFAULT_SYNC_HOST,
    DEFAULT_SYNC_PORT,
    sync_server_reachable,
    sync_target,
)


def set_endpoint(value):
    mw.pm.sync_endpoint = mock.Mock(return_value=value)


class SyncTargetTests(unittest.TestCase):
    def tearDown(self):
        # Leave the harness as install() left it: a bare Mock, not a string.
        mw.pm.sync_endpoint = mock.Mock()

    def test_defaults_to_ankiweb_when_endpoint_is_not_a_string(self):
        # Under the mock harness sync_endpoint() returns a Mock, so the
        # isinstance guard is what keeps this deterministic.
        set_endpoint(mock.Mock())
        self.assertEqual(sync_target(), (DEFAULT_SYNC_HOST, DEFAULT_SYNC_PORT))

    def test_defaults_when_endpoint_missing_or_blank(self):
        for value in (None, "", "   "):
            with self.subTest(value=value):
                set_endpoint(value)
                self.assertEqual(sync_target(), (DEFAULT_SYNC_HOST, DEFAULT_SYNC_PORT))

    def test_defaults_when_reading_the_endpoint_raises(self):
        mw.pm.sync_endpoint = mock.Mock(side_effect=RuntimeError("no profile"))
        self.assertEqual(sync_target(), (DEFAULT_SYNC_HOST, DEFAULT_SYNC_PORT))

    def test_reads_custom_https_endpoint_with_explicit_port(self):
        set_endpoint("https://sync.example.com:8080/sync/")
        self.assertEqual(sync_target(), ("sync.example.com", 8080))

    def test_https_without_port_uses_443(self):
        set_endpoint("https://sync.example.com/")
        self.assertEqual(sync_target(), ("sync.example.com", 443))

    def test_http_without_port_uses_80(self):
        set_endpoint("http://sync.example.com/")
        self.assertEqual(sync_target(), ("sync.example.com", 80))

    def test_bare_host_without_scheme(self):
        set_endpoint("sync.example.com")
        self.assertEqual(sync_target(), ("sync.example.com", DEFAULT_SYNC_PORT))

    def test_malformed_port_falls_back_instead_of_raising(self):
        set_endpoint("https://sync.example.com:not-a-port/")
        host, port = sync_target()
        self.assertEqual(port, DEFAULT_SYNC_PORT)


class ReachabilityTests(unittest.TestCase):
    def setUp(self):
        set_endpoint("https://ankiweb.net/")

    def tearDown(self):
        mw.pm.sync_endpoint = mock.Mock()

    def test_true_when_the_connection_succeeds(self):
        with mock.patch("addon.utils.socket.create_connection"):
            self.assertTrue(sync_server_reachable())

    def test_false_when_the_connection_fails(self):
        with mock.patch("addon.utils.socket.create_connection", side_effect=OSError):
            self.assertFalse(sync_server_reachable())

    def test_probes_the_configured_sync_server(self):
        set_endpoint("https://sync.example.com:8080/")
        with mock.patch("addon.utils.socket.create_connection") as conn:
            sync_server_reachable()
        self.assertEqual(conn.call_args.args[0], ("sync.example.com", 8080))

    def test_explicit_arguments_win(self):
        with mock.patch("addon.utils.socket.create_connection") as conn:
            sync_server_reachable(host="127.0.0.1", port=1234)
        self.assertEqual(conn.call_args.args[0], ("127.0.0.1", 1234))

    def test_never_contacts_a_third_party_resolver(self):
        """Regression guard for the privacy change.

        The probe used to hit 8.8.8.8 and only fall back to AnkiWeb. It must
        now only ever touch the server the collection actually syncs with,
        including when that server is unreachable and every attempt fails.
        """
        with mock.patch(
            "addon.utils.socket.create_connection", side_effect=OSError
        ) as conn:
            self.assertFalse(sync_server_reachable())
        hosts = [call.args[0][0] for call in conn.call_args_list]
        self.assertEqual(hosts, ["ankiweb.net"])
        self.assertNotIn("8.8.8.8", hosts)

    def test_only_one_connection_attempt_is_made(self):
        # The old implementation tried a second host on failure.
        with mock.patch(
            "addon.utils.socket.create_connection", side_effect=OSError
        ) as conn:
            sync_server_reachable()
        self.assertEqual(conn.call_count, 1)


if __name__ == "__main__":
    unittest.main()
