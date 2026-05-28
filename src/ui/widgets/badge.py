from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QHBoxLayout, QLabel, QSizePolicy, QWidget

from src.resources import asset_path


class Badge(QWidget):
    def __init__(self, icon_name, text):
        super().__init__()
        self.setObjectName("badge")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 5, 9, 5)
        layout.setSpacing(6)
        self.icon = QLabel()
        self.icon.setPixmap(QIcon(str(asset_path(icon_name))).pixmap(14, 14))
        self.icon.setObjectName("badgeIcon")
        self.label = QLabel(text)
        self.label.setObjectName("badgeText")
        self.label.setWordWrap(False)
        self.label.setMinimumWidth(0)
        self.label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
        layout.addWidget(self.icon, 0, Qt.AlignVCenter)
        layout.addWidget(self.label, 1, Qt.AlignVCenter)

    def setText(self, text):
        self.label.setText(text)

    def text(self):
        return self.label.text()
