from aqt import mw
from .constants import (
    AUTO_SYNC_CONFIG_NAME,
    CONFIG_AVOID_INTERRUPTION_DIALOGS,
    CONFIG_AVOID_DIALOG_LIST,
    CONFIG_AVOID_DIALOGS_TIMEOUT,
    CONFIG_AVOID_INTERRUPTION_FOCUS,
    CONFIG_AVOID_INTERRUPTION_REVIEW,
    CONFIG_AVOID_REVIEW_TIMEOUT,
    CONFIG_AVOID_OVERRIDE_TIMEOUT,
    CONFIG_SYNC_ON_CHANGE_ONLY,
    CONFIG_DEFAULT_CONFIG,
    CONFIG_MAXIMUMS,
    CONFIG_MINIMUMS,
    CONFIG_IDLE_SYNC_TIMEOUT,
    CONFIG_IDLE_BEFORE_SYNC,
    CONFIG_IDLE_SYNC_FOCUSED_TIMEOUT,
    CONFIG_CONFIG_VERSION,
    CONFIG_DISABLE_INTERNET_CHECK,
    CONFIG_CONFLICT_RESOLUTION,
    DEFAULT_AVOID_DIALOG_LIST,
    DIALOG_WINDOW_OPTIONS,
    CONFLICT_PROMPT,
    CONFLICT_DOWNLOAD,
    CONFLICT_UPLOAD,
)


class AutoSyncConfigManager:
    """Manages accessing the addons configuration in Ankis config storage"""

    _BOOL_CONFIG_KEYS = frozenset(
        {
            CONFIG_AVOID_INTERRUPTION_DIALOGS,
            CONFIG_AVOID_INTERRUPTION_FOCUS,
            CONFIG_AVOID_INTERRUPTION_REVIEW,
            CONFIG_SYNC_ON_CHANGE_ONLY,
            CONFIG_DISABLE_INTERNET_CHECK,
        }
    )

    _LIST_CONFIG_KEYS = frozenset({CONFIG_AVOID_DIALOG_LIST})

    _STR_CONFIG_KEYS = frozenset({CONFIG_CONFLICT_RESOLUTION})

    _STR_CONFIG_ALLOWED = frozenset({CONFLICT_PROMPT, CONFLICT_DOWNLOAD, CONFLICT_UPLOAD})

    _INT_CONFIG_KEYS = frozenset(CONFIG_DEFAULT_CONFIG) - _BOOL_CONFIG_KEYS - _STR_CONFIG_KEYS - _LIST_CONFIG_KEYS

    def __init__(self, mw: mw):
        """Load the config with default return value and in case it's the first run, save it to Anki"""
        self.mw = mw
        self.col = mw.col

        # Load existing config or use default
        current_config = self.col.get_config(
            AUTO_SYNC_CONFIG_NAME,
            default=dict(CONFIG_DEFAULT_CONFIG),
        )
        if not isinstance(current_config, dict):
            current_config = {}

        # Migration for version 4: safer server defaults with idle sync off
        if current_config.get(CONFIG_CONFIG_VERSION, 0) < 4:
            current_config[CONFIG_IDLE_SYNC_TIMEOUT] = 0
            current_config[CONFIG_SYNC_ON_CHANGE_ONLY] = True
            current_config[CONFIG_IDLE_BEFORE_SYNC] = 2
            current_config[CONFIG_CONFIG_VERSION] = 4

        # Migration for version 5: add option to disable internet check
        if current_config.get(CONFIG_CONFIG_VERSION, 0) < 5:
            current_config[CONFIG_DISABLE_INTERNET_CHECK] = False
            current_config[CONFIG_CONFIG_VERSION] = 5

        # Migration for version 6: add conflict resolution direction option
        if current_config.get(CONFIG_CONFIG_VERSION, 0) < 6:
            current_config[CONFIG_CONFLICT_RESOLUTION] = CONFLICT_PROMPT
            current_config[CONFIG_CONFIG_VERSION] = 6

        # Migration for version 7: add idle-sync-while-focused grace timeout
        if current_config.get(CONFIG_CONFIG_VERSION, 0) < 7:
            current_config[CONFIG_IDLE_SYNC_FOCUSED_TIMEOUT] = 0
            current_config[CONFIG_CONFIG_VERSION] = 7

        # Migration for version 8: split the single interruption toggle into
        # three independent per-condition toggles
        if current_config.get(CONFIG_CONFIG_VERSION, 0) < 8:
            strict_was = current_config.get("strictly avoid interruptions", True)
            current_config[CONFIG_AVOID_INTERRUPTION_DIALOGS] = strict_was
            current_config[CONFIG_AVOID_INTERRUPTION_FOCUS] = strict_was
            current_config[CONFIG_AVOID_INTERRUPTION_REVIEW] = strict_was
            current_config[CONFIG_CONFIG_VERSION] = 8

        # Migration for version 9: add per-window-type sub-settings for dialogs
        if current_config.get(CONFIG_CONFIG_VERSION, 0) < 9:
            current_config[CONFIG_AVOID_DIALOG_LIST] = list(DEFAULT_AVOID_DIALOG_LIST)
            current_config[CONFIG_CONFIG_VERSION] = 9

        # Migration for version 10: per-interruption override timeouts
        if current_config.get(CONFIG_CONFIG_VERSION, 0) < 10:
            current_config[CONFIG_AVOID_DIALOGS_TIMEOUT] = 0
            current_config[CONFIG_AVOID_REVIEW_TIMEOUT] = 0
            current_config[CONFIG_CONFIG_VERSION] = 10

        # Migration for version 11: global override timeout
        if current_config.get(CONFIG_CONFIG_VERSION, 0) < 11:
            current_config[CONFIG_AVOID_OVERRIDE_TIMEOUT] = 10
            current_config[CONFIG_CONFIG_VERSION] = 11

        # Merge default config into current config for any missing keys (migrations)
        self.config = self._sanitize_config(current_config)

        # Save merged config
        self._save()

    def _save(self):
        self.col.set_config(AUTO_SYNC_CONFIG_NAME, self.config)

    def _sanitize_config(self, raw_config):
        merged = {**CONFIG_DEFAULT_CONFIG, **raw_config}
        sanitized = {}

        for key, default_value in CONFIG_DEFAULT_CONFIG.items():
            value = merged.get(key, default_value)
            if key in self._BOOL_CONFIG_KEYS:
                value = self._coerce_bool(value, default_value)
            elif key in self._STR_CONFIG_KEYS:
                value = value if value in self._STR_CONFIG_ALLOWED else default_value
            elif key in self._LIST_CONFIG_KEYS:
                value = self._coerce_dialog_list(value, default_value)
            elif key in self._INT_CONFIG_KEYS:
                value = self._coerce_int(value, default_value)

            minimum = CONFIG_MINIMUMS.get(key)
            if minimum is not None:
                value = max(minimum, value)

            maximum = CONFIG_MAXIMUMS.get(key)
            if maximum is not None:
                value = min(maximum, value)

            sanitized[key] = value

        return sanitized

    @staticmethod
    def _coerce_dialog_list(value, default):
        valid = {name for _, name in DIALOG_WINDOW_OPTIONS}
        if not isinstance(value, (list, tuple, set)):
            return list(default)
        result = [name for name in value if name in valid]
        return result or list(default)

    @staticmethod
    def _coerce_bool(value, default):
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"1", "true", "yes", "on"}:
                return True
            if normalized in {"0", "false", "no", "off"}:
                return False
            return default
        if isinstance(value, (int, float)):
            return bool(value)
        return default

    @staticmethod
    def _coerce_int(value, default):
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    def get(self, key):
        """get the value of the given config key"""
        return self.config[key]

    def set(self, key, val):
        """set the value of the given config key"""
        if key not in CONFIG_DEFAULT_CONFIG:
            raise KeyError(f"Unknown config key: {key}")
        updated_config = dict(self.config)
        updated_config[key] = val
        self.config = self._sanitize_config(updated_config)
        self._save()
