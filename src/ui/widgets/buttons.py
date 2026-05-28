from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QToolButton

from src.resources import asset_path


class HoverIconToolButton(QToolButton):
    def __init__(self, icon_name, tooltip, parent=None):
        super().__init__(parent)
        self.default_icon_name = icon_name
        self.setIcon(QIcon(str(asset_path(icon_name))))
        self.setIconSize(QSize(15, 15))
        self.setToolTip(tooltip)
        self.setObjectName("iconButton")
        self.setFixedSize(28, 28)

    def enterEvent(self, event):
        self.set_named_icon(self.property("hoverIcon") or self.default_icon_name)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.set_named_icon(self.property("normalIcon") or self.default_icon_name)
        super().leaveEvent(event)

    def set_named_icon(self, icon_name):
        self.setIcon(QIcon(str(asset_path(icon_name))))
