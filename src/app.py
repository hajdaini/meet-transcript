import sys

from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import QApplication

from src.resources import asset_path
from src.ui.main_window import MainWindow


def run():
    app = QApplication(sys.argv)
    app.setApplicationName("Meet Transcript")
    app.setFont(QFont("Segoe UI", 10))
    app.setWindowIcon(QIcon(str(asset_path("app-icon.svg"))))
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
