from aqt.qt import QApplication, QIcon, QStyle

# Config parameter keys and default values

AUTO_SYNC_CONFIG_NAME = "auto_sync_config"
CONFIG_SYNC_TIMEOUT = "sync timeout"
CONFIG_IDLE_SYNC_TIMEOUT = "idle sync timeout"
CONFIG_CONFIG_VERSION = "config version"
CONFIG_AVOID_INTERRUPTION_DIALOGS = "avoid sync when dialogs open"
CONFIG_AVOID_DIALOG_LIST = "avoid dialogs list"
CONFIG_AVOID_DIALOGS_TIMEOUT = "avoid dialogs timeout"
CONFIG_AVOID_INTERRUPTION_FOCUS = "avoid sync when main window focused"
CONFIG_AVOID_INTERRUPTION_REVIEW = "avoid sync while reviewing"
CONFIG_AVOID_REVIEW_TIMEOUT = "avoid review timeout"
CONFIG_AVOID_OVERRIDE_TIMEOUT = "global avoid override timeout"
CONFIG_SYNC_ON_CHANGE_ONLY = "sync on change only"
CONFIG_IDLE_BEFORE_SYNC = "idle before sync"
CONFIG_IDLE_SYNC_FOCUSED_TIMEOUT = "idle sync focused timeout"
CONFIG_DISABLE_INTERNET_CHECK = "disable internet check"
CONFIG_CONFLICT_RESOLUTION = "on conflict"

# Window types that can block sync when open (label, aqt dialog registry name)
DIALOG_WINDOW_OPTIONS = (
    ("Card browser", "Browser"),
    ("Add cards", "AddCards"),
    ("Edit current card", "EditCurrent"),
    ("Deck stats", "DeckStats"),
    ("Preferences", "Preferences"),
)

# Default window types that block sync when open
DEFAULT_AVOID_DIALOG_LIST = [name for _, name in DIALOG_WINDOW_OPTIONS]

# Valid values for CONFIG_CONFLICT_RESOLUTION
CONFLICT_PROMPT = "prompt"      # Ask the user (Anki default)
CONFLICT_DOWNLOAD = "download"  # Always AnkiWeb -> local
CONFLICT_UPLOAD = "upload"      # Always local -> AnkiWeb

CONFIG_DEFAULT_CONFIG = {
    CONFIG_SYNC_TIMEOUT: 1,
    CONFIG_IDLE_SYNC_TIMEOUT: 0,
    CONFIG_CONFIG_VERSION: 11,
    CONFIG_AVOID_INTERRUPTION_DIALOGS: True,
    CONFIG_AVOID_DIALOG_LIST: DEFAULT_AVOID_DIALOG_LIST,
    CONFIG_AVOID_DIALOGS_TIMEOUT: 0,
    CONFIG_AVOID_INTERRUPTION_FOCUS: True,
    CONFIG_AVOID_INTERRUPTION_REVIEW: True,
    CONFIG_AVOID_REVIEW_TIMEOUT: 0,
    CONFIG_AVOID_OVERRIDE_TIMEOUT: 10,
    CONFIG_SYNC_ON_CHANGE_ONLY: True,
    CONFIG_IDLE_BEFORE_SYNC: 2,
    CONFIG_IDLE_SYNC_FOCUSED_TIMEOUT: 5,
    CONFIG_DISABLE_INTERNET_CHECK: False,
    CONFIG_CONFLICT_RESOLUTION: CONFLICT_PROMPT,
}

CONFIG_MINIMUMS = {
    CONFIG_SYNC_TIMEOUT: 1,
    CONFIG_IDLE_SYNC_TIMEOUT: 0,
    CONFIG_IDLE_BEFORE_SYNC: 1,
    CONFIG_IDLE_SYNC_FOCUSED_TIMEOUT: 0,
    CONFIG_AVOID_DIALOGS_TIMEOUT: 0,
    CONFIG_AVOID_REVIEW_TIMEOUT: 0,
    CONFIG_AVOID_OVERRIDE_TIMEOUT: 0,
    CONFIG_CONFIG_VERSION: CONFIG_DEFAULT_CONFIG[CONFIG_CONFIG_VERSION],
}

CONFIG_MAXIMUMS = {
    CONFIG_IDLE_BEFORE_SYNC: 60,
    CONFIG_IDLE_SYNC_FOCUSED_TIMEOUT: 120,
    CONFIG_AVOID_DIALOGS_TIMEOUT: 120,
    CONFIG_AVOID_REVIEW_TIMEOUT: 120,
    CONFIG_AVOID_OVERRIDE_TIMEOUT: 120,
}


def get_auto_sync_icon() -> QIcon:
    app = QApplication.instance()
    if app is None:
        return QIcon()
    return app.style().standardIcon(QStyle.StandardPixmap.SP_BrowserReload)
