"""Settings tab for the Auto Sync options dialog."""
from aqt.qt import (
    QCheckBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
    Qt,
)

from ..constants import (
    CONFIG_AVOID_DIALOG_LIST,
    CONFIG_AVOID_DIALOGS_TIMEOUT,
    CONFIG_AVOID_INTERRUPTION_DIALOGS,
    CONFIG_AVOID_INTERRUPTION_FOCUS,
    CONFIG_AVOID_INTERRUPTION_REVIEW,
    CONFIG_AVOID_OVERRIDE_TIMEOUT,
    CONFIG_AVOID_REVIEW_TIMEOUT,
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
    row = QWidget()
    layout = QHBoxLayout(row)
    layout.setContentsMargins(20, 0, 0, 0)
    layout.setSpacing(6)

    label = QLabel("Allow sync anyway after")
    label.setToolTip(
        "After this many minutes of inactivity, sync proceeds even if this condition is true (0 = never)."
    )
    spinbox.setMinimum(0)
    spinbox.setMaximum(120)
    spinbox.setSpecialValueText("Off")
    spinbox.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTrailing | Qt.AlignmentFlag.AlignVCenter)
    spinbox.setValue(dialog.config.get(config_key))
    dialog._set_minutes_suffix(spinbox, spinbox.value())
    spinbox.setToolTip(label.toolTip())
    spinbox.valueChanged.connect(change_fn)
    spinbox.setMinimumWidth(90)
    layout.addWidget(label)
    layout.addWidget(spinbox)
    layout.addStretch()
    return row


def _add_section(layout, title, form):
    group = QGroupBox(title)
    group.setLayout(form)
    layout.addWidget(group)
    return group


def _build_sync_section(dialog):
    form = QFormLayout()
    form.setHorizontalSpacing(12)
    form.setVerticalSpacing(7)

    dialog.sync_on_change_only_checkbox.setText("")
    change_only_tooltip = (
        "Only sync when the collection has changed. This avoids unnecessary syncs when nothing changed."
    )
    dialog.sync_on_change_only_checkbox.setToolTip(change_only_tooltip)
    dialog.sync_on_change_only_checkbox.setChecked(dialog.config.get(CONFIG_SYNC_ON_CHANGE_ONLY))
    dialog.sync_on_change_only_checkbox.toggled.connect(dialog.change_sync_on_change_only)
    form.addRow(QLabel("Only sync when changes are detected"), dialog.sync_on_change_only_checkbox)

    sync_label = QLabel("Sync after")
    sync_label.setToolTip("Minutes of inactivity before syncing a changed collection.")
    dialog.sync_timeout_spinbox.setMinimum(1)
    dialog.sync_timeout_spinbox.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTrailing | Qt.AlignmentFlag.AlignVCenter)
    dialog.sync_timeout_spinbox.setValue(dialog.config.get(CONFIG_SYNC_TIMEOUT))
    dialog._set_minutes_suffix(dialog.sync_timeout_spinbox, dialog.sync_timeout_spinbox.value())
    dialog.sync_timeout_spinbox.setToolTip(sync_label.toolTip())
    dialog.sync_timeout_spinbox.valueChanged.connect(dialog.change_sync_timeout)
    dialog.sync_timeout_spinbox.setEnabled(not dialog.config.get(CONFIG_SYNC_ON_CHANGE_ONLY))
    form.addRow(sync_label, dialog.sync_timeout_spinbox)

    idle_before_label = QLabel("After a change, wait idle before syncing")
    idle_before_label.setToolTip("Wait this long after a change before syncing, so active editing is not interrupted.")
    dialog.idle_before_sync_spinbox.setMinimum(1)
    dialog.idle_before_sync_spinbox.setMaximum(60)
    dialog.idle_before_sync_spinbox.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTrailing | Qt.AlignmentFlag.AlignVCenter)
    dialog.idle_before_sync_spinbox.setValue(dialog.config.get(CONFIG_IDLE_BEFORE_SYNC))
    dialog._set_minutes_suffix(dialog.idle_before_sync_spinbox, dialog.idle_before_sync_spinbox.value())
    dialog.idle_before_sync_spinbox.setToolTip(idle_before_label.toolTip())
    dialog.idle_before_sync_spinbox.valueChanged.connect(dialog.change_idle_before_sync)
    dialog.idle_before_sync_spinbox.setEnabled(dialog.config.get(CONFIG_SYNC_ON_CHANGE_ONLY))
    form.addRow(idle_before_label, dialog.idle_before_sync_spinbox)
    return form


def _build_dialogs_cell(dialog):
    cell = QWidget()
    layout = QVBoxLayout(cell)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(2)
    layout.addWidget(dialog.avoid_dialogs_checkbox)

    dialog.avoid_dialog_sub_checkboxes = []
    avoid_list = set(dialog.config.get(CONFIG_AVOID_DIALOG_LIST))
    enabled = dialog.config.get(CONFIG_AVOID_INTERRUPTION_DIALOGS)
    for option_label, name in DIALOG_WINDOW_OPTIONS:
        checkbox = QCheckBox(option_label)
        checkbox.setProperty("dialogName", name)
        checkbox.setChecked(name in avoid_list)
        checkbox.setEnabled(enabled)
        checkbox.toggled.connect(lambda checked, n=name: dialog.change_avoid_dialog_type(n, checked))
        layout.addWidget(checkbox)
        dialog.avoid_dialog_sub_checkboxes.append((name, checkbox))

    dialog.avoid_dialogs_timeout_spinbox.setEnabled(enabled)
    layout.addWidget(_make_override_row(
        dialog,
        dialog.avoid_dialogs_timeout_spinbox,
        CONFIG_AVOID_DIALOGS_TIMEOUT,
        dialog.change_avoid_dialogs_timeout,
    ))
    return cell


def _build_interruption_section(dialog):
    form = QFormLayout()
    form.setHorizontalSpacing(12)
    form.setVerticalSpacing(7)

    global_label = QLabel("Global override")
    global_label.setToolTip(
        "Global cap for interruption grace periods. The effective value is the lower positive value of the specific and global settings."
    )
    dialog.avoid_override_timeout_spinbox.setMinimum(0)
    dialog.avoid_override_timeout_spinbox.setMaximum(120)
    dialog.avoid_override_timeout_spinbox.setSpecialValueText("Off")
    dialog.avoid_override_timeout_spinbox.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTrailing | Qt.AlignmentFlag.AlignVCenter)
    dialog.avoid_override_timeout_spinbox.setValue(dialog.config.get(CONFIG_AVOID_OVERRIDE_TIMEOUT))
    dialog._set_minutes_suffix(dialog.avoid_override_timeout_spinbox, dialog.avoid_override_timeout_spinbox.value())
    dialog.avoid_override_timeout_spinbox.setToolTip(global_label.toolTip())
    dialog.avoid_override_timeout_spinbox.valueChanged.connect(dialog.change_avoid_override_timeout)
    form.addRow(global_label, dialog.avoid_override_timeout_spinbox)

    dialog.avoid_dialogs_checkbox.setText("")
    dialogs_label = QLabel("Avoid sync when dialogs are open")
    dialogs_label.setToolTip("Defer sync while the selected Anki windows are open.")
    dialog.avoid_dialogs_checkbox.setToolTip(dialogs_label.toolTip())
    dialog.avoid_dialogs_checkbox.setChecked(dialog.config.get(CONFIG_AVOID_INTERRUPTION_DIALOGS))
    dialog.avoid_dialogs_checkbox.toggled.connect(dialog.change_avoid_dialogs)
    form.addRow(dialogs_label, _build_dialogs_cell(dialog))

    dialog.avoid_focus_checkbox.setText("")
    focus_label = QLabel("Avoid sync when the main window is focused")
    focus_label.setToolTip("Defer sync while the main Anki window has focus.")
    dialog.avoid_focus_checkbox.setToolTip(focus_label.toolTip())
    dialog.avoid_focus_checkbox.setChecked(dialog.config.get(CONFIG_AVOID_INTERRUPTION_FOCUS))
    dialog.avoid_focus_checkbox.toggled.connect(dialog.change_avoid_focus)
    focus_cell = QWidget()
    focus_layout = QVBoxLayout(focus_cell)
    focus_layout.setContentsMargins(0, 0, 0, 0)
    focus_layout.setSpacing(2)
    focus_layout.addWidget(dialog.avoid_focus_checkbox)
    dialog.idle_sync_focused_timeout_spinbox.setEnabled(dialog.config.get(CONFIG_AVOID_INTERRUPTION_FOCUS))
    focus_layout.addWidget(_make_override_row(
        dialog,
        dialog.idle_sync_focused_timeout_spinbox,
        CONFIG_IDLE_SYNC_FOCUSED_TIMEOUT,
        dialog.change_idle_sync_focused_timeout,
    ))
    form.addRow(focus_label, focus_cell)

    dialog.avoid_review_checkbox.setText("")
    review_label = QLabel("Avoid sync while reviewing")
    review_label.setToolTip("Defer sync unless Anki is on the deck browser or overview screen.")
    dialog.avoid_review_checkbox.setToolTip(review_label.toolTip())
    dialog.avoid_review_checkbox.setChecked(dialog.config.get(CONFIG_AVOID_INTERRUPTION_REVIEW))
    dialog.avoid_review_checkbox.toggled.connect(dialog.change_avoid_review)
    review_cell = QWidget()
    review_layout = QVBoxLayout(review_cell)
    review_layout.setContentsMargins(0, 0, 0, 0)
    review_layout.setSpacing(2)
    review_layout.addWidget(dialog.avoid_review_checkbox)
    dialog.avoid_review_timeout_spinbox.setEnabled(dialog.config.get(CONFIG_AVOID_INTERRUPTION_REVIEW))
    review_layout.addWidget(_make_override_row(
        dialog,
        dialog.avoid_review_timeout_spinbox,
        CONFIG_AVOID_REVIEW_TIMEOUT,
        dialog.change_avoid_review_timeout,
    ))
    form.addRow(review_label, review_cell)
    return form


def _build_background_section(dialog):
    form = QFormLayout()
    form.setHorizontalSpacing(12)
    form.setVerticalSpacing(7)

    idle_label = QLabel("When idle, sync every")
    idle_label.setToolTip("Periodically sync while Anki is idle to pick up changes from another device.")
    dialog.idle_sync_timeout_spinbox.setMinimum(0)
    dialog.idle_sync_timeout_spinbox.setSpecialValueText("Off")
    dialog.idle_sync_timeout_spinbox.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTrailing | Qt.AlignmentFlag.AlignVCenter)
    dialog.idle_sync_timeout_spinbox.setValue(dialog.config.get(CONFIG_IDLE_SYNC_TIMEOUT))
    dialog._set_minutes_suffix(dialog.idle_sync_timeout_spinbox, dialog.idle_sync_timeout_spinbox.value())
    dialog.idle_sync_timeout_spinbox.setToolTip(idle_label.toolTip())
    dialog.idle_sync_timeout_spinbox.valueChanged.connect(dialog.change_idle_sync_timeout)
    dialog.idle_sync_timeout_spinbox.setEnabled(not dialog.config.get(CONFIG_SYNC_ON_CHANGE_ONLY))
    form.addRow(idle_label, dialog.idle_sync_timeout_spinbox)

    dialog.disable_internet_check_checkbox.setText("")
    internet_label = QLabel("Disable pre-sync reachability check")
    internet_label.setToolTip(
        "Skip the check that the sync server is reachable and attempt to sync immediately."
    )
    dialog.disable_internet_check_checkbox.setToolTip(internet_label.toolTip())
    dialog.disable_internet_check_checkbox.setChecked(dialog.config.get(CONFIG_DISABLE_INTERNET_CHECK))
    dialog.disable_internet_check_checkbox.toggled.connect(dialog.change_disable_internet_check)
    form.addRow(internet_label, dialog.disable_internet_check_checkbox)

    conflict_label = QLabel("On sync conflict")
    conflict_label.setToolTip("Choose how ambiguous full-sync conflicts are resolved.")
    dialog.conflict_resolution_combo.setToolTip(conflict_label.toolTip())
    dialog.conflict_resolution_combo.addItem("Ask me each time", CONFLICT_PROMPT)
    dialog.conflict_resolution_combo.addItem("Always AnkiWeb -> local", CONFLICT_DOWNLOAD)
    dialog.conflict_resolution_combo.addItem("Always local -> AnkiWeb", CONFLICT_UPLOAD)
    current = dialog.config.get(CONFIG_CONFLICT_RESOLUTION)
    index = dialog.conflict_resolution_combo.findData(current)
    if index >= 0:
        dialog.conflict_resolution_combo.setCurrentIndex(index)
    dialog.conflict_resolution_combo.currentIndexChanged.connect(dialog.change_conflict_resolution)
    form.addRow(conflict_label, dialog.conflict_resolution_combo)
    return form


def build(dialog) -> QWidget:
    """Build one compact, grouped Settings tab."""
    layout = QVBoxLayout()
    layout.setSpacing(10)
    _add_section(layout, "Sync behavior", _build_sync_section(dialog))
    _add_section(layout, "Interruption avoidance", _build_interruption_section(dialog))
    _add_section(layout, "Background and network", _build_background_section(dialog))
    layout.addStretch()

    content = QWidget()
    content.setLayout(layout)
    return wrap_in_scroll(content)
