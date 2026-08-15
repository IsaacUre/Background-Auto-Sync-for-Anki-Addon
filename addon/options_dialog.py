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
    CONFIG_IDLE_SYNC_FOCUSED_TIMEOUT,
    CONFIG_IDLE_SYNC_TIMEOUT,
    CONFIG_AVOID_INTERRUPTION_DIALOGS,
    CONFIG_AVOID_DIALOG_LIST,
    CONFIG_AVOID_DIALOGS_TIMEOUT,
    CONFIG_AVOID_INTERRUPTION_FOCUS,
    CONFIG_AVOID_INTERRUPTION_REVIEW,
    CONFIG_AVOID_REVIEW_TIMEOUT,
    CONFIG_AVOID_OVERRIDE_TIMEOUT,
    CONFIG_SYNC_ON_CHANGE_ONLY,
    CONFIG_SYNC_TIMEOUT,
    CONFIG_DISABLE_INTERNET_CHECK,
    CONFIG_CONFLICT_RESOLUTION,
    get_auto_sync_icon,
)
from .tabs import settings_tab, logs_tab, support_tab
from .tabs.logs_tab import LogManager

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
        self.idle_sync_focused_timeout_spinbox = QSpinBox()
        self.avoid_dialogs_checkbox = QCheckBox()
        self.avoid_dialogs_timeout_spinbox = QSpinBox()
        self.avoid_focus_checkbox = QCheckBox()
        self.avoid_review_checkbox = QCheckBox()
        self.avoid_review_timeout_spinbox = QSpinBox()
        self.avoid_override_timeout_spinbox = QSpinBox()
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

    def change_avoid_dialogs(self, enabled):
        self.config.set(CONFIG_AVOID_INTERRUPTION_DIALOGS, bool(enabled))
        self.sync_routine.reload_config()
        self.avoid_dialogs_timeout_spinbox.setEnabled(bool(enabled))
        for _, checkbox in getattr(self, "avoid_dialog_sub_checkboxes", []):
            checkbox.setEnabled(bool(enabled))

    def change_avoid_dialogs_timeout(self, value):
        self._set_minutes_suffix(self.avoid_dialogs_timeout_spinbox, value)
        self.config.set(CONFIG_AVOID_DIALOGS_TIMEOUT, value)
        self.sync_routine.reload_config()

    def change_avoid_dialog_type(self, name, checked):
        current = list(self.config.get(CONFIG_AVOID_DIALOG_LIST))
        if checked and name not in current:
            current.append(name)
        elif not checked and name in current:
            current.remove(name)
        self.config.set(CONFIG_AVOID_DIALOG_LIST, current)
        self.sync_routine.reload_config()

    def change_avoid_focus(self, enabled):
        self.config.set(CONFIG_AVOID_INTERRUPTION_FOCUS, bool(enabled))
        self.sync_routine.reload_config()
        # The focused-idle grace only matters when the focus check is on
        self.idle_sync_focused_timeout_spinbox.setEnabled(bool(enabled))

    def change_avoid_review(self, enabled):
        self.config.set(CONFIG_AVOID_INTERRUPTION_REVIEW, bool(enabled))
        self.sync_routine.reload_config()
        self.avoid_review_timeout_spinbox.setEnabled(bool(enabled))

    def change_avoid_review_timeout(self, value):
        self._set_minutes_suffix(self.avoid_review_timeout_spinbox, value)
        self.config.set(CONFIG_AVOID_REVIEW_TIMEOUT, value)
        self.sync_routine.reload_config()

    def change_avoid_override_timeout(self, value):
        self._set_minutes_suffix(self.avoid_override_timeout_spinbox, value)
        self.config.set(CONFIG_AVOID_OVERRIDE_TIMEOUT, value)
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

    def change_idle_sync_focused_timeout(self, value):
        self._set_minutes_suffix(self.idle_sync_focused_timeout_spinbox, value)
        self.config.set(CONFIG_IDLE_SYNC_FOCUSED_TIMEOUT, value)
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
        if support_tab.should_open_after_update():
            tab_widget.setCurrentIndex(2)

        # --- Bottom buttons (shared across tabs) ---
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(0, 5, 0, 0)

        reset_button = QPushButton("Reset Defaults")
        reset_button.setMaximumWidth(120)
        reset_button.clicked.connect(self.on_reset_to_defaults_call)

        save_button = QPushButton("Save")
        save_button.setMaximumWidth(120)
        save_button.clicked.connect(self._save_and_close)

        cancel_button = QPushButton("Cancel")
        cancel_button.setMaximumWidth(120)
        cancel_button.clicked.connect(lambda *args: self.reject())

        btn_layout.addWidget(reset_button)
        btn_layout.addStretch()
        btn_layout.addWidget(cancel_button)
        btn_layout.addWidget(save_button)
        main_layout.addLayout(btn_layout)

    def _save_and_close(self):
        """Apply any pending settings, persist config, and close the dialog."""
        self.sync_routine.reload_config()
        self.accept()

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

    def _refresh_avoid_dialog_sub_checkboxes(self):
        avoid_list = set(self.config.get(CONFIG_AVOID_DIALOG_LIST))
        for _, checkbox in getattr(self, "avoid_dialog_sub_checkboxes", []):
            checkbox.setChecked(checkbox.property("dialogName") in avoid_list)

    def on_reset_to_defaults_call(self):
        from .constants import CONFIG_DEFAULT_CONFIG
        for key, value in CONFIG_DEFAULT_CONFIG.items():
            self.config.set(key, value)

        self.sync_timeout_spinbox.blockSignals(True)
        self.idle_sync_timeout_spinbox.blockSignals(True)
        self.avoid_dialogs_checkbox.blockSignals(True)
        self.avoid_dialogs_timeout_spinbox.blockSignals(True)
        for _, checkbox in getattr(self, "avoid_dialog_sub_checkboxes", []):
            checkbox.blockSignals(True)
        self.avoid_focus_checkbox.blockSignals(True)
        self.avoid_review_checkbox.blockSignals(True)
        self.avoid_review_timeout_spinbox.blockSignals(True)
        self.avoid_override_timeout_spinbox.blockSignals(True)
        self.sync_on_change_only_checkbox.blockSignals(True)
        self.idle_before_sync_spinbox.blockSignals(True)
        self.idle_sync_focused_timeout_spinbox.blockSignals(True)
        self.disable_internet_check_checkbox.blockSignals(True)
        self.conflict_resolution_combo.blockSignals(True)

        self.sync_timeout_spinbox.setValue(self.config.get(CONFIG_SYNC_TIMEOUT))
        self.idle_sync_timeout_spinbox.setValue(self.config.get(CONFIG_IDLE_SYNC_TIMEOUT))
        self.avoid_dialogs_checkbox.setChecked(self.config.get(CONFIG_AVOID_INTERRUPTION_DIALOGS))
        self._refresh_avoid_dialog_sub_checkboxes()
        self.avoid_dialogs_timeout_spinbox.setValue(self.config.get(CONFIG_AVOID_DIALOGS_TIMEOUT))
        self._set_minutes_suffix(self.avoid_dialogs_timeout_spinbox, self.config.get(CONFIG_AVOID_DIALOGS_TIMEOUT))
        self.avoid_focus_checkbox.setChecked(self.config.get(CONFIG_AVOID_INTERRUPTION_FOCUS))
        self.avoid_review_checkbox.setChecked(self.config.get(CONFIG_AVOID_INTERRUPTION_REVIEW))
        self.avoid_review_timeout_spinbox.setValue(self.config.get(CONFIG_AVOID_REVIEW_TIMEOUT))
        self._set_minutes_suffix(self.avoid_review_timeout_spinbox, self.config.get(CONFIG_AVOID_REVIEW_TIMEOUT))
        self.avoid_override_timeout_spinbox.setValue(self.config.get(CONFIG_AVOID_OVERRIDE_TIMEOUT))
        self._set_minutes_suffix(self.avoid_override_timeout_spinbox, self.config.get(CONFIG_AVOID_OVERRIDE_TIMEOUT))
        self.sync_on_change_only_checkbox.setChecked(self.config.get(CONFIG_SYNC_ON_CHANGE_ONLY))
        self.idle_before_sync_spinbox.setValue(self.config.get(CONFIG_IDLE_BEFORE_SYNC))
        self.idle_sync_focused_timeout_spinbox.setValue(self.config.get(CONFIG_IDLE_SYNC_FOCUSED_TIMEOUT))
        self.disable_internet_check_checkbox.setChecked(self.config.get(CONFIG_DISABLE_INTERNET_CHECK))
        reset_idx = self.conflict_resolution_combo.findData(self.config.get(CONFIG_CONFLICT_RESOLUTION))
        if reset_idx >= 0:
            self.conflict_resolution_combo.setCurrentIndex(reset_idx)

        self.idle_before_sync_spinbox.setEnabled(self.config.get(CONFIG_SYNC_ON_CHANGE_ONLY))
        self.sync_timeout_spinbox.setEnabled(not self.config.get(CONFIG_SYNC_ON_CHANGE_ONLY))
        self.idle_sync_timeout_spinbox.setEnabled(not self.config.get(CONFIG_SYNC_ON_CHANGE_ONLY))
        self.idle_sync_focused_timeout_spinbox.setEnabled(self.config.get(CONFIG_AVOID_INTERRUPTION_FOCUS))
        self.avoid_dialogs_timeout_spinbox.setEnabled(self.config.get(CONFIG_AVOID_INTERRUPTION_DIALOGS))
        self.avoid_review_timeout_spinbox.setEnabled(self.config.get(CONFIG_AVOID_INTERRUPTION_REVIEW))

        self.sync_timeout_spinbox.blockSignals(False)
        self.idle_sync_timeout_spinbox.blockSignals(False)
        self.avoid_dialogs_checkbox.blockSignals(False)
        self.avoid_dialogs_timeout_spinbox.blockSignals(False)
        for _, checkbox in getattr(self, "avoid_dialog_sub_checkboxes", []):
            checkbox.blockSignals(False)
        self.avoid_focus_checkbox.blockSignals(False)
        self.avoid_review_checkbox.blockSignals(False)
        self.avoid_review_timeout_spinbox.blockSignals(False)
        self.avoid_override_timeout_spinbox.blockSignals(False)
        self.sync_on_change_only_checkbox.blockSignals(False)
        self.idle_before_sync_spinbox.blockSignals(False)
        self.idle_sync_focused_timeout_spinbox.blockSignals(False)
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
