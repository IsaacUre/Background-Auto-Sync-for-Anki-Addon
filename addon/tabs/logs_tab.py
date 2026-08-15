"""Logs tab for the Auto Sync options dialog."""
from aqt.qt import QTextEdit, QVBoxLayout, QWidget


def build(dialog) -> QWidget:
    """Build the log viewer and return the tab widget."""
    parent = QWidget()
    dialog.log_output = QTextEdit()
    dialog.log_output.setReadOnly(True)
    dialog.log_output.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)

    layout = QVBoxLayout()
    layout.addWidget(dialog.log_output, 1)  # stretch factor 1 to fill space
    parent.setLayout(layout)

    # Register for live log updates and show existing log
    dialog.log_manager.register(dialog)
    dialog.refresh_log()
    return parent
