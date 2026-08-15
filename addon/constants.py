from aqt.qt import QApplication, QIcon, QStyle

# Config parameter keys and default values

AUTO_SYNC_CONFIG_NAME = "auto_sync_config"
ADDON_PACKAGE = __name__.split(".")[0]
CONFIG_SYNC_TIMEOUT = "sync timeout"
CONFIG_IDLE_SYNC_TIMEOUT = "idle sync timeout"
CONFIG_CONFIG_VERSION = "config version"
CONFIG_STRICTLY_AVOID_INTERRUPTIONS = "strictly avoid interruptions"
CONFIG_SYNC_ON_CHANGE_ONLY = "sync on change only"
CONFIG_IDLE_BEFORE_SYNC = "idle before sync"
CONFIG_DISABLE_INTERNET_CHECK = "disable internet check"
CONFIG_CONFLICT_RESOLUTION = "on conflict"

# Valid values for CONFIG_CONFLICT_RESOLUTION
CONFLICT_PROMPT = "prompt"      # Ask the user (Anki default)
CONFLICT_DOWNLOAD = "download"  # Always AnkiWeb -> local
CONFLICT_UPLOAD = "upload"      # Always local -> AnkiWeb

CONFIG_DEFAULT_CONFIG = {
    CONFIG_SYNC_TIMEOUT: 1,
    CONFIG_IDLE_SYNC_TIMEOUT: 0,
    CONFIG_CONFIG_VERSION: 6,
    CONFIG_STRICTLY_AVOID_INTERRUPTIONS: True,
    CONFIG_SYNC_ON_CHANGE_ONLY: True,
    CONFIG_IDLE_BEFORE_SYNC: 2,
    CONFIG_DISABLE_INTERNET_CHECK: False,
    CONFIG_CONFLICT_RESOLUTION: CONFLICT_PROMPT,
}

CONFIG_MINIMUMS = {
    CONFIG_SYNC_TIMEOUT: 1,
    CONFIG_IDLE_SYNC_TIMEOUT: 0,
    CONFIG_IDLE_BEFORE_SYNC: 1,
    CONFIG_CONFIG_VERSION: CONFIG_DEFAULT_CONFIG[CONFIG_CONFIG_VERSION],
}

CONFIG_MAXIMUMS = {
    CONFIG_IDLE_BEFORE_SYNC: 60,
}


def get_auto_sync_icon() -> QIcon:
    app = QApplication.instance()
    if app is None:
        return QIcon()
    return app.style().standardIcon(QStyle.StandardPixmap.SP_BrowserReload)
