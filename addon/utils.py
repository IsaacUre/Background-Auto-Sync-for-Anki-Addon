import socket
from urllib.parse import urlsplit

from aqt.qt import QScrollArea, QWidget

DEFAULT_SYNC_HOST = "ankiweb.net"
DEFAULT_SYNC_PORT = 443


def wrap_in_scroll(content: QWidget) -> QWidget:
    """Wrap a widget in a scroll area that only shows scrollbars when needed."""
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QScrollArea.Shape.NoFrame)
    scroll.setWidget(content)
    return scroll


def sync_target(
    default_host: str = DEFAULT_SYNC_HOST,
    default_port: int = DEFAULT_SYNC_PORT,
) -> tuple[str, int]:
    """Return (host, port) of the server this collection actually syncs with.

    Anki supports self-hosted sync servers, so the configured endpoint is read
    from the profile and AnkiWeb is only the fallback. Any failure to read or
    parse it falls back to the default rather than raising, because this runs
    on the sync timer and must never break syncing.
    """
    try:
        from aqt import mw

        endpoint = mw.pm.sync_endpoint()
    except Exception:
        endpoint = None

    # Under tests mw.pm is a Mock, so sync_endpoint() is not a string.
    if not isinstance(endpoint, str) or not endpoint.strip():
        return default_host, default_port

    raw = endpoint.strip()
    # urlsplit needs a scheme or leading // to find a host; accept a bare host.
    parts = urlsplit(raw if "//" in raw else f"//{raw}")

    host = parts.hostname or default_host
    try:
        port = parts.port
    except ValueError:
        # Malformed port in the URL - fall back rather than raise.
        port = None
    if not port:
        port = 80 if parts.scheme == "http" else default_port
    return host, port


def sync_server_reachable(host=None, port=None, timeout=3) -> bool:
    """Whether the sync server accepts a TCP connection.

    This probes the sync server itself rather than an unrelated third party.
    Asking a public DNS resolver whether it is up answers a different question
    than the one that matters here - if the sync server is unreachable there is
    nothing useful to do regardless - and it would disclose the user's sync
    activity to an operator with no part in it.

    Nothing is transmitted: the socket is opened and closed immediately.
    """
    target_host, target_port = sync_target()
    if host is None:
        host = target_host
    if port is None:
        port = target_port

    try:
        with socket.create_connection((host, port), timeout=timeout):
            pass
        return True
    except OSError:
        return False
