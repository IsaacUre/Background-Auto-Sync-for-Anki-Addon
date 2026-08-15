"""Settings tab for the Auto Sync options dialog."""
from aqt.qt import (
    QCheckBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
    Qt,
)

from ..constants import (
    CONFIG_AVOID_INTERRUPTION_DIALOGS,
    CONFIG_AVOID_DIALOG_LIST,
    CONFIG_AVOID_DIALOGS_TIMEOUT,
    CONFIG_AVOID_INTERRUPTION_FOCUS,
    CONFIG_AVOID_INTERRUPTION_REVIEW,
    CONFIG_AVOID_REVIEW_TIMEOUT,
    CONFIG_AVOID_OVERRIDE_TIMEOUT,
    CONFIG_CONFLICT_RESOLUTION,
    CONFIG_DISABLE_INTERNET_CHECK,
    CONFIG_IDLE_BEFORE_SYNC,
    CONFIG_IDLE_SYNC_FOCUSED_TIMEOUT,
    CONFIG_IDLE_SYNC_TIMEOUT,
    CONFIG_SYNC_ON_CHANGE_ONLY,
    CONFIG_SYNC_TIMEOUT,
    CONFLICT_DOWNLOAD,
    CONFLICT_PROMPT,
    CONFLICT_UPLOAD,
    DIALOG_WINDOW_OPTIONS,
)
from ..utils import wrap_in_scroll


def _make_override_row(dialog, spinbox, config_key, change_fn):
    """Build an indented row: 'Allow sync anyway after [N min]' for an interruption."""
    row = QWidget()
    row_layout = QHBoxLayout(row)
    row_layout.setContentsMargins(20, 0, 0, 0)
    row_layout.setSpacing(6)

    label = QLabel("Allow sync anyway after")
    label.setToolTip("After this many minutes of inactivity, sync proceeds even if this condition is true (0 = never).")

    spinbox.setMinimum(0)
    spinbox.setMaximum(120)
    spinbox.setSpecialValueText("Off")
    spinbox.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTrailing | Qt.AlignmentFlag.AlignVCenter)
    spinbox.setValue(dialog.config.get(config_key))
    dialog._set_minutes_suffix(spinbox, spinbox.value())
    spinbox.setToolTip(label.toolTip())
    spinbox.valueChanged.connect(change_fn)
    spinbox.setMinimumWidth(90)

    row_layout.addWidget(label)
    row_layout.addWidget(spinbox)
    row_layout.addStretch()
    return row


def build(dialog) -> QWidget:
    """Build the settings controls and return the tab widget."""

    # "Sync after" option
    sync_timeout_label = QLabel("Sync after")
    sync_timeout_label.setToolTip("How many minutes after you have last interacted with Anki the program will wait to start the sync")
    dialog.sync_timeout_spinbox.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTrailing | Qt.AlignmentFlag.AlignVCenter)
    dialog.sync_timeout_spinbox.setMinimum(1)
    dialog.sync_timeout_spinbox.setValue(dialog.config.get(CONFIG_SYNC_TIMEOUT))
    dialog._set_minutes_suffix(dialog.sync_timeout_spinbox, dialog.sync_timeout_spinbox.value())
    dialog.sync_timeout_spinbox.setToolTip("How many minutes after you have last interacted with Anki the program will wait to start the sync")
    dialog.sync_timeout_spinbox.valueChanged.connect(dialog.change_sync_timeout)
    dialog.sync_timeout_spinbox.setEnabled(not dialog.config.get(CONFIG_SYNC_ON_CHANGE_ONLY))

    # "Idle Sync after" option
    idle_sync_timeout_label = QLabel("When the program is idle, sync every")
    idle_sync_timeout_label.setToolTip("While you are not using Anki, the program will keep syncing in the background (in case you are using Anki on mobile or web and there are changes to sync)")
    dialog.idle_sync_timeout_spinbox.setMinimum(0)
    dialog.idle_sync_timeout_spinbox.setSpecialValueText("Off")
    dialog.idle_sync_timeout_spinbox.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTrailing | Qt.AlignmentFlag.AlignVCenter)
    dialog.idle_sync_timeout_spinbox.setValue(dialog.config.get(CONFIG_IDLE_SYNC_TIMEOUT))
    dialog._set_minutes_suffix(dialog.idle_sync_timeout_spinbox, dialog.idle_sync_timeout_spinbox.value())
    dialog.idle_sync_timeout_spinbox.setToolTip("While you are not using Anki, the program will keep syncing in the background (in case you are using Anki on mobile or web and there are changes to sync)")
    dialog.idle_sync_timeout_spinbox.valueChanged.connect(dialog.change_idle_sync_timeout)
    dialog.idle_sync_timeout_spinbox.setEnabled(not dialog.config.get(CONFIG_SYNC_ON_CHANGE_ONLY))

    # "Avoid interruptions" — individually toggleable conditions

    # Global override timeout (applies to every interruption; lower of specific/global wins)
    avoid_override_label = QLabel("Global: allow sync anyway after")
    avoid_override_label.setToolTip(
        "A global safety valve applied to all three interruption conditions below.<br>"
        "For each one, the effective grace is the lower of its own timeout and this global "
        "value (0 = disabled). After that much inactivity, sync proceeds regardless."
    )
    dialog.avoid_override_timeout_spinbox.setMinimum(0)
    dialog.avoid_override_timeout_spinbox.setMaximum(120)
    dialog.avoid_override_timeout_spinbox.setSpecialValueText("Off")
    dialog.avoid_override_timeout_spinbox.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTrailing | Qt.AlignmentFlag.AlignVCenter)
    dialog.avoid_override_timeout_spinbox.setValue(dialog.config.get(CONFIG_AVOID_OVERRIDE_TIMEOUT))
    dialog._set_minutes_suffix(dialog.avoid_override_timeout_spinbox, dialog.avoid_override_timeout_spinbox.value())
    dialog.avoid_override_timeout_spinbox.setToolTip(avoid_override_label.toolTip())
    dialog.avoid_override_timeout_spinbox.valueChanged.connect(dialog.change_avoid_override_timeout)

    # Avoid syncing while dialogs are open, with per-window-type sub-settings
    avoid_dialogs_label = QLabel("Avoid sync when dialogs are open")
    avoid_dialogs_tooltip = "Don't auto-sync while the card browser, add-note or similar windows are open."
    avoid_dialogs_label.setToolTip(avoid_dialogs_tooltip)
    dialog.avoid_dialogs_checkbox.setToolTip(avoid_dialogs_tooltip)
    dialog.avoid_dialogs_checkbox.setChecked(dialog.config.get(CONFIG_AVOID_INTERRUPTION_DIALOGS))
    dialog.avoid_dialogs_checkbox.toggled.connect(dialog.change_avoid_dialogs)
    avoid_dialogs_label.mouseReleaseEvent = lambda *args: dialog.avoid_dialogs_checkbox.toggle()

    avoid_dialogs_cell = QWidget()
    avoid_dialogs_cell_layout = QVBoxLayout(avoid_dialogs_cell)
    avoid_dialogs_cell_layout.setContentsMargins(0, 0, 0, 0)
    avoid_dialogs_cell_layout.setSpacing(2)
    avoid_dialogs_cell_layout.addWidget(dialog.avoid_dialogs_checkbox)

    dialog.avoid_dialog_sub_checkboxes = []
    avoid_list = set(dialog.config.get(CONFIG_AVOID_DIALOG_LIST))
    for label, name in DIALOG_WINDOW_OPTIONS:
        sub = QCheckBox(label)
        sub.setProperty("dialogName", name)
        sub.setChecked(name in avoid_list)
        sub.toggled.connect(lambda checked, n=name: dialog.change_avoid_dialog_type(n, checked))
        sub.setEnabled(dialog.config.get(CONFIG_AVOID_INTERRUPTION_DIALOGS))
        avoid_dialogs_cell_layout.addWidget(sub)
        dialog.avoid_dialog_sub_checkboxes.append((name, sub))

    dialog.avoid_dialogs_timeout_spinbox.setEnabled(dialog.config.get(CONFIG_AVOID_INTERRUPTION_DIALOGS))
    avoid_dialogs_cell_layout.addWidget(_make_override_row(
        dialog, dialog.avoid_dialogs_timeout_spinbox, CONFIG_AVOID_DIALOGS_TIMEOUT,
        dialog.change_avoid_dialogs_timeout))
    avoid_dialogs_cell_layout.addStretch()

    # Avoid syncing while the main window is focused (with its own override timeout)
    avoid_focus_label = QLabel("Avoid sync when the main window is focused")
    avoid_focus_tooltip = "Don't auto-sync while the main Anki window has focus."
    avoid_focus_label.setToolTip(avoid_focus_tooltip)
    dialog.avoid_focus_checkbox.setToolTip(avoid_focus_tooltip)
    dialog.avoid_focus_checkbox.setChecked(dialog.config.get(CONFIG_AVOID_INTERRUPTION_FOCUS))
    dialog.avoid_focus_checkbox.toggled.connect(dialog.change_avoid_focus)
    avoid_focus_label.mouseReleaseEvent = lambda *args: dialog.avoid_focus_checkbox.toggle()

    avoid_focus_cell = QWidget()
    avoid_focus_cell_layout = QVBoxLayout(avoid_focus_cell)
    avoid_focus_cell_layout.setContentsMargins(0, 0, 0, 0)
    avoid_focus_cell_layout.setSpacing(2)
    avoid_focus_cell_layout.addWidget(dialog.avoid_focus_checkbox)
    dialog.idle_sync_focused_timeout_spinbox.setEnabled(dialog.config.get(CONFIG_AVOID_INTERRUPTION_FOCUS))
    avoid_focus_cell_layout.addWidget(_make_override_row(
        dialog, dialog.idle_sync_focused_timeout_spinbox, CONFIG_IDLE_SYNC_FOCUSED_TIMEOUT,
        dialog.change_idle_sync_focused_timeout))
    avoid_focus_cell_layout.addStretch()

    # Avoid syncing while reviewing (with its own override timeout)
    avoid_review_label = QLabel("Avoid sync while reviewing")
    avoid_review_tooltip = "Don't auto-sync unless Anki is on the deck browser or overview screen."
    avoid_review_label.setToolTip(avoid_review_tooltip)
    dialog.avoid_review_checkbox.setToolTip(avoid_review_tooltip)
    dialog.avoid_review_checkbox.setChecked(dialog.config.get(CONFIG_AVOID_INTERRUPTION_REVIEW))
    dialog.avoid_review_checkbox.toggled.connect(dialog.change_avoid_review)
    avoid_review_label.mouseReleaseEvent = lambda *args: dialog.avoid_review_checkbox.toggle()

    avoid_review_cell = QWidget()
    avoid_review_cell_layout = QVBoxLayout(avoid_review_cell)
    avoid_review_cell_layout.setContentsMargins(0, 0, 0, 0)
    avoid_review_cell_layout.setSpacing(2)
    avoid_review_cell_layout.addWidget(dialog.avoid_review_checkbox)
    dialog.avoid_review_timeout_spinbox.setEnabled(dialog.config.get(CONFIG_AVOID_INTERRUPTION_REVIEW))
    avoid_review_cell_layout.addWidget(_make_override_row(
        dialog, dialog.avoid_review_timeout_spinbox, CONFIG_AVOID_REVIEW_TIMEOUT,
        dialog.change_avoid_review_timeout))
    avoid_review_cell_layout.addStretch()

    # "Only sync when changes detected" checkbox
    sync_on_change_only_label = QLabel("Only sync when changes are detected")
    sync_on_change_only_tooltip = (
        "When enabled, the addon will only sync when the collection has been modified "
        "(e.g. cards added, reviewed, edited).<br>"
        "Idle periodic syncs will be skipped if no changes are detected, "
        "reducing unnecessary network traffic."
    )
    sync_on_change_only_label.setToolTip(sync_on_change_only_tooltip)
    dialog.sync_on_change_only_checkbox = QCheckBox()
    dialog.sync_on_change_only_checkbox.setToolTip(sync_on_change_only_tooltip)
    dialog.sync_on_change_only_checkbox.setChecked(dialog.config.get(CONFIG_SYNC_ON_CHANGE_ONLY))
    dialog.sync_on_change_only_checkbox.toggled.connect(dialog.change_sync_on_change_only)
    sync_on_change_only_label.mouseReleaseEvent = lambda *args: dialog.sync_on_change_only_checkbox.toggle()

    # "Idle before sync after change" spinbox
    idle_before_sync_label = QLabel("After a change, wait idle before syncing")
    idle_before_sync_tooltip = (
        "When a change is detected, wait this many minutes of user inactivity "
        "before triggering a sync.<br>"
        "This prevents syncing in the middle of an editing session."
    )
    idle_before_sync_label.setToolTip(idle_before_sync_tooltip)
    dialog.idle_before_sync_spinbox.setMinimum(1)
    dialog.idle_before_sync_spinbox.setMaximum(60)
    dialog.idle_before_sync_spinbox.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTrailing | Qt.AlignmentFlag.AlignVCenter)
    dialog.idle_before_sync_spinbox.setValue(dialog.config.get(CONFIG_IDLE_BEFORE_SYNC))
    dialog._set_minutes_suffix(dialog.idle_before_sync_spinbox, dialog.idle_before_sync_spinbox.value())
    dialog.idle_before_sync_spinbox.setToolTip(idle_before_sync_tooltip)
    dialog.idle_before_sync_spinbox.valueChanged.connect(dialog.change_idle_before_sync)
    dialog.idle_before_sync_spinbox.setEnabled(dialog.config.get(CONFIG_SYNC_ON_CHANGE_ONLY))

    # "Disable internet check" checkbox
    disable_internet_check_label = QLabel("Disable pre-sync internet check")
    disable_internet_check_tooltip = (
        "When enabled, the addon will skip the connectivity check "
        "and immediately attempt to sync."
    )
    disable_internet_check_label.setToolTip(disable_internet_check_tooltip)
    dialog.disable_internet_check_checkbox.setToolTip(disable_internet_check_tooltip)
    dialog.disable_internet_check_checkbox.setChecked(dialog.config.get(CONFIG_DISABLE_INTERNET_CHECK))
    dialog.disable_internet_check_checkbox.toggled.connect(dialog.change_disable_internet_check)
    disable_internet_check_label.mouseReleaseEvent = lambda *args: dialog.disable_internet_check_checkbox.toggle()

    # "On conflict" combo box
    conflict_resolution_label = QLabel("On sync conflict")
    conflict_resolution_tooltip = (
        "When a full-sync conflict is detected, Anki normally asks which "
        "direction to sync.<br>"
        "Here you can force a direction automatically. WARNING: the losing "
        "side's local changes are discarded."
    )
    conflict_resolution_label.setToolTip(conflict_resolution_tooltip)
    dialog.conflict_resolution_combo.setToolTip(conflict_resolution_tooltip)
    dialog.conflict_resolution_combo.addItem("Ask me each time", CONFLICT_PROMPT)
    dialog.conflict_resolution_combo.addItem("Always AnkiWeb -> local", CONFLICT_DOWNLOAD)
    dialog.conflict_resolution_combo.addItem("Always local -> AnkiWeb", CONFLICT_UPLOAD)
    current = dialog.config.get(CONFIG_CONFLICT_RESOLUTION)
    idx = dialog.conflict_resolution_combo.findData(current)
    if idx >= 0:
        dialog.conflict_resolution_combo.setCurrentIndex(idx)
    dialog.conflict_resolution_combo.currentIndexChanged.connect(dialog.change_conflict_resolution)

    # Grid layout for settings
    grid = QGridLayout()
    grid.setSpacing(10)
    grid.addWidget(sync_timeout_label, 0, 0)
    grid.addWidget(dialog.sync_timeout_spinbox, 0, 1)

    grid.addWidget(idle_sync_timeout_label, 1, 0)
    grid.addWidget(dialog.idle_sync_timeout_spinbox, 1, 1)

    grid.addWidget(avoid_override_label, 2, 0)
    grid.addWidget(dialog.avoid_override_timeout_spinbox, 2, 1)

    grid.addWidget(avoid_dialogs_label, 3, 0)
    grid.addWidget(avoid_dialogs_cell, 3, 1)

    grid.addWidget(avoid_focus_label, 4, 0)
    grid.addWidget(avoid_focus_cell, 4, 1)

    grid.addWidget(avoid_review_label, 5, 0)
    grid.addWidget(avoid_review_cell, 5, 1)

    grid.addWidget(sync_on_change_only_label, 6, 0)
    grid.addWidget(dialog.sync_on_change_only_checkbox, 6, 1)

    grid.addWidget(idle_before_sync_label, 7, 0)
    grid.addWidget(dialog.idle_before_sync_spinbox, 7, 1)

    grid.addWidget(disable_internet_check_label, 8, 0)
    grid.addWidget(dialog.disable_internet_check_checkbox, 8, 1)

    grid.addWidget(conflict_resolution_label, 9, 0)
    grid.addWidget(dialog.conflict_resolution_combo, 9, 1)

    # Wrap grid in a vbox
    outer_layout = QVBoxLayout()
    outer_layout.addLayout(grid)

    content = QWidget()
    content.setLayout(outer_layout)
    return wrap_in_scroll(content)
