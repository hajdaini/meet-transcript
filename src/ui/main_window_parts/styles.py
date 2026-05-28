


class MainWindowStyleMixin:
    def apply_style(self):
        self.setStyleSheet(
            """
            QMainWindow { background: #101216; color: #f3f6f8; }
            QWidget { background: #101216; color: #f3f6f8; font-family: Segoe UI; font-size: 10pt; }
            #sidebar { background: #171a20; min-width: 64px; max-width: 64px; border-right: 1px solid #202630; }
            QLabel { background: transparent; }
            #brandIcon { background: transparent; }
            #navButton { border: 0; border-radius: 8px; background: transparent; padding: 6px; }
            #navButton:hover { background: transparent; }
            #navButton[active="true"] { background: transparent; border-left: 3px solid #14b8a6; }
            #pageTitle { font-size: 18pt; font-weight: 700; }
            #sectionTitle { font-size: 12pt; font-weight: 650; background: transparent; }
            #sectionHeader { background: transparent; }
            #sectionIcon { background: transparent; }
            #statusLabel { color: #f0b35a; font-size: 10pt; }
            #statusLabel[state="done"] { color: #62f0c8; }
            #statusLabel[state="error"] { color: #ffb4a8; }
            #statusLabel[state="working"] { color: #dce5ec; }
            #transcriptionProgress { background: #101216; border: 1px solid #2a313b; border-radius: 7px; color: #dce5ec; min-height: 14px; max-height: 16px; text-align: center; }
            #transcriptionProgress::chunk { background: #14b8a6; border-radius: 7px; }
            #bodyText { color: #b8c0cc; }
            #emptyText { color: #7f8b98; padding: 22px; border: 1px dashed #2a313b; border-radius: 8px; }
            #sessionSearchInput { min-height: 20px; padding: 7px 10px; }
            #formLabel { color: #b8c0cc; min-width: 140px; }
            #formRow { background: transparent; }
            #badge { background: #202630; color: #dce5ec; border-radius: 7px; font-size: 9pt; }
            #badgeIcon { background: transparent; }
            #badgeText { background: transparent; color: #dce5ec; font-size: 9pt; }
            #badge[state="ok"] { background: #143f35; color: #62f0c8; }
            #badge[state="blocked"] { background: #4a1d1d; color: #ffb4a8; }
            #badge[state="neutral"] { background: #202630; color: #dce5ec; }
            #panel, #recordCenter, #settingsSection { background: #171a20; border-radius: 8px; }
            #recordControls { background: transparent; }
            #transcriptBox { background: #101216; border: 1px solid #2a313b; border-radius: 8px; }
            #startButton { min-width: 132px; min-height: 46px; border-radius: 10px; background: #14b8a6; color: #061412; font-size: 10pt; font-weight: 800; border: 0; padding: 0 12px; }
            #startButton:hover { background: #14b8a6; }
            #startButton[recording="true"] { background: #ef4444; color: #ffffff; }
            #startButton[recording="true"]:hover { background: #ef4444; }
            #startButton:disabled { background: #41505a; color: #aab4bc; }
            #importButton { min-width: 106px; min-height: 44px; border-radius: 10px; background: #232a33; color: #f3f6f8; font-size: 10pt; font-weight: 700; border: 1px solid #303946; padding: 0 12px; }
            #importButton:hover { background: #303946; border: 1px solid #14b8a6; color: #62f0c8; }
            #importButton:disabled { background: #202630; border: 1px solid #2a313b; color: #7f8b98; }
            #timerLabel { font-size: 21pt; font-weight: 700; color: #ffffff; }
            QListWidget, QTextEdit, QComboBox, QLineEdit, QDoubleSpinBox { background: #101216; border: 1px solid #2a313b; border-radius: 8px; padding: 8px; color: #edf2f6; selection-background-color: #143f35; }
            #transcriptPreview { border: 0; border-top: 1px solid #2a313b; border-radius: 0; }
            QListWidget::item { padding: 0; border-radius: 7px; background: transparent; margin: 0; min-height: 42px; }
            QListWidget::item:selected { background: transparent; }
            QPushButton { background: #232a33; border: 0; border-radius: 8px; padding: 10px 14px; color: #f3f6f8; }
            QPushButton:hover { background: #303946; }
            #historyTabs { background: transparent; border: 0; }
            #historyTabs::pane { border: 0; top: -1px; }
            #historyTabs::tab-bar { alignment: left; }
            QTabBar::tab { background: #101216; color: #b8c0cc; border: 1px solid #2a313b; border-radius: 7px; padding: 6px 12px; margin-right: 6px; }
            QTabBar::tab:selected { background: #143f35; color: #62f0c8; border: 1px solid #14b8a6; }
            QTabBar::tab:hover { background: #101216; }
            QListWidget::item:hover { background: transparent; }
            #sessionRow { background: #202630; border: 1px solid #303946; border-radius: 7px; }
            #sessionRow:hover { background: #24343b; border: 1px solid #14b8a6; }
            #sessionRow[selected="true"] { background: #24343b; border: 1px solid #14b8a6; }
            #sessionContent, #sessionMeta { background: transparent; }
            #sessionButton { text-align: left; background: transparent; padding: 0 5px; color: #f3f6f8; font-weight: 650; min-height: 20px; font-size: 9pt; }
            #sessionButton:hover { background: transparent; color: #62f0c8; }
            #sessionMetaText { color: #96a3af; font-size: 8pt; background: transparent; }
            #iconButton { background: transparent; border: 0; border-radius: 0; padding: 3px; min-width: 24px; min-height: 24px; }
            #iconButton:hover { background: transparent; border: 0; }
            #iconButton:pressed { background: transparent; border: 0; }
            #iconButton[role="action"]:hover { background: transparent; border: 0; }
            #iconButton[role="delete"]:hover { background: transparent; border: 0; }
            #iconButton:disabled { opacity: 0.35; }
            #gainControl { background: transparent; }
            #gainButton { background: #101216; border: 1px solid #2a313b; border-radius: 8px; min-width: 34px; min-height: 34px; color: #62f0c8; font-size: 13pt; font-weight: 700; padding: 0; }
            #gainButton:hover { background: #101216; border: 1px solid #14b8a6; }
            #gainButton:pressed { background: #101216; color: #62f0c8; border: 1px solid #62f0c8; }
            QComboBox, QLineEdit, QDoubleSpinBox { min-height: 22px; }
            QScrollArea, #pageScroll { border: 0; background: #101216; }
            QScrollBar:vertical { background: transparent; width: 8px; margin: 2px; }
            QScrollBar::handle:vertical { background: #303946; border-radius: 4px; min-height: 28px; }
            QScrollBar::handle:vertical:hover { background: #3b4654; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; background: transparent; border: 0; }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: transparent; }
            QScrollBar:horizontal { background: transparent; height: 8px; margin: 2px; }
            QScrollBar::handle:horizontal { background: #303946; border-radius: 4px; min-width: 28px; }
            QScrollBar::handle:horizontal:hover { background: #3b4654; }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; background: transparent; border: 0; }
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal { background: transparent; }
            """
        )

