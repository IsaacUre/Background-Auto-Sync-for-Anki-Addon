"""Support tab for the Auto Sync options dialog."""
import os

from aqt.qt import (
    QHBoxLayout,
    QLabel,
    QPixmap,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
    Qt,
)
from aqt.webview import AnkiWebView


def build(dialog) -> QWidget:
    """Build the support / donate content and return the tab widget."""
    parent = QWidget()
    main_layout = QVBoxLayout()
    parent.setLayout(main_layout)

    # Introduction
    intro_label = QLabel("If you find this add-on useful, consider supporting its development!")
    intro_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    intro_label.setWordWrap(True)
    main_layout.addWidget(intro_label)

    # Ko-fi Widget
    kofi_html = """
    <body style="margin: 0; padding: 8px 0;">
    <div style="display: flex; justify-content: center; align-items: center; height: 100%;">
        <script type='text/javascript' src='https://storage.ko-fi.com/cdn/widget/Widget_2.js'></script>
        <script type='text/javascript'>
            kofiwidget2.init('Support me on Ko-fi', '#72a4f2', 'D1D01W6NQT');
            kofiwidget2.draw();
        </script>
    </div>
    </body>
    """
    dialog.kofi_widget = AnkiWebView(title="kofi_support")
    dialog.kofi_widget.stdHtml(kofi_html)
    dialog.kofi_widget.setFixedHeight(60)
    main_layout.addWidget(dialog.kofi_widget)

    # Scroll area for donation details
    scroll_area = QScrollArea()
    scroll_area.setWidgetResizable(True)
    scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    main_layout.addWidget(scroll_area)

    scroll_widget = QWidget()
    scroll_layout = QVBoxLayout()
    scroll_widget.setLayout(scroll_layout)
    scroll_area.setWidget(scroll_widget)

    # Support details
    support_items = [
        {"title": "UPI", "id": "athulkrishnasv2015-2@okhdfcbank", "img": "UPI.jpg"},
        {"title": "Bitcoin (BTC)", "id": "bc1qrrek3m7sr33qujjrktj949wav6mehdsk057cfx", "img": "BTC.jpg"},
        {"title": "Ethereum (ETH)", "id": "0xce6899e4903EcB08bE5Be65E44549fadC3F45D27", "img": "ETH.jpg"},
    ]

    addon_path = os.path.dirname(__file__)
    support_dir = os.path.join(addon_path, "..", "Support")

    for item in support_items:
        item_widget = QWidget()
        item_layout = QVBoxLayout()
        item_widget.setLayout(item_layout)

        # Title
        title_label = QLabel(f"<b>{item['title']}</b>")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        item_layout.addWidget(title_label)

        # QR Code
        qr_label = QLabel()
        qr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        img_path = os.path.join(support_dir, item["img"])
        if os.path.exists(img_path):
            pixmap = QPixmap(img_path)
            pixmap = pixmap.scaled(250, 250, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            qr_label.setPixmap(pixmap)
        else:
            qr_label.setText("(Image not found)")
        item_layout.addWidget(qr_label)

        # ID and Copy Button
        id_layout = QHBoxLayout()
        id_label = QLabel(item["id"])
        id_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        copy_button = QPushButton("Copy")
        copy_button.setMaximumWidth(80)
        copy_button.clicked.connect(lambda checked, text=item["id"]: dialog._copy_to_clipboard(text))

        id_layout.addWidget(id_label)
        id_layout.addWidget(copy_button)
        item_layout.addLayout(id_layout)

        item_layout.setContentsMargins(0, 10, 0, 20)
        scroll_layout.addWidget(item_widget)

    return parent
