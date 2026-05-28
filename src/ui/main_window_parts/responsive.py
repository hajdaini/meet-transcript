from PySide6.QtWidgets import QBoxLayout


class MainWindowResponsiveMixin:
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_responsive_layout()

    def update_responsive_layout(self):
        stacked = self.width() < 860
        medium = self.width() < 1270
        compact = stacked or medium
        if compact == self.is_compact and getattr(self, "is_stacked", None) == stacked:
            return
        self.is_compact = compact
        self.is_stacked = stacked
        if stacked:
            self.sidebar.setFixedWidth(64)
            self.record_layout.setDirection(QBoxLayout.TopToBottom)
            self.record_layout.setContentsMargins(14, 12, 14, 14)
            self.record_layout.setSpacing(10)
            self.record_layout.setStretchFactor(self.record_main_panel, 0)
            self.record_layout.setStretchFactor(self.history_panel, 0)
            self.clear_badge_layout()
            self.arrange_badges(2)
            self.center_layout.setDirection(QBoxLayout.LeftToRight)
            self.center_layout.setContentsMargins(12, 10, 12, 10)
            self.center_layout.setSpacing(10)
            self.record_center.setMinimumHeight(122)
            self.start_button.setFixedSize(132, 46)
            self.import_button.setFixedSize(112, 46)
            self.timer_label.setMinimumWidth(86)
            self.waveform.setMinimumHeight(82)
            self.waveform.setMaximumHeight(96)
            self.waveform.setMinimumWidth(120)
            self.waveform.setMaximumWidth(16777215)
            self.history_panel.setMinimumHeight(250)
            self.recent_list.setMinimumHeight(90)
        elif medium:
            self.sidebar.setFixedWidth(64)
            self.record_layout.setDirection(QBoxLayout.LeftToRight)
            self.record_layout.setContentsMargins(18, 20, 20, 20)
            self.record_layout.setSpacing(14)
            self.record_layout.setStretchFactor(self.record_main_panel, 3)
            self.record_layout.setStretchFactor(self.history_panel, 3)
            self.clear_badge_layout()
            self.arrange_badges(1)
            self.center_layout.setDirection(QBoxLayout.LeftToRight)
            self.center_layout.setContentsMargins(12, 10, 12, 10)
            self.center_layout.setSpacing(10)
            self.record_center.setMinimumHeight(112)
            self.start_button.setFixedSize(126, 44)
            self.import_button.setFixedSize(106, 44)
            self.timer_label.setMinimumWidth(82)
            self.waveform.setMinimumHeight(76)
            self.waveform.setMaximumHeight(90)
            self.waveform.setMinimumWidth(100)
            self.waveform.setMaximumWidth(16777215)
            self.history_panel.setMinimumHeight(0)
            self.recent_list.setMinimumHeight(100)
        else:
            self.sidebar.setFixedWidth(64)
            self.record_layout.setDirection(QBoxLayout.LeftToRight)
            self.record_layout.setContentsMargins(22, 24, 24, 24)
            self.record_layout.setSpacing(18)
            self.record_layout.setStretchFactor(self.record_main_panel, 5)
            self.record_layout.setStretchFactor(self.history_panel, 3)
            self.clear_badge_layout()
            self.arrange_badges(3)
            self.center_layout.setDirection(QBoxLayout.LeftToRight)
            self.center_layout.setContentsMargins(14, 12, 14, 12)
            self.center_layout.setSpacing(14)
            self.record_center.setMinimumHeight(132)
            self.start_button.setFixedSize(142, 50)
            self.import_button.setFixedSize(118, 50)
            self.timer_label.setMinimumWidth(110)
            self.waveform.setMinimumHeight(86)
            self.waveform.setMaximumHeight(100)
            self.waveform.setMinimumWidth(140)
            self.waveform.setMaximumWidth(16777215)
            self.history_panel.setMinimumHeight(0)
            self.recent_list.setMinimumHeight(110)

