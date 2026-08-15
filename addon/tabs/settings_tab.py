"""Settings tab for the Auto Sync options dialog."""
from aqt.qt import (
    QCheckBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
    Qt,
)

from ..constants import (
    CONFIG_CONFLICT_RESOLUTION,
    CONFIG_DISABLE_INTERNET_CHECK,
    CONFIG_IDLE_BEFORE_SYNC,
    CONFIG_IDLE_SYNC_TIMEOUT,
    CONFIG_STRICTLY_AVOID_INTERRUPTIONS,
    CONFIG_SYNC_ON_CHANGE_ONLY,
    CONFIG_SYNC_TIMEOUT,
    CONFLICT_DOWNLOAD,
    CONFLICT_PROMPT,
    CONFLICT_UPLOAD,
)


def build(dialog) -> QWidget:
    """Build the settings controls and return the tab widget."""
    parent = QWidget()

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

    # "Strictly avoid interruptions" checkbox
    strictly_avoid_interruptions_label = QLabel("Strictly avoid interruptions (recommended)")
    strictly_avoid_interruptions_label.setToolTip("Will not auto sync if cards are being reviewed, the card browser or similar windows are open <br>or the main window has focus (isn't minimized or in the background)")
    dialog.strictly_avoid_interruptions_checkbox.setToolTip("Will not auto sync if cards are being reviewed, the card browser or similar windows are open <br>or the main window has focus (isn't minimized or in the background)")
    dialog.strictly_avoid_interruptions_checkbox.setChecked(dialog.config.get(CONFIG_STRICTLY_AVOID_INTERRUPTIONS))
    dialog.strictly_avoid_interruptions_checkbox.toggled.connect(dialog.change_strictly_avoid_interruption)
    strictly_avoid_interruptions_label.mouseReleaseEvent = lambda *args: dialog.strictly_avoid_interruptions_checkbox.toggle()

    # Explanation of when syncing runs/deferring while this is enabled
    strictly_avoid_note = QLabel(
        "<span style='color: #cc0000;'>When enabled, auto-sync only runs while Anki is in the "
        "background &mdash; unfocused, no dialogs open, and not reviewing.<br>"
        "Changes made during a session are still uploaded when you close Anki.</span>"
    )
    strictly_avoid_note.setWordWrap(True)
    strictly_avoid_note.setTextFormat(Qt.TextFormat.RichText)
    strictly_avoid_note.setContentsMargins(0, 0, 0, 0)
    strictly_avoid_note.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

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

    # Reset Defaults button
    reset_button = QPushButton("Reset Defaults")
    reset_button.clicked.connect(dialog.on_reset_to_defaults_call)
    reset_button.setMaximumWidth(120)

    # Grid layout for settings
    grid = QGridLayout()
    grid.setSpacing(10)
    grid.addWidget(sync_timeout_label, 0, 0)
    grid.addWidget(dialog.sync_timeout_spinbox, 0, 1)

    grid.addWidget(idle_sync_timeout_label, 1, 0)
    grid.addWidget(dialog.idle_sync_timeout_spinbox, 1, 1)

    grid.addWidget(strictly_avoid_interruptions_label, 2, 0)
    grid.addWidget(dialog.strictly_avoid_interruptions_checkbox, 2, 1)
    grid.addWidget(strictly_avoid_note, 3, 0, 1, 2)

    grid.addWidget(sync_on_change_only_label, 4, 0)
    grid.addWidget(dialog.sync_on_change_only_checkbox, 4, 1)

    grid.addWidget(idle_before_sync_label, 5, 0)
    grid.addWidget(dialog.idle_before_sync_spinbox, 5, 1)

    grid.addWidget(disable_internet_check_label, 6, 0)
    grid.addWidget(dialog.disable_internet_check_checkbox, 6, 1)

    grid.addWidget(conflict_resolution_label, 7, 0)
    grid.addWidget(dialog.conflict_resolution_combo, 7, 1)

    reset_layout = QHBoxLayout()
    reset_layout.setContentsMargins(0, 0, 0, 0)
    reset_layout.addStretch()
    reset_layout.addWidget(reset_button)
    grid.addLayout(reset_layout, 8, 1)

    # Wrap grid in a vbox
    outer_layout = QVBoxLayout()
    outer_layout.addLayout(grid)
    parent.setLayout(outer_layout)
    return parent
