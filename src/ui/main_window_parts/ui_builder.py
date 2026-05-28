from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QAbstractSpinBox,
    QBoxLayout,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QStackedWidget,
    QTabWidget,
    QTextEdit,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from src.resources import asset_path
from src.ui.waveform import WaveformWidget
from src.ui.widgets import Badge, HoverIconToolButton, NoWheelComboBox, NoWheelDoubleSpinBox


class MainWindowUiBuilderMixin:
    def build_ui(self):
        root = QWidget()
        shell = QHBoxLayout(root)
        shell.setContentsMargins(0, 0, 0, 0)
        shell.setSpacing(0)
        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        side = QVBoxLayout(self.sidebar)
        side.setContentsMargins(10, 14, 10, 14)
        side.setSpacing(10)
        brand = QLabel()
        brand.setPixmap(QIcon(str(asset_path("app-icon.svg"))).pixmap(22, 22))
        brand.setAlignment(Qt.AlignCenter)
        brand.setObjectName("brandIcon")
        self.record_nav = self.nav_button("mic.svg", self.tr("recording"), 0)
        self.settings_nav = self.nav_button("settings.svg", self.tr("settings"), 1)
        side.addWidget(brand)
        side.addSpacing(16)
        side.addWidget(self.record_nav, alignment=Qt.AlignCenter)
        side.addWidget(self.settings_nav, alignment=Qt.AlignCenter)
        side.addStretch()
        self.stack = QStackedWidget()
        self.stack.addWidget(self.record_page())
        self.stack.addWidget(self.settings_page())
        shell.addWidget(self.sidebar, 0)
        shell.addWidget(self.stack, 1)
        self.setCentralWidget(root)
        self.switch_page(0)

    def nav_button(self, icon_name, tooltip, index):
        button = QToolButton()
        button.setIcon(QIcon(str(asset_path(icon_name))))
        button.setIconSize(QSize(18, 18))
        button.setToolTip(tooltip)
        button.setObjectName("navButton")
        button.setFixedSize(36, 36)
        button.clicked.connect(lambda: self.switch_page(index))
        return button

    def switch_page(self, index):
        self.stack.setCurrentIndex(index)
        for nav_index, button in enumerate((self.record_nav, self.settings_nav)):
            button.setProperty("active", nav_index == index)
            button.style().unpolish(button)
            button.style().polish(button)

    def record_page(self):
        page = QWidget()
        self.record_layout = QBoxLayout(QBoxLayout.LeftToRight, page)
        self.record_layout.setContentsMargins(34, 30, 34, 30)
        self.record_layout.setSpacing(24)
        self.record_main_panel = QWidget()
        main = QVBoxLayout(self.record_main_panel)
        main.setSpacing(10)
        self.record_title = QLabel(self.tr("recording"))
        self.record_title.setObjectName("pageTitle")
        self.status_label = QLabel(self.tr("ready"))
        self.status_label.setObjectName("statusLabel")
        self.status_label.setProperty("state", "ready")
        self.transcription_progress = QProgressBar()
        self.transcription_progress.setObjectName("transcriptionProgress")
        self.transcription_progress.setRange(0, 100)
        self.transcription_progress.setValue(0)
        self.transcription_progress.setTextVisible(True)
        self.transcription_progress.setFormat("%p%")
        self.transcription_progress.setVisible(False)
        self.badge_panel = QWidget()
        self.device_row = QGridLayout(self.badge_panel)
        self.device_row.setContentsMargins(0, 0, 0, 0)
        self.device_row.setHorizontalSpacing(8)
        self.device_row.setVerticalSpacing(8)
        self.micro_badge = Badge("mic.svg", self.tr("micro_check"))
        self.system_badge = Badge("audio.svg", self.tr("audio_check"))
        self.model_badge = Badge("model.svg", self.tr("model_badge", model="medium"))
        self.compute_badge = Badge("bolt.svg", self.tr("transcription_check"))
        self.badges = (self.micro_badge, self.system_badge, self.model_badge, self.compute_badge)
        for badge in self.badges:
            badge.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.arrange_badges(3)
        self.record_center = QFrame()
        self.record_center.setObjectName("recordCenter")
        self.center_layout = QBoxLayout(QBoxLayout.LeftToRight, self.record_center)
        self.center_layout.setContentsMargins(18, 14, 18, 14)
        self.center_layout.setSpacing(14)
        self.record_controls = QWidget()
        self.record_controls.setObjectName("recordControls")
        controls_layout = QHBoxLayout(self.record_controls)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(12)
        self.start_button = QPushButton(self.tr("start"))
        self.start_button.setIcon(QIcon(str(asset_path("start.svg"))))
        self.start_button.setIconSize(QSize(18, 18))
        self.start_button.setObjectName("startButton")
        self.start_button.clicked.connect(self.toggle_recording)
        self.import_button = QPushButton(self.tr("import_audio"))
        self.import_button.setIcon(QIcon(str(asset_path("import.svg"))))
        self.import_button.setIconSize(QSize(18, 18))
        self.import_button.setObjectName("importButton")
        self.import_button.clicked.connect(self.import_audio_file)
        self.timer_label = QLabel("00:00")
        self.timer_label.setObjectName("timerLabel")
        controls_layout.addWidget(self.start_button)
        controls_layout.addWidget(self.import_button)
        controls_layout.addWidget(self.timer_label)
        self.waveform = WaveformWidget()
        self.waveform.setMinimumHeight(58)
        self.waveform.setMaximumHeight(74)
        self.center_layout.addWidget(self.record_controls, 0, Qt.AlignVCenter)
        self.center_layout.addWidget(self.waveform, 1)
        main.addWidget(self.record_title)
        main.addWidget(self.status_label)
        main.addWidget(self.transcription_progress)
        main.addWidget(self.badge_panel)
        main.addWidget(self.record_center, 1)
        self.history_panel = QFrame()
        self.history_panel.setObjectName("panel")
        right_layout = QVBoxLayout(self.history_panel)
        right_layout.setContentsMargins(16, 16, 16, 16)
        right_layout.setSpacing(8)
        self.recent_title = QLabel(self.tr("recent_sessions"))
        self.recent_title.setObjectName("sectionTitle")
        self.session_search_input = QLineEdit()
        self.session_search_input.setObjectName("sessionSearchInput")
        self.session_search_input.setPlaceholderText(self.tr("search_sessions"))
        self.session_search_input.textChanged.connect(self.filter_sessions)
        self.recent_empty_label = QLabel(self.tr("empty_sessions"))
        self.recent_empty_label.setObjectName("emptyText")
        self.recent_empty_label.setAlignment(Qt.AlignCenter)
        self.recent_list = QListWidget()
        self.recent_list.itemSelectionChanged.connect(self.show_selected_session)
        self.recent_list.itemClicked.connect(lambda item: self.select_session(item.data(Qt.UserRole)))
        self.recent_list.setMinimumHeight(118)
        self.recent_list.setSpacing(6)
        transcript_box = QFrame()
        transcript_box.setObjectName("transcriptBox")
        transcript_layout = QVBoxLayout(transcript_box)
        transcript_layout.setContentsMargins(0, 0, 0, 0)
        transcript_layout.setSpacing(0)
        transcript_header = QHBoxLayout()
        transcript_header.setContentsMargins(12, 8, 12, 6)
        self.transcript_title = QLabel(self.tr("transcript"))
        self.transcript_title.setObjectName("sectionTitle")
        self.copy_button = self.svg_icon_button("copy.svg", self.tr("copy"))
        self.copy_button.setProperty("normalIcon", "copy.svg")
        self.copy_button.setProperty("hoverIcon", "copy-hover.svg")
        self.copy_button.setEnabled(False)
        self.copy_button.clicked.connect(self.copy_transcript)
        self.export_button = self.svg_icon_button("export.svg", self.tr("export"))
        self.export_button.setProperty("normalIcon", "export.svg")
        self.export_button.setProperty("hoverIcon", "export-hover.svg")
        self.export_button.setEnabled(False)
        self.export_button.clicked.connect(self.export_transcript)
        transcript_header.addWidget(self.transcript_title)
        transcript_header.addStretch()
        transcript_header.addWidget(self.copy_button)
        transcript_header.addWidget(self.export_button)
        self.transcript_preview = QTextEdit()
        self.transcript_preview.setReadOnly(True)
        self.transcript_preview.setObjectName("transcriptPreview")
        self.transcript_preview.setPlaceholderText(self.tr("select_session"))
        transcript_layout.addLayout(transcript_header)
        transcript_layout.addWidget(self.transcript_preview)
        sessions_page = QWidget()
        sessions_layout = QVBoxLayout(sessions_page)
        sessions_layout.setContentsMargins(0, 0, 0, 0)
        sessions_layout.setSpacing(8)
        sessions_layout.addWidget(self.session_search_input)
        sessions_layout.addWidget(self.recent_empty_label)
        sessions_layout.addWidget(self.recent_list)
        self.history_tabs = QTabWidget()
        self.history_tabs.setObjectName("historyTabs")
        self.history_tabs.addTab(sessions_page, self.tr("sessions_tab"))
        self.history_tabs.addTab(transcript_box, self.tr("transcript_tab"))
        right_layout.addWidget(self.recent_title)
        right_layout.addWidget(self.history_tabs, 1)
        self.record_layout.addWidget(self.record_main_panel, 3)
        self.record_layout.addWidget(self.history_panel, 2)
        return page

    def arrange_badges(self, columns):
        for index, badge in enumerate(self.badges):
            self.device_row.addWidget(badge, index // columns, index % columns)

    def clear_badge_layout(self):
        for badge in (self.micro_badge, self.system_badge, self.model_badge, self.compute_badge):
            self.device_row.removeWidget(badge)

    def settings_page(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setObjectName("pageScroll")
        page = QWidget()
        scroll.setWidget(page)
        layout = QVBoxLayout(page)
        layout.setContentsMargins(34, 30, 34, 30)
        layout.setSpacing(16)
        self.settings_title = QLabel(self.tr("settings"))
        self.settings_title.setObjectName("pageTitle")
        self.runtime_refresh_button = QPushButton(self.tr("verify_gpu"))
        self.runtime_refresh_button.clicked.connect(self.show_gpu_status)
        self.model_combo = self.combo(["small", "medium", "large-v3"])
        self.device_combo = NoWheelComboBox()
        self.device_combo.addItem("GPU", "cuda")
        self.device_combo.addItem("CPU", "cpu")
        self.device_combo.currentIndexChanged.connect(self.on_device_changed)
        self.compute_combo = self.combo(["int8_float16", "float16", "int8"])
        self.interface_language_combo = NoWheelComboBox()
        self.interface_language_combo.addItem(self.tr("english"), "en")
        self.interface_language_combo.addItem(self.tr("french"), "fr")
        self.micro_combo = NoWheelComboBox()
        self.mic_gain_input = NoWheelDoubleSpinBox()
        self.mic_gain_input.setRange(0.5, 4.0)
        self.mic_gain_input.setSingleStep(0.1)
        self.mic_gain_input.setDecimals(1)
        self.mic_gain_input.setSuffix("x")
        self.mic_gain_input.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.mic_gain_minus = QToolButton()
        self.mic_gain_minus.setText("-")
        self.mic_gain_minus.setObjectName("gainButton")
        self.mic_gain_minus.clicked.connect(lambda: self.mic_gain_input.stepBy(-1))
        self.mic_gain_plus = QToolButton()
        self.mic_gain_plus.setText("+")
        self.mic_gain_plus.setObjectName("gainButton")
        self.mic_gain_plus.clicked.connect(lambda: self.mic_gain_input.stepBy(1))
        mic_gain_control = QWidget()
        mic_gain_control.setObjectName("gainControl")
        mic_gain_layout = QHBoxLayout(mic_gain_control)
        mic_gain_layout.setContentsMargins(0, 0, 0, 0)
        mic_gain_layout.setSpacing(6)
        mic_gain_layout.addWidget(self.mic_gain_input, 1)
        mic_gain_layout.addWidget(self.mic_gain_minus)
        mic_gain_layout.addWidget(self.mic_gain_plus)
        self.system_output_combo = NoWheelComboBox()
        self.output_dir_input = QLineEdit()
        self.output_dir_button = QPushButton(self.tr("browse"))
        self.output_dir_button.clicked.connect(self.choose_output_dir)
        self.form_labels = {}
        self.section_labels = {}
        transcription_section = self.section("transcription", "bolt.svg")
        transcription_layout = transcription_section.layout()
        transcription_layout.addWidget(self.form_row("model", self.model_combo))
        transcription_layout.addWidget(self.form_row("device", self.device_combo))
        transcription_layout.addWidget(self.form_row("compute", self.compute_combo))
        transcription_layout.addWidget(self.runtime_refresh_button)
        audio_section = self.section("audio", "audio.svg")
        audio_layout = audio_section.layout()
        audio_layout.addWidget(self.form_row("microphone", self.micro_combo))
        audio_layout.addWidget(self.form_row("mic_gain", mic_gain_control))
        audio_layout.addWidget(self.form_row("system_output", self.system_output_combo))
        interface_section = self.section("interface", "language.svg")
        interface_section.layout().addWidget(self.form_row("interface_language", self.interface_language_combo))
        output_row = QWidget()
        output_layout = QHBoxLayout(output_row)
        output_layout.setContentsMargins(0, 0, 0, 0)
        output_layout.setSpacing(10)
        output_layout.addWidget(self.output_dir_input)
        output_layout.addWidget(self.output_dir_button)
        storage_section = self.section("storage", "storage.svg")
        storage_section.layout().addWidget(self.form_row("output_folder", output_row))
        layout.addWidget(self.settings_title)
        layout.addWidget(transcription_section)
        layout.addWidget(audio_section)
        layout.addWidget(interface_section)
        layout.addWidget(storage_section)
        layout.addStretch()
        return scroll

    def section(self, title_key, icon_name=None):
        box = QFrame()
        box.setObjectName("settingsSection")
        layout = QVBoxLayout(box)
        layout.setContentsMargins(18, 16, 18, 18)
        layout.setSpacing(12)
        header = QWidget()
        header.setObjectName("sectionHeader")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(8)
        if icon_name:
            icon = QLabel()
            icon.setObjectName("sectionIcon")
            icon.setPixmap(QIcon(str(asset_path(icon_name))).pixmap(16, 16))
            header_layout.addWidget(icon, 0, Qt.AlignVCenter)
        label = QLabel(self.tr(title_key))
        label.setObjectName("sectionTitle")
        self.section_labels[title_key] = label
        header_layout.addWidget(label, 0, Qt.AlignVCenter)
        header_layout.addStretch()
        layout.addWidget(header)
        return box

    def combo(self, values):
        box = NoWheelComboBox()
        box.addItems(values)
        return box

    def form_row(self, label_key, widget):
        row = QWidget()
        row.setObjectName("formRow")
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        name = QLabel(self.tr(label_key))
        name.setObjectName("formLabel")
        name.setWordWrap(True)
        self.form_labels[label_key] = name
        layout.addWidget(name, 1)
        layout.addWidget(widget, 3)
        return row

    def icon_button(self, standard_icon, tooltip):
        button = QToolButton()
        button.setIcon(self.style().standardIcon(standard_icon))
        button.setToolTip(tooltip)
        button.setObjectName("iconButton")
        return button

    def svg_icon_button(self, name, tooltip):
        return HoverIconToolButton(name, tooltip)

    def set_button_icon(self, button, name):
        if hasattr(button, "set_named_icon"):
            button.set_named_icon(name)
        else:
            button.setIcon(QIcon(str(asset_path(name))))

