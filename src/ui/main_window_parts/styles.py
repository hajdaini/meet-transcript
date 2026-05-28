


class MainWindowStyleMixin:
    def apply_style(self):
        self.setStyleSheet(
            """
            QMainWindow { background: #101216; color: #f3f6f8; }
            QWidget { background: #101216; color: #f3f6f8; font-family: Segoe UI; font-size: 10pt; }
            #sidebar { background: #171a20; min-width: 64px; max-width: 64px; border-right: 1px solid #202630; }
            QLabel { background: transparent; }
            #navButton { border: 0; border-radius: 8px; background: transparent; padding: 6px; }
            #navButton:hover { background: transparent; }
            #navButton[active="true"] { background: transparent; border-left: 3px solid #14b8a6; }
            #pageTitle { font-size: 17pt; font-weight: 700; }
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
            #sessionSearchInput {
                background: #202630;
                border: 1px solid #303946;
                border-radius: 8px;
                padding: 6px 11px;
                color: #edf2f6;
                min-height: 20px;
                max-height: 26px;
                selection-background-color: #143f35;
            }
            #sessionSearchInput:focus {
                border: 1px solid #14b8a6;
            }
            #sessionSearchInput::placeholder {
                color: #96a3af;
            }
            #formLabel { color: #b8c0cc; min-width: 140px; }
            #formRow { background: transparent; min-height: 38px; }
            #badge { background: #202630; color: #dce5ec; border-radius: 7px; font-size: 9pt; }
            #badgeIcon { background: transparent; }
            #badgeText { background: transparent; color: #dce5ec; font-size: 9pt; }
            #badge[state="ok"] { background: #143f35; color: #62f0c8; }
            #badge[state="blocked"] { background: #4a1d1d; color: #ffb4a8; }
            #badge[state="neutral"] { background: #202630; color: #dce5ec; }
            #panel, #recordCenter, #settingsSection { background: #171a20; border-radius: 8px; }
            #recordControls { background: transparent; max-height: 42px; min-width: 284px; }
            #transcriptBox { background: #171a20; border: 1px solid #303946; border-radius: 8px; }
            #audioPlayerPanel { background: #171a20; border-top: 1px solid #303946; border-bottom: 1px solid #303946; min-height: 44px; max-height: 46px; }
            #audioPlayButton { background: #202630; border: 1px solid #303946; border-radius: 8px; color: #62f0c8; font-size: 11pt; font-weight: 800; padding: 0; }
            #audioPlayButton:hover { background: #24343b; border: 1px solid #14b8a6; }
            #audioPlayButton:disabled { color: #7f8b98; background: #202630; border: 1px solid #2a313b; }
            #audioTimeLabel { color: #96a3af; font-size: 9pt; background: transparent; }
            #audioPositionSlider { background: transparent; min-height: 22px; }
            #audioPositionSlider::groove:horizontal { height: 5px; background: #2a313b; border-radius: 2px; }
            #audioPositionSlider::handle:horizontal { width: 12px; height: 12px; margin: -4px 0; background: #14b8a6; border-radius: 6px; }
            #audioPositionSlider::sub-page:horizontal { background: #14b8a6; border-radius: 2px; }
            #startButton { min-width: 108px; min-height: 38px; border-radius: 10px; background: #14b8a6; color: #061412; font-size: 9pt; font-weight: 800; border: 0; padding: 0 10px; }
            #startButton:hover { background: #14b8a6; }
            #startButton[recording="true"] { background: #ef4444; color: #ffffff; }
            #startButton[recording="true"]:hover { background: #ef4444; }
            #startButton:disabled { background: #41505a; color: #aab4bc; }
            #importButton { min-width: 88px; min-height: 38px; border-radius: 10px; background: #232a33; color: #f3f6f8; font-size: 10pt; font-weight: 700; border: 1px solid #303946; padding: 0 12px; }
            #importButton:hover { background: #303946; border: 1px solid #14b8a6; color: #62f0c8; }
            #importButton:disabled { background: #202630; border: 1px solid #2a313b; color: #7f8b98; }
            #timerLabel { font-size: 18pt; font-weight: 700; color: #ffffff; }
            QListWidget, QTextEdit, QComboBox, QLineEdit, QSpinBox, QDoubleSpinBox { background: #101216; border: 1px solid #2a313b; border-radius: 8px; padding: 8px; color: #edf2f6; selection-background-color: #143f35; }
            #transcriptPreview { background: #171a20; border: 0; border-radius: 0; }
            #transcriptPreview viewport { background: #171a20; }
            QListWidget::item { padding: 0; border-radius: 7px; background: transparent; margin: 0; min-height: 42px; }
            QListWidget::item:selected { background: transparent; }
            QPushButton { background: #232a33; border: 0; border-radius: 8px; padding: 10px 14px; color: #f3f6f8; }
            QPushButton:hover { background: #303946; }
            #historyTabs { background: #171a20; border: 0; }
            #historyTabs::pane { border: 0; top: -1px; background: #171a20; }
            QTabBar { background: #171a20; }
            #historyTabPage { background: #171a20; }
            #historyTabs::tab-bar { alignment: left; }
            QTabBar::tab { background: #171a20; color: #b8c0cc; border: 1px solid #303946; border-radius: 7px; padding: 6px 12px; margin-right: 6px; }
            QTabBar::tab:selected { background: #202630; color: #62f0c8; border: 1px solid #14b8a6; }
            QTabBar::tab:hover { background: #202630; }
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
            #stepperControl { background: transparent; min-height: 38px; max-height: 38px; }
            #stepperControl QSpinBox, #stepperControl QDoubleSpinBox { background: #101216; border: 1px solid #2a313b; border-radius: 8px; padding: 6px 12px; color: #edf2f6; min-height: 20px; max-height: 20px; }
            #stepperControl QSpinBox:focus, #stepperControl QDoubleSpinBox:focus { border: 1px solid #14b8a6; }
            #stepperButton { background: #101216; border: 1px solid #2a313b; border-radius: 8px; min-width: 32px; max-width: 32px; min-height: 32px; max-height: 32px; color: #62f0c8; font-size: 12pt; font-weight: 700; padding: 0; margin: 0; }
            #stepperButton:hover { background: #101216; border: 1px solid #14b8a6; }
            #stepperButton:pressed { background: #101216; color: #62f0c8; border: 1px solid #62f0c8; }
            #settingsSubsection { background: #101216; border: 1px solid #2a313b; border-radius: 8px; }
            #settingsSubsectionTitle { color: #62f0c8; font-size: 10pt; font-weight: 700; background: transparent; }
            QComboBox, QLineEdit, QSpinBox, QDoubleSpinBox { min-height: 22px; }
            QScrollArea, #pageScroll, #recordPageScroll { border: 0; background: #101216; }
            #recordPageScroll QScrollBar:horizontal { height: 0; width: 0; background: transparent; }
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

