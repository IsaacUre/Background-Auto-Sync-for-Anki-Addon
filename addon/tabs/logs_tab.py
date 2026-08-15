"""Logs tab for the Auto Sync options dialog, plus the shared LogManager."""
import os
from aqt.qt import QTextEdit, QVBoxLayout, QWidget

# Log file written alongside the in-memory log. It is cleared on every Anki
# restart so it always captures the current session for bug-fix review.
LOG_FILENAME = "auto_sync.log"


def _addon_root():
    """Absolute path to the add-on root (contains __init__.py / main.py)."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _log_path():
    return os.path.join(_addon_root(), LOG_FILENAME)


class LogManager:
    def __init__(self):
        self.log = ""
        self.log_dialog = None
        # Clear the file each session so it reflects only this run of Anki.
        self._clear_file()

    def _clear_file(self):
        try:
            with open(_log_path(), "w", encoding="utf-8"):
                pass
        except OSError:
            pass

    def _append_to_file(self, line: str):
        try:
            with open(_log_path(), "a", encoding="utf-8") as f:
                f.write(line + "\n")
        except OSError:
            pass

    def write(self, line: str):
        """Add a single line to the log (and append it to the log file)."""
        self.log += line + "\n"
        self._append_to_file(line)
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
