import sys
from pathlib import Path

from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import QApplication

from src.ui.main_window import MainWindow


def run():
    app = QApplication(sys.argv)
    app.setApplicationName("Meet Transcript")
    app.setFont(QFont("Segoe UI", 10))
    app.setWindowIcon(QIcon(str(Path(__file__).resolve().parents[1] / "assets" / "app-icon.svg")))
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
