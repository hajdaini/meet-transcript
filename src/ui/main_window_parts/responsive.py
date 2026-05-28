from PySide6.QtWidgets import QBoxLayout


class MainWindowResponsiveMixin:
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_responsive_layout()

    def update_responsive_layout(self):
        self.apply_single_layout()

    def apply_single_layout(self):
        self.is_compact = True
        self.sidebar.setFixedWidth(64)

        self.record_layout.setDirection(QBoxLayout.TopToBottom)
        self.record_layout.setContentsMargins(14, 12, 14, 14)
        self.record_layout.setSpacing(12)
        self.record_layout.setStretchFactor(self.record_main_panel, 0)
        self.record_layout.setStretchFactor(self.history_panel, 1)

        self.clear_badge_layout()
        self.arrange_badges(2)

        self.center_layout.setDirection(QBoxLayout.LeftToRight)
        self.center_layout.setContentsMargins(10, 8, 10, 8)
        self.center_layout.setSpacing(8)

        self.record_center.setMinimumHeight(86)
        self.record_center.setMaximumHeight(110)

        self.start_button.setFixedSize(108, 38)
        self.import_button.setFixedSize(88, 38)
        self.timer_label.setMinimumWidth(68)
        self.timer_label.setMaximumWidth(82)

        self.waveform.setMinimumHeight(58)
        self.waveform.setMaximumHeight(72)
        self.waveform.setMinimumWidth(0)
        self.waveform.setMaximumWidth(16777215)

        self.history_panel.setMinimumWidth(0)
        self.history_panel.setMinimumHeight(320)
        self.recent_list.setMinimumHeight(150)
