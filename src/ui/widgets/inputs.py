from PySide6.QtWidgets import QComboBox, QDoubleSpinBox


class NoWheelComboBox(QComboBox):
    def wheelEvent(self, event):
        event.ignore()


class NoWheelDoubleSpinBox(QDoubleSpinBox):
    def wheelEvent(self, event):
        event.ignore()
