"""Install lightweight fake ``aqt`` modules so the addon can be imported and
unit-tested without a running Anki instance."""
import sys
import types
from unittest import mock

_STATE = {"installed": False, "aqt": None, "mw": None}


def install():
    if _STATE["installed"]:
        return _STATE["aqt"], _STATE["mw"]
    aqt = types.ModuleType("aqt")

    # ---------- aqt.mw ----------
    timer = mock.Mock()
    timer.stop = mock.Mock()
    mw = mock.Mock()
    mw.progress.timer = mock.Mock(return_value=timer)
    mw.app = mock.Mock()
    mw.pm = mock.Mock()
    mw.pm.media_syncing_enabled = mock.Mock(return_value=True)
    mw.pm.sync_auth = mock.Mock(return_value="auth")
    mw.col = mock.Mock()
    mw.col.mod = 100
    mw.taskman = mock.Mock()
    mw.media_syncer = mock.Mock()
    mw.addonManager = mock.Mock()
    mw.state = "deckBrowser"
    aqt.mw = mw

    # ---------- aqt.qt ----------
    qt = types.ModuleType("aqt.qt")

    class QEvent:
        class Type:
            MouseButtonPress = 1
            MouseMove = 2
            KeyPress = 3

    class QObject:
        pass

    class QApplication:
        active = None

        @classmethod
        def activeWindow(cls):
            return cls.active

        @staticmethod
        def instance():
            return None

    class QIcon:
        pass

    class QStyle:
        class StandardPixmap:
            SP_BrowserReload = "reload"

    # Widgets/symbols referenced by main.py and options_dialog.py
    class _Widget(mock.Mock):
        pass

    for _name in (
        "QAction",
        "QCheckBox",
        "QCloseEvent",
        "QComboBox",
        "QDialog",
        "QGridLayout",
        "QHBoxLayout",
        "QLabel",
        "QPixmap",
        "QPushButton",
        "QScrollArea",
        "QSpinBox",
        "QTabWidget",
        "QTextEdit",
        "QVBoxLayout",
        "QWidget",
    ):
        setattr(qt, _name, type(_name, (_Widget,), {}))

    class Qt:
        class AlignmentFlag:
            AlignRight = 1
            AlignTrailing = 2
            AlignVCenter = 4

        class AspectRatioMode:
            KeepAspectRatio = 0

        class TransformationMode:
            SmoothTransformation = 0

        class ScrollBarPolicy:
            ScrollBarAlwaysOff = 0

        class TextInteractionFlag:
            TextSelectableByMouse = 0

        class TextFormat:
            MarkdownText = 1
            RichText = 2

    qt.Qt = Qt

    qt.QEvent = QEvent
    qt.QObject = QObject
    qt.QApplication = QApplication
    qt.QIcon = QIcon
    qt.QStyle = QStyle
    aqt.qt = qt

    # ---------- aqt.dialogs ----------
    dialogs = types.ModuleType("aqt.dialogs")
    dialogs.allClosed = mock.Mock(return_value=True)
    dialogs._dialogs = {}
    aqt.dialogs = dialogs

    # ---------- aqt.gui_hooks ----------
    gui_hooks = types.ModuleType("aqt.gui_hooks")
    for name in (
        "sync_will_start",
        "sync_did_finish",
        "profile_did_open",
        "profile_will_close",
        "collection_will_temporarily_close",
    ):
        hook = mock.Mock()
        hook.append = mock.Mock()
        hook.remove = mock.Mock()
        setattr(gui_hooks, name, hook)
    aqt.gui_hooks = gui_hooks

    # ---------- aqt.utils ----------
    utils = types.ModuleType("aqt.utils")
    utils.showText = mock.Mock()
    utils.openLink = mock.Mock()
    aqt.utils = utils

    # ---------- aqt.sync ----------
    sync = types.ModuleType("aqt.sync")
    sync.handle_sync_error = mock.Mock()
    sync.full_sync = mock.Mock()
    sync.full_download = mock.Mock()
    sync.full_upload = mock.Mock()
    aqt.sync = sync

    # ---------- aqt.main / aqt.webview ----------
    aqt.main = types.ModuleType("aqt.main")

    class AnkiWebView(mock.Mock):
        pass

    webview = types.ModuleType("aqt.webview")
    webview.AnkiWebView = AnkiWebView
    aqt.webview = webview

    # ---------- register ----------
    for name, mod in (
        ("aqt", aqt),
        ("aqt.qt", qt),
        ("aqt.dialogs", dialogs),
        ("aqt.gui_hooks", gui_hooks),
        ("aqt.utils", utils),
        ("aqt.sync", sync),
        ("aqt.main", aqt.main),
        ("aqt.webview", aqt.webview),
    ):
        sys.modules[name] = mod

    _STATE["installed"] = True
    _STATE["aqt"] = aqt
    _STATE["mw"] = mw
    return aqt, mw


class FakeSyncOutput:
    """Mirrors the protobuf SyncCollectionResponse surface used by the addon."""

    NO_CHANGES = 0
    FULL_DOWNLOAD = 1
    FULL_UPLOAD = 2
    CONFLICT = 3

    def __init__(self, required=NO_CHANGES):
        self.required = required
        self.server_media_usn = 5
        self.server_message = ""
        self.host_number = 1
        self.new_endpoint = ""
