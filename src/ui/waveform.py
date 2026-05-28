from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget


class WaveformWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.values = [0.05] * 56
        self.setMinimumHeight(96)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(80)

    def set_level(self, level):
        self.values.append(max(0.06, min(1.0, level)))
        self.values = self.values[-56:]

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor("#15181f"))
        painter.drawRoundedRect(self.rect().adjusted(0, 0, -1, -1), 12, 12)
        width = self.width()
        height = self.height()
        gap = 3
        padding = 16
        usable_width = max(1, width - padding * 2)
        visible_count = max(10, min(len(self.values), int(usable_width / 6)))
        values = self.values[-visible_count:]
        bar_width = max(2, min(4, int((usable_width - gap * max(0, len(values) - 1)) / len(values))))
        x = padding
        pen = QPen(QColor("#14b8a6"))
        pen.setWidth(bar_width)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        for value in values:
            bar_height = max(14, int(value * (height - 18)))
            y1 = int((height - bar_height) / 2)
            y2 = y1 + bar_height
            painter.drawLine(x, y1, x, y2)
            x += bar_width + gap
