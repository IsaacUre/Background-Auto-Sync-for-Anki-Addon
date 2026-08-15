"""Logs tab for the Auto Sync options dialog, plus the shared LogManager."""
from aqt.qt import QTextEdit, QVBoxLayout, QWidget


class LogManager:
    def __init__(self):
        self.log = ""
        self.log_dialog = None

    def write(self, line: str):
        """Add a single line to the log"""
        self.log += line + "\n"
        # call the log dialog window to refresh it
        if self.log_dialog:
            try:
                self.log_dialog.refresh_log()
            except RuntimeError:
                self.log_dialog = None

    def read(self):
        """Get all log entries seperated by \\n"""
        return self.log

    def register(self, log_dialog):
        """Register a dialog instance to listen to log output"""
        self.log_dialog = log_dialog

    def unregister(self, log_dialog):
        """Stop sending updates to the provided dialog instance."""
        if self.log_dialog is log_dialog:
            self.log_dialog = None


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
