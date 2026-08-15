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
        """Register AutoSyncLogDialog instance to listen to log output"""
        self.log_dialog = log_dialog

    def unregister(self, log_dialog):
        """Stop sending updates to the provided dialog instance."""
        if self.log_dialog is log_dialog:
            self.log_dialog = None
