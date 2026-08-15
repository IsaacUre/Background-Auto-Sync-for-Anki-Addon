"""Support tab for the Auto Sync options dialog."""
import os

from aqt import mw
from aqt.qt import (
    QApplication,
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTimer,
    QVBoxLayout,
    QWidget,
    QPixmap,
    Qt,
)
from aqt.webview import AnkiWebView

from ..constants import ADDON_PACKAGE
from ..utils import wrap_in_scroll


def _current_version():
    version_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "VERSION")
    try:
        with open(version_path, encoding="utf-8") as version_file:
            return version_file.read().strip()
    except OSError:
        return ""


def should_open_after_update():
    """Mark the current release as shown and report whether Support should open."""
    meta = mw.addonManager.addonMeta(ADDON_PACKAGE)
    version = _current_version()
    if meta.get("supporter_opt_out", False) or not version:
        return False
    if meta.get("last_seen_version") == version:
        return False

    meta["last_seen_version"] = version
    mw.addonManager.writeAddonMeta(ADDON_PACKAGE, meta)
    return True


def _load_supporter_state(dialog):
    meta = mw.addonManager.addonMeta(ADDON_PACKAGE)
    dialog.supporter_check.blockSignals(True)
    dialog.supporter_check.setChecked(meta.get("supporter_opt_out", False))
    dialog.supporter_check.blockSignals(False)


def _on_supporter_check_toggled(dialog, checked):
    meta = mw.addonManager.addonMeta(ADDON_PACKAGE)
    meta["supporter_opt_out"] = checked
    mw.addonManager.writeAddonMeta(ADDON_PACKAGE, meta)


def _add_qr(qr_list, name, address, filename, base_path):
    container = QWidget()
    vbox = QVBoxLayout(container)
    vbox.setAlignment(Qt.AlignmentFlag.AlignCenter)

    title = QLabel(f"<b>{name}</b>")
    title.setAlignment(Qt.AlignmentFlag.AlignCenter)
    vbox.addWidget(title)

    qr_label = QLabel()
    qr_path = os.path.join(base_path, "Support", filename)
    pixmap = QPixmap(qr_path)
    if not pixmap.isNull():
        qr_label.setPixmap(pixmap.scaled(400, 400, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
    else:
        qr_label.setText("Image not found")
    qr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    vbox.addWidget(qr_label)

    addr_row_container = QWidget()
    addr_row_container.setFixedWidth(420)
    addr_row = QHBoxLayout(addr_row_container)
    addr_row.setContentsMargins(10, 0, 10, 0)
    addr_row.setSpacing(10)

    addr_label = QLineEdit(address)
    addr_label.setReadOnly(True)
    addr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    addr_label.setStyleSheet("background: rgba(0,0,0,5%); border: 1px solid rgba(0,0,0,10%); border-radius: 3px; padding: 2px;")
    addr_label.setMinimumWidth(0)

    copy_btn = QPushButton("Copy")
    copy_btn.setFixedWidth(80)
    copy_btn.setCursor(Qt.CursorShape.PointingHandCursor)

    def on_copy(_=None, addr=address, btn=copy_btn):
        clipboard = QApplication.clipboard()
        if clipboard:
            clipboard.setText(addr)
            btn.setText("Copied!")
            QTimer.singleShot(2000, lambda: btn.setText("Copy"))

    copy_btn.clicked.connect(on_copy)

    addr_row.addWidget(addr_label, 1)
    addr_row.addWidget(copy_btn)
    vbox.addWidget(addr_row_container, 0, Qt.AlignmentFlag.AlignCenter)

    qr_list.addWidget(container)


def build(dialog) -> QWidget:
    """Build the support / donate content and return the tab widget."""
    content = QWidget()
    layout = QVBoxLayout(content)
    layout.setContentsMargins(10, 10, 10, 10)

    instr = QLabel(
        "If you find this addon useful, consider supporting the development through the following methods:"
    )
    instr.setWordWrap(True)
    instr.setOpenExternalLinks(True)
    instr.setTextFormat(Qt.TextFormat.RichText)
    instr.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(instr)

    # Supporter opt-out (hides the automatic update welcome)
    dialog.supporter_check = QCheckBox("I have supported this addon (Hide automatic update welcome)")
    dialog.supporter_check.setToolTip("Checking this will prevent the Support tab from opening automatically after future updates.")
    dialog.supporter_check.toggled.connect(lambda checked: _on_supporter_check_toggled(dialog, checked))
    layout.addWidget(dialog.supporter_check, 0, Qt.AlignmentFlag.AlignCenter)
    layout.addSpacing(10)

    # Ko-fi widget (embedded via AnkiWebView)
    dialog.kofi_widget = AnkiWebView(content)
    dialog.kofi_widget.setFixedHeight(42)
    kofi_html = """
    <html>
    <head>
    <style>
      body { background-color: transparent; margin: 0; padding: 0; overflow: hidden; text-align: center; line-height: 42px; }
      .kofi-button-col { display: inline-block; vertical-align: middle; }
    </style>
    </head>
    <body>
    <script type='text/javascript' src='https://storage.ko-fi.com/cdn/widget/Widget_2.js'></script>
    <script type='text/javascript'>
      kofiwidget2.init('Support me on Ko-fi', '#72a4f2', 'D1D01W6NQT');
      kofiwidget2.draw();
    </script>
    </body>
    </html>
    """
    dialog.kofi_widget.setHtml(kofi_html)
    layout.addWidget(dialog.kofi_widget)

    base_path = os.path.dirname(os.path.dirname(__file__))

    qr_list = QVBoxLayout()
    qr_list.setAlignment(Qt.AlignmentFlag.AlignHCenter)
    qr_list.setSpacing(30)

    _add_qr(qr_list, "UPI", "athulkrishnasv2015-2@okhdfcbank", "UPI.jpg", base_path)
    _add_qr(qr_list, "BTC", "bc1qrrek3m7sr33qujjrktj949wav6mehdsk057cfx", "BTC.jpg", base_path)
    _add_qr(qr_list, "ETH", "0xce6899e4903EcB08bE5Be65E44549fadC3F45D27", "ETH.jpg", base_path)
    layout.addLayout(qr_list)

    _load_supporter_state(dialog)
    return wrap_in_scroll(content)
