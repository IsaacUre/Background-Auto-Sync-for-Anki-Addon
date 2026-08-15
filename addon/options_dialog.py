from aqt.qt import (
    QApplication,
    QCheckBox,
    QCloseEvent,
    QComboBox,
    QDialog,
    QHBoxLayout,
    QPushButton,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from .sync_routine import SyncRoutine
from .config import AutoSyncConfigManager
from .constants import (
    CONFIG_IDLE_BEFORE_SYNC,
    CONFIG_IDLE_SYNC_TIMEOUT,
    CONFIG_STRICTLY_AVOID_INTERRUPTIONS,
    CONFIG_SYNC_ON_CHANGE_ONLY,
    CONFIG_SYNC_TIMEOUT,
    CONFIG_DISABLE_INTERNET_CHECK,
    CONFIG_CONFLICT_RESOLUTION,
    get_auto_sync_icon,
)
from .log_window import LogManager
from .tabs import settings_tab, logs_tab, support_tab


class AutoSyncOptionsDialog(QDialog):
    def __init__(self, config: AutoSyncConfigManager, sync_routine: SyncRoutine, log_manager: LogManager):
        super(AutoSyncOptionsDialog, self).__init__()
        self.config = config
        self.sync_routine: SyncRoutine = sync_routine
        self.log_manager = log_manager

        self.kofi_widget = None
        self.log_output = None

        # set up UI elements
        self.sync_timeout_spinbox = QSpinBox()
        self.idle_sync_timeout_spinbox = QSpinBox()
        self.sync_on_change_only_checkbox = QCheckBox()
        self.idle_before_sync_spinbox = QSpinBox()
        self.strictly_avoid_interruptions_checkbox = QCheckBox()
        self.disable_internet_check_checkbox = QCheckBox()
        self.conflict_resolution_combo = QComboBox()

        self.setup_ui()

    @staticmethod
    def _set_minutes_suffix(spinbox: QSpinBox, value: int):
        if value == 0:
            spinbox.setSuffix("")
        else:
            spinbox.setSuffix(" minute" if value == 1 else " minutes")

    def change_sync_timeout(self, value):
        self._set_minutes_suffix(self.sync_timeout_spinbox, value)
        self.config.set(CONFIG_SYNC_TIMEOUT, value)
        self.sync_routine.reload_config()

    def change_idle_sync_timeout(self, value):
        self._set_minutes_suffix(self.idle_sync_timeout_spinbox, value)
        self.config.set(CONFIG_IDLE_SYNC_TIMEOUT, value)
        self.sync_routine.reload_config()

    def change_strictly_avoid_interruption(self, enabled):
        self.config.set(CONFIG_STRICTLY_AVOID_INTERRUPTIONS, bool(enabled))
        self.sync_routine.reload_config()

    def change_sync_on_change_only(self, enabled):
        self.config.set(CONFIG_SYNC_ON_CHANGE_ONLY, bool(enabled))
        self.sync_routine.reload_config()
        # Enable/disable the relevant spinboxes based on this
        self.idle_before_sync_spinbox.setEnabled(bool(enabled))
        self.sync_timeout_spinbox.setEnabled(not bool(enabled))
        self.idle_sync_timeout_spinbox.setEnabled(not bool(enabled))

    def change_idle_before_sync(self, value):
        self._set_minutes_suffix(self.idle_before_sync_spinbox, value)
        self.config.set(CONFIG_IDLE_BEFORE_SYNC, value)
        self.sync_routine.reload_config()

    def change_disable_internet_check(self, enabled):
        self.config.set(CONFIG_DISABLE_INTERNET_CHECK, bool(enabled))
        self.sync_routine.reload_config()

    def change_conflict_resolution(self, index):
        value = self.conflict_resolution_combo.itemData(index)
        self.config.set(CONFIG_CONFLICT_RESOLUTION, value)
        self.sync_routine.reload_config()

    def setup_ui(self):
        self.setWindowTitle('Auto Sync Options')
        self.setWindowIcon(get_auto_sync_icon())
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)

        # Main layout with tab widget
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        tab_widget = QTabWidget()
        main_layout.addWidget(tab_widget)

        # --- Settings Tab ---
        tab_widget.addTab(settings_tab.build(self), "Settings")

        # --- Logs Tab ---
        tab_widget.addTab(logs_tab.build(self), "Logs")

        # --- Support Tab ---
        tab_widget.addTab(support_tab.build(self), "Support")

        # --- Bottom buttons (shared across tabs) ---
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(0, 5, 0, 0)

        close_button = QPushButton("Close")
        close_button.clicked.connect(lambda *args: self.close())

        btn_layout.addStretch()
        btn_layout.addWidget(close_button)
        main_layout.addLayout(btn_layout)

    def _copy_to_clipboard(self, text):
        cb = QApplication.clipboard()
        cb.setText(text)

    def refresh_log(self):
        """Refresh the inline log and scroll to the bottom"""
        if self.log_output:
            self.log_output.setPlainText(self.log_manager.read())
            self.log_output.verticalScrollBar().setValue(
                self.log_output.verticalScrollBar().maximum()
            )

    def on_reset_to_defaults_call(self):
        from .constants import CONFIG_DEFAULT_CONFIG
        for key, value in CONFIG_DEFAULT_CONFIG.items():
            self.config.set(key, value)

        self.sync_timeout_spinbox.blockSignals(True)
        self.idle_sync_timeout_spinbox.blockSignals(True)
        self.strictly_avoid_interruptions_checkbox.blockSignals(True)
        self.sync_on_change_only_checkbox.blockSignals(True)
        self.idle_before_sync_spinbox.blockSignals(True)
        self.disable_internet_check_checkbox.blockSignals(True)
        self.conflict_resolution_combo.blockSignals(True)

        self.sync_timeout_spinbox.setValue(self.config.get(CONFIG_SYNC_TIMEOUT))
        self.idle_sync_timeout_spinbox.setValue(self.config.get(CONFIG_IDLE_SYNC_TIMEOUT))
        self.strictly_avoid_interruptions_checkbox.setChecked(self.config.get(CONFIG_STRICTLY_AVOID_INTERRUPTIONS))
        self.sync_on_change_only_checkbox.setChecked(self.config.get(CONFIG_SYNC_ON_CHANGE_ONLY))
        self.idle_before_sync_spinbox.setValue(self.config.get(CONFIG_IDLE_BEFORE_SYNC))
        self.disable_internet_check_checkbox.setChecked(self.config.get(CONFIG_DISABLE_INTERNET_CHECK))
        reset_idx = self.conflict_resolution_combo.findData(self.config.get(CONFIG_CONFLICT_RESOLUTION))
        if reset_idx >= 0:
            self.conflict_resolution_combo.setCurrentIndex(reset_idx)

        self.idle_before_sync_spinbox.setEnabled(self.config.get(CONFIG_SYNC_ON_CHANGE_ONLY))
        self.sync_timeout_spinbox.setEnabled(not self.config.get(CONFIG_SYNC_ON_CHANGE_ONLY))
        self.idle_sync_timeout_spinbox.setEnabled(not self.config.get(CONFIG_SYNC_ON_CHANGE_ONLY))

        self.sync_timeout_spinbox.blockSignals(False)
        self.idle_sync_timeout_spinbox.blockSignals(False)
        self.strictly_avoid_interruptions_checkbox.blockSignals(False)
        self.sync_on_change_only_checkbox.blockSignals(False)
        self.idle_before_sync_spinbox.blockSignals(False)
        self.disable_internet_check_checkbox.blockSignals(False)
        self.conflict_resolution_combo.blockSignals(False)

        self.sync_routine.reload_config()

    def closeEvent(self, a0: QCloseEvent) -> None:
        self.log_manager.unregister(self)
        if self.kofi_widget:
            self.kofi_widget.cleanup()
            self.kofi_widget = None
        super().closeEvent(a0)


def on_options_call(conf, sync_routine, log_manager):
    """Open settings dialog"""
    dialog = AutoSyncOptionsDialog(conf, sync_routine, log_manager)
    dialog.exec()
