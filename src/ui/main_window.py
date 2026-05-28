import os
from pathlib import Path

from PySide6.QtCore import QSize, QThread, QTimer, Signal, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication,
    QAbstractSpinBox,
    QBoxLayout,
    QComboBox,
    QDoubleSpinBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QInputDialog,
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

from src.services.audio import AudioRecorder
from src.services.storage import StorageService
from src.services.transcription import TranscriptionService
from src.ui.waveform import WaveformWidget


class Badge(QWidget):
    def __init__(self, icon_name, text):
        super().__init__()
        self.setObjectName("badge")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 5, 9, 5)
        layout.setSpacing(6)
        self.icon = QLabel()
        self.icon.setPixmap(QIcon(str(Path(__file__).resolve().parents[2] / "assets" / icon_name)).pixmap(14, 14))
        self.icon.setObjectName("badgeIcon")
        self.label = QLabel(text)
        self.label.setObjectName("badgeText")
        self.label.setWordWrap(False)
        layout.addWidget(self.icon, 0, Qt.AlignVCenter)
        layout.addWidget(self.label, 1, Qt.AlignVCenter)

    def setText(self, text):
        self.label.setText(text)

    def text(self):
        return self.label.text()


class TranscriptionWorker(QThread):
    finished_ok = Signal(object)
    failed = Signal(str)
    progress = Signal(int)

    def __init__(self, service, storage, session_id, audio_path, duration):
        super().__init__()
        self.service = service
        self.storage = storage
        self.session_id = session_id
        self.audio_path = audio_path
        self.duration = duration

    def run(self):
        try:
            result = self.service.transcribe(self.audio_path, self.progress.emit)
            session = self.storage.save_session(self.session_id, self.audio_path, result.text, self.duration, result.language)
            self.finished_ok.emit(session)
        except Exception as exc:
            self.failed.emit(str(exc))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.storage = StorageService()
        self.settings = self.storage.load_settings()
        self.storage.update_base_dir(self.settings.get("output_dir", self.storage.base_dir))
        self.recorder = AudioRecorder()
        self.transcription = TranscriptionService()
        self.transcription.configure(self.settings)
        self.current_session_id = None
        self.current_audio_path = None
        self.elapsed_seconds = 0
        self.worker = None
        self.sessions = []
        self.loading_settings = True
        self.is_compact = False
        self.transcription_running = False
        self.setWindowTitle("Meet Transcript")
        self.setWindowIcon(QIcon(str(Path(__file__).resolve().parents[2] / "assets" / "app-icon.svg")))
        self.setMinimumSize(760, 620)
        self.build_ui()
        self.apply_style()
        self.load_settings_to_ui()
        self.bind_auto_save()
        self.loading_settings = False
        self.refresh_devices()
        self.load_history()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)

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
        brand.setPixmap(QIcon(str(Path(__file__).resolve().parents[2] / "assets" / "app-icon.svg")).pixmap(22, 22))
        brand.setAlignment(Qt.AlignCenter)
        brand.setObjectName("brandIcon")
        self.record_nav = self.nav_button("mic.svg", "Enregistrement", 0)
        self.settings_nav = self.nav_button("settings.svg", "Paramètres", 1)
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
        button.setIcon(QIcon(str(Path(__file__).resolve().parents[2] / "assets" / icon_name)))
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
        header = QLabel("Enregistrement")
        header.setObjectName("pageTitle")
        self.status_label = QLabel("Prêt à enregistrer")
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
        self.micro_badge = Badge("mic.svg", "Micro: vérification")
        self.system_badge = Badge("audio.svg", "Audio: vérification")
        self.language_badge = Badge("language.svg", "Langue: Auto")
        self.model_badge = Badge("model.svg", "Modèle: medium")
        self.compute_badge = Badge("bolt.svg", "Transcription: vérification")
        self.badges = (self.micro_badge, self.system_badge, self.language_badge, self.model_badge, self.compute_badge)
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
        self.start_button = QPushButton("Démarrer")
        self.start_button.setObjectName("startButton")
        self.start_button.clicked.connect(self.toggle_recording)
        self.timer_label = QLabel("00:00")
        self.timer_label.setObjectName("timerLabel")
        controls_layout.addWidget(self.start_button)
        controls_layout.addWidget(self.timer_label)
        self.waveform = WaveformWidget()
        self.waveform.setMinimumHeight(58)
        self.waveform.setMaximumHeight(74)
        self.center_layout.addWidget(self.record_controls, 0, Qt.AlignVCenter)
        self.center_layout.addWidget(self.waveform, 1)
        main.addWidget(header)
        main.addWidget(self.status_label)
        main.addWidget(self.transcription_progress)
        main.addWidget(self.badge_panel)
        main.addWidget(self.record_center, 1)
        self.history_panel = QFrame()
        self.history_panel.setObjectName("panel")
        right_layout = QVBoxLayout(self.history_panel)
        right_layout.setContentsMargins(16, 16, 16, 16)
        right_layout.setSpacing(8)
        right_title = QLabel("Sessions récentes")
        right_title.setObjectName("sectionTitle")
        self.recent_empty_label = QLabel("Aucune session enregistrée")
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
        transcript_title = QLabel("Transcript")
        transcript_title.setObjectName("sectionTitle")
        self.copy_button = self.svg_icon_button("copy.svg", "Copier")
        self.copy_button.setProperty("normalIcon", "copy.svg")
        self.copy_button.setProperty("hoverIcon", "copy-hover.svg")
        self.copy_button.setEnabled(False)
        self.copy_button.clicked.connect(self.copy_transcript)
        transcript_header.addWidget(transcript_title)
        transcript_header.addStretch()
        transcript_header.addWidget(self.copy_button)
        self.transcript_preview = QTextEdit()
        self.transcript_preview.setReadOnly(True)
        self.transcript_preview.setObjectName("transcriptPreview")
        self.transcript_preview.setPlaceholderText("Sélectionnez une session pour afficher son transcript.")
        transcript_layout.addLayout(transcript_header)
        transcript_layout.addWidget(self.transcript_preview)
        sessions_page = QWidget()
        sessions_layout = QVBoxLayout(sessions_page)
        sessions_layout.setContentsMargins(0, 0, 0, 0)
        sessions_layout.setSpacing(8)
        sessions_layout.addWidget(self.recent_empty_label)
        sessions_layout.addWidget(self.recent_list)
        self.history_tabs = QTabWidget()
        self.history_tabs.setObjectName("historyTabs")
        self.history_tabs.addTab(sessions_page, "Sessions")
        self.history_tabs.addTab(transcript_box, "Transcript")
        right_layout.addWidget(right_title)
        right_layout.addWidget(self.history_tabs, 1)
        self.record_layout.addWidget(self.record_main_panel, 3)
        self.record_layout.addWidget(self.history_panel, 2)
        return page

    def arrange_badges(self, columns):
        for index, badge in enumerate(self.badges):
            self.device_row.addWidget(badge, index // columns, index % columns)

    def clear_badge_layout(self):
        for badge in (self.micro_badge, self.system_badge, self.language_badge, self.model_badge, self.compute_badge):
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
        title = QLabel("Paramètres")
        title.setObjectName("pageTitle")
        self.runtime_refresh_button = QPushButton("Vérifier GPU")
        self.runtime_refresh_button.clicked.connect(self.show_gpu_status)
        self.model_combo = self.combo(["small", "medium", "large-v3"])
        self.device_combo = QComboBox()
        self.device_combo.addItem("GPU", "cuda")
        self.device_combo.addItem("CPU", "cpu")
        self.device_combo.currentIndexChanged.connect(self.on_device_changed)
        self.compute_combo = self.combo(["int8_float16", "float16", "int8"])
        self.language_combo = QComboBox()
        self.language_combo.setObjectName("languageCombo")
        self.populate_language_combo()
        self.micro_combo = QComboBox()
        self.mic_gain_input = QDoubleSpinBox()
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
        self.system_output_combo = QComboBox()
        self.output_dir_input = QLineEdit()
        self.output_dir_button = QPushButton("Parcourir")
        self.output_dir_button.clicked.connect(self.choose_output_dir)
        transcription_section = self.section("Transcription", "bolt.svg")
        transcription_layout = transcription_section.layout()
        transcription_layout.addWidget(self.form_row("Modèle", self.model_combo))
        transcription_layout.addWidget(self.form_row("Device", self.device_combo))
        transcription_layout.addWidget(self.form_row("Compute", self.compute_combo))
        transcription_layout.addWidget(self.runtime_refresh_button)
        audio_section = self.section("Audio", "audio.svg")
        audio_layout = audio_section.layout()
        audio_layout.addWidget(self.form_row("Micro", self.micro_combo))
        audio_layout.addWidget(self.form_row("Gain micro", mic_gain_control))
        audio_layout.addWidget(self.form_row("Sortie audio système", self.system_output_combo))
        language_section = self.section("Langues", "language.svg")
        language_section.layout().addWidget(self.form_row("Détection", self.language_combo))
        output_row = QWidget()
        output_layout = QHBoxLayout(output_row)
        output_layout.setContentsMargins(0, 0, 0, 0)
        output_layout.setSpacing(10)
        output_layout.addWidget(self.output_dir_input)
        output_layout.addWidget(self.output_dir_button)
        storage_section = self.section("Stockage", "storage.svg")
        storage_section.layout().addWidget(self.form_row("Dossier de sortie", output_row))
        layout.addWidget(title)
        layout.addWidget(transcription_section)
        layout.addWidget(audio_section)
        layout.addWidget(language_section)
        layout.addWidget(storage_section)
        layout.addStretch()
        return scroll

    def section(self, title, icon_name=None):
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
            icon.setPixmap(QIcon(str(Path(__file__).resolve().parents[2] / "assets" / icon_name)).pixmap(16, 16))
            header_layout.addWidget(icon, 0, Qt.AlignVCenter)
        label = QLabel(title)
        label.setObjectName("sectionTitle")
        header_layout.addWidget(label, 0, Qt.AlignVCenter)
        header_layout.addStretch()
        layout.addWidget(header)
        return box

    def combo(self, values):
        box = QComboBox()
        box.addItems(values)
        return box

    def whisper_languages(self):
        return [
            ("auto", "Auto"),
            ("af", "Afrikaans"),
            ("am", "Amharic"),
            ("ar", "Arabic"),
            ("as", "Assamese"),
            ("az", "Azerbaijani"),
            ("ba", "Bashkir"),
            ("be", "Belarusian"),
            ("bg", "Bulgarian"),
            ("bn", "Bengali"),
            ("bo", "Tibetan"),
            ("br", "Breton"),
            ("bs", "Bosnian"),
            ("ca", "Catalan"),
            ("cs", "Czech"),
            ("cy", "Welsh"),
            ("da", "Danish"),
            ("de", "German"),
            ("el", "Greek"),
            ("en", "English"),
            ("es", "Spanish"),
            ("et", "Estonian"),
            ("eu", "Basque"),
            ("fa", "Persian"),
            ("fi", "Finnish"),
            ("fo", "Faroese"),
            ("fr", "French"),
            ("gl", "Galician"),
            ("gu", "Gujarati"),
            ("ha", "Hausa"),
            ("haw", "Hawaiian"),
            ("he", "Hebrew"),
            ("hi", "Hindi"),
            ("hr", "Croatian"),
            ("ht", "Haitian Creole"),
            ("hu", "Hungarian"),
            ("hy", "Armenian"),
            ("id", "Indonesian"),
            ("is", "Icelandic"),
            ("it", "Italian"),
            ("ja", "Japanese"),
            ("jw", "Javanese"),
            ("ka", "Georgian"),
            ("kk", "Kazakh"),
            ("km", "Khmer"),
            ("kn", "Kannada"),
            ("ko", "Korean"),
            ("la", "Latin"),
            ("lb", "Luxembourgish"),
            ("ln", "Lingala"),
            ("lo", "Lao"),
            ("lt", "Lithuanian"),
            ("lv", "Latvian"),
            ("mg", "Malagasy"),
            ("mi", "Maori"),
            ("mk", "Macedonian"),
            ("ml", "Malayalam"),
            ("mn", "Mongolian"),
            ("mr", "Marathi"),
            ("ms", "Malay"),
            ("mt", "Maltese"),
            ("my", "Myanmar"),
            ("ne", "Nepali"),
            ("nl", "Dutch"),
            ("nn", "Norwegian Nynorsk"),
            ("no", "Norwegian"),
            ("oc", "Occitan"),
            ("pa", "Punjabi"),
            ("pl", "Polish"),
            ("ps", "Pashto"),
            ("pt", "Portuguese"),
            ("ro", "Romanian"),
            ("ru", "Russian"),
            ("sa", "Sanskrit"),
            ("sd", "Sindhi"),
            ("si", "Sinhala"),
            ("sk", "Slovak"),
            ("sl", "Slovenian"),
            ("sn", "Shona"),
            ("so", "Somali"),
            ("sq", "Albanian"),
            ("sr", "Serbian"),
            ("su", "Sundanese"),
            ("sv", "Swedish"),
            ("sw", "Swahili"),
            ("ta", "Tamil"),
            ("te", "Telugu"),
            ("tg", "Tajik"),
            ("th", "Thai"),
            ("tk", "Turkmen"),
            ("tl", "Tagalog"),
            ("tr", "Turkish"),
            ("tt", "Tatar"),
            ("uk", "Ukrainian"),
            ("ur", "Urdu"),
            ("uz", "Uzbek"),
            ("vi", "Vietnamese"),
            ("yi", "Yiddish"),
            ("yo", "Yoruba"),
            ("zh", "Chinese"),
            ("yue", "Cantonese"),
        ]

    def populate_language_combo(self):
        self.language_combo.clear()
        self.language_combo.addItem("Auto", ["auto"])
        self.language_combo.addItem("Français + Anglais", ["fr", "en"])
        for code, name in self.whisper_languages():
            if code != "auto":
                self.language_combo.addItem(name, [code])

    def form_row(self, label, widget):
        row = QWidget()
        row.setObjectName("formRow")
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        name = QLabel(label)
        name.setObjectName("formLabel")
        name.setWordWrap(True)
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
        button = QToolButton()
        button.setIcon(QIcon(str(Path(__file__).resolve().parents[2] / "assets" / name)))
        button.setIconSize(QSize(15, 15))
        button.setToolTip(tooltip)
        button.setObjectName("iconButton")
        button.setFixedSize(28, 28)
        button.enterEvent = lambda event, item=button: self.set_button_icon(item, item.property("hoverIcon") or name)
        button.leaveEvent = lambda event, item=button: self.set_button_icon(item, item.property("normalIcon") or name)
        return button

    def set_button_icon(self, button, name):
        button.setIcon(QIcon(str(Path(__file__).resolve().parents[2] / "assets" / name)))

    def load_settings_to_ui(self):
        self.set_combo(self.model_combo, self.settings.get("model", "medium"))
        self.set_combo_data(self.device_combo, self.settings.get("device", "cuda"))
        self.set_combo(self.compute_combo, self.settings.get("compute_type", "int8_float16"))
        self.mic_gain_input.setValue(float(self.settings.get("mic_gain", 1.8)))
        self.set_selected_languages(self.settings.get("languages", ["auto"]))
        self.output_dir_input.setText(self.settings.get("output_dir", str(self.storage.base_dir)))
        self.refresh_device_choices()
        self.on_device_changed()

    def bind_auto_save(self):
        self.model_combo.currentIndexChanged.connect(self.auto_save_settings)
        self.device_combo.currentIndexChanged.connect(self.auto_save_settings)
        self.compute_combo.currentIndexChanged.connect(self.auto_save_settings)
        self.language_combo.currentIndexChanged.connect(self.auto_save_settings)
        self.language_combo.currentIndexChanged.connect(self.refresh_language_combo_style)
        self.micro_combo.currentIndexChanged.connect(self.auto_save_settings)
        self.mic_gain_input.valueChanged.connect(self.auto_save_settings)
        self.system_output_combo.currentIndexChanged.connect(self.auto_save_settings)
        self.output_dir_input.editingFinished.connect(self.auto_save_settings)

    def refresh_device_choices(self):
        self.micro_combo.clear()
        self.system_output_combo.clear()
        self.micro_combo.addItem("Auto", "")
        self.system_output_combo.addItem("Auto", "")
        for name in self.recorder.list_microphones():
            self.micro_combo.addItem(name, name)
        for name in self.recorder.list_system_outputs():
            self.system_output_combo.addItem(name, name)
        self.set_combo_data(self.micro_combo, self.settings.get("microphone", ""))
        self.set_combo_data(self.system_output_combo, self.settings.get("system_output", ""))

    def set_combo(self, combo, value):
        index = combo.findText(value)
        if index >= 0:
            combo.setCurrentIndex(index)

    def set_combo_data(self, combo, value):
        index = combo.findData(value)
        if index >= 0:
            combo.setCurrentIndex(index)

    def set_selected_languages(self, languages):
        languages = languages or ["auto"]
        normalized = sorted(languages)
        self.language_combo.blockSignals(True)
        target_index = 0
        for index in range(self.language_combo.count()):
            value = self.language_combo.itemData(index)
            if sorted(value or []) == normalized:
                target_index = index
                break
        self.language_combo.setCurrentIndex(target_index)
        self.language_combo.blockSignals(False)
        self.refresh_language_combo_style()

    def selected_languages(self):
        return self.language_combo.currentData() or ["auto"]

    def refresh_language_combo_style(self):
        self.language_combo.setProperty("selected", self.language_combo.currentData() != ["auto"])
        self.language_combo.style().unpolish(self.language_combo)
        self.language_combo.style().polish(self.language_combo)

    def on_device_changed(self):
        is_gpu = self.device_combo.currentData() == "cuda"
        if is_gpu:
            if self.compute_combo.currentText() == "int8":
                self.set_combo(self.compute_combo, "int8_float16")
        else:
            self.set_combo(self.compute_combo, "int8")
        self.refresh_runtime_status()

    def choose_output_dir(self):
        selected = QFileDialog.getExistingDirectory(self, "Dossier de sortie", self.output_dir_input.text())
        if selected:
            self.output_dir_input.setText(selected)
            self.auto_save_settings()

    def collect_settings(self):
        languages = self.selected_languages() or ["auto"]
        return {
            "model": self.model_combo.currentText(),
            "device": self.device_combo.currentData() or "cuda",
            "compute_type": "int8" if self.device_combo.currentData() == "cpu" else self.compute_combo.currentText(),
            "require_gpu": self.device_combo.currentData() == "cuda",
            "languages": languages,
            "microphone": self.micro_combo.currentData() or "",
            "mic_gain": round(float(self.mic_gain_input.value()), 2),
            "system_output": self.system_output_combo.currentData() or "",
            "output_dir": self.output_dir_input.text().strip() or str(Path.cwd() / "transcripts"),
        }

    def auto_save_settings(self):
        if self.loading_settings:
            return
        self.settings = self.collect_settings()
        self.storage.save_settings(self.settings)
        self.storage.update_base_dir(self.settings["output_dir"])
        self.transcription.configure(self.settings)
        self.refresh_devices()
        self.load_history()

    def refresh_devices(self):
        self.recorder.microphone = self.settings.get("microphone", "")
        self.recorder.mic_gain = float(self.settings.get("mic_gain", 1.8))
        self.recorder.system_output = self.settings.get("system_output", "")
        status = self.recorder.detect_devices()
        self.micro_badge.setText(f"Micro: {status.microphone_name}" if status.microphone_available else "Aucun micro")
        self.micro_badge.setProperty("state", "neutral" if status.microphone_available else "blocked")
        self.system_badge.setText(f"Audio: {status.system_name}" if status.system_audio_available else "Audio indisponible")
        self.system_badge.setProperty("state", "neutral" if status.system_audio_available else "blocked")
        languages = self.settings.get("languages", ["auto"])
        language_text = "Auto" if "auto" in languages else "/".join(language.upper() for language in languages)
        self.language_badge.setText("Langue: " + language_text)
        self.language_badge.setToolTip("Langues: " + language_text)
        self.language_badge.setProperty("state", "neutral")
        self.model_badge.setText(f"Modèle: {self.settings.get('model', 'medium')}")
        self.model_badge.setProperty("state", "neutral")
        for badge in (self.micro_badge, self.system_badge, self.language_badge, self.model_badge):
            badge.style().unpolish(badge)
            badge.style().polish(badge)
        self.refresh_runtime_status()

    def refresh_runtime_status(self):
        if hasattr(self, "model_combo"):
            self.transcription.configure(self.collect_settings())
        status = self.transcription.runtime_status()
        self.compute_badge.setText(f"Transcription: {status.backend}")
        self.compute_badge.setProperty("state", "neutral" if status.backend == "GPU" else "blocked" if "bloque" in status.backend else "neutral")
        self.compute_badge.style().unpolish(self.compute_badge)
        self.compute_badge.style().polish(self.compute_badge)
        return status

    def show_gpu_status(self):
        status = self.refresh_runtime_status()
        box = QMessageBox(self)
        if status.backend == "GPU":
            box.setIcon(QMessageBox.Information)
            box.setWindowTitle("GPU détecté")
            box.setText("GPU détecté")
            box.setInformativeText(status.message)
            box.setStyleSheet("QMessageBox { background: #101216; } QLabel { color: #62f0c8; } QPushButton { background: #143f35; color: #ffffff; padding: 8px 14px; border-radius: 8px; }")
        else:
            box.setIcon(QMessageBox.Critical)
            box.setWindowTitle("GPU indisponible")
            box.setText("GPU non disponible")
            box.setInformativeText(status.message)
            box.setStyleSheet("QMessageBox { background: #101216; } QLabel { color: #ffb4a8; } QPushButton { background: #4a1d1d; color: #ffffff; padding: 8px 14px; border-radius: 8px; }")
        box.exec()

    def toggle_recording(self):
        if self.recorder.running:
            self.stop_recording()
        else:
            self.start_recording()

    def start_recording(self):
        try:
            self.settings = self.collect_settings()
            self.storage.save_settings(self.settings)
            self.storage.update_base_dir(self.settings["output_dir"])
            self.transcription.configure(self.settings)
            self.current_session_id, self.current_audio_path, _ = self.storage.create_paths()
            self.recorder.start(self.current_audio_path, self.settings)
            self.elapsed_seconds = 0
            self.timer.start(200)
            self.start_button.setText("Arrêter")
            self.status_label.setText("Enregistrement en cours ...")
            self.status_label.setProperty("state", "recording")
            self.status_label.style().unpolish(self.status_label)
            self.status_label.style().polish(self.status_label)
            self.transcription_progress.setRange(0, 100)
            self.transcription_progress.setVisible(False)
            self.transcription_progress.setValue(0)
            self.start_button.setProperty("recording", True)
            self.start_button.style().unpolish(self.start_button)
            self.start_button.style().polish(self.start_button)
        except Exception as exc:
            QMessageBox.warning(self, "Enregistrement impossible", str(exc))
            self.refresh_devices()

    def stop_recording(self):
        self.timer.stop()
        self.start_button.setEnabled(False)
        self.start_button.setText("Transcription")
        self.start_button.setProperty("recording", False)
        self.start_button.style().unpolish(self.start_button)
        self.start_button.style().polish(self.start_button)
        status = self.refresh_runtime_status()
        self.status_label.setText("Transcription en cours")
        self.status_label.setProperty("state", "working")
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)
        self.transcription_progress.setRange(0, 100)
        self.transcription_progress.setFormat("%p%")
        self.transcription_progress.setValue(0)
        self.transcription_progress.setVisible(True)
        audio_path, duration = self.recorder.stop()
        self.worker = TranscriptionWorker(self.transcription, self.storage, self.current_session_id, audio_path, duration)
        self.transcription_running = True
        self.worker.progress.connect(self.on_transcription_progress)
        self.worker.finished_ok.connect(self.on_transcription_done)
        self.worker.failed.connect(self.on_transcription_failed)
        self.worker.start()

    def tick(self):
        self.elapsed_seconds += 0.2
        seconds = int(self.elapsed_seconds)
        self.timer_label.setText(f"{seconds // 60:02d}:{seconds % 60:02d}")
        self.waveform.set_level(self.recorder.last_level)

    def on_transcription_done(self, session):
        self.transcription_running = False
        self.status_label.setText("Transcription terminée")
        self.status_label.setProperty("state", "done")
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)
        self.transcription_progress.setVisible(False)
        self.transcription_progress.setValue(0)
        self.start_button.setText("Démarrer")
        self.start_button.setProperty("recording", False)
        self.start_button.style().unpolish(self.start_button)
        self.start_button.style().polish(self.start_button)
        self.start_button.setEnabled(True)
        self.timer_label.setText("00:00")
        self.load_history()
        self.select_session(session.id)

    def on_transcription_failed(self, message):
        self.transcription_running = False
        self.status_label.setText("Erreur transcription")
        self.status_label.setProperty("state", "error")
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)
        self.transcription_progress.setRange(0, 100)
        self.transcription_progress.setFormat("%p%")
        self.transcription_progress.setVisible(False)
        self.transcription_progress.setValue(0)
        self.start_button.setText("Démarrer")
        self.start_button.setProperty("recording", False)
        self.start_button.style().unpolish(self.start_button)
        self.start_button.style().polish(self.start_button)
        self.start_button.setEnabled(True)
        QMessageBox.critical(self, "Erreur", message)

    def on_transcription_progress(self, value):
        self.transcription_progress.setVisible(True)
        self.transcription_progress.setRange(0, 100)
        self.transcription_progress.setFormat("%p%")
        self.transcription_progress.setValue(max(0, min(100, int(value))))

    def closeEvent(self, event):
        if not self.recorder.running and not self.transcription_running:
            event.accept()
            return
        message = "Un enregistrement est en cours. Voulez-vous vraiment quitter ?" if self.recorder.running else "Une transcription est en cours. Voulez-vous vraiment quitter ?"
        answer = QMessageBox.question(self, "Quitter Meet Transcript", message, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if answer == QMessageBox.Yes:
            if self.recorder.running:
                self.recorder.stop()
            event.accept()
        else:
            event.ignore()

    def load_history(self):
        self.sessions = self.storage.load_sessions()
        self.recent_list.clear()
        self.recent_empty_label.setVisible(not self.sessions)
        self.recent_list.setVisible(bool(self.sessions))
        for session in self.sessions:
            item = QListWidgetItem()
            item.setData(Qt.UserRole, session.id)
            row = self.session_row(session)
            item.setSizeHint(row.minimumSizeHint())
            self.recent_list.addItem(item)
            self.recent_list.setItemWidget(item, row)

    def session_row(self, session):
        row = QWidget()
        row.setObjectName("sessionRow")
        layout = QHBoxLayout(row)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(4)
        duration = self.format_duration(session.duration_seconds)
        date_text = session.created_at.strftime("%d/%m/%Y %H:%M")
        content = QWidget()
        content.setObjectName("sessionContent")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(2)
        label = QPushButton(session.title)
        label.setObjectName("sessionButton")
        label.setCursor(Qt.PointingHandCursor)
        label.clicked.connect(lambda: self.select_session(session.id))
        meta = QWidget()
        meta.setObjectName("sessionMeta")
        meta_layout = QHBoxLayout(meta)
        meta_layout.setContentsMargins(5, 0, 0, 0)
        meta_layout.setSpacing(5)
        calendar_icon = QLabel()
        calendar_icon.setPixmap(QIcon(str(Path(__file__).resolve().parents[2] / "assets" / "calendar.svg")).pixmap(12, 12))
        date_label = QLabel(date_text)
        date_label.setObjectName("sessionMetaText")
        clock_icon = QLabel()
        clock_icon.setPixmap(QIcon(str(Path(__file__).resolve().parents[2] / "assets" / "clock.svg")).pixmap(12, 12))
        duration_label = QLabel(duration)
        duration_label.setObjectName("sessionMetaText")
        meta_layout.addWidget(calendar_icon, 0, Qt.AlignVCenter)
        meta_layout.addWidget(date_label, 0, Qt.AlignVCenter)
        meta_layout.addSpacing(8)
        meta_layout.addWidget(clock_icon, 0, Qt.AlignVCenter)
        meta_layout.addWidget(duration_label, 0, Qt.AlignVCenter)
        meta_layout.addStretch()
        content_layout.addWidget(label)
        content_layout.addWidget(meta)
        play_button = self.svg_icon_button("play.svg", "Écouter")
        rename_button = self.svg_icon_button("edit.svg", "Renommer")
        delete_button = self.svg_icon_button("trash.svg", "Supprimer")
        play_button.setProperty("role", "action")
        rename_button.setProperty("role", "action")
        delete_button.setProperty("role", "delete")
        play_button.setProperty("normalIcon", "play.svg")
        play_button.setProperty("hoverIcon", "play-hover.svg")
        rename_button.setProperty("normalIcon", "edit.svg")
        rename_button.setProperty("hoverIcon", "edit-hover.svg")
        delete_button.setProperty("normalIcon", "trash.svg")
        delete_button.setProperty("hoverIcon", "trash-hover.svg")
        play_button.clicked.connect(lambda: self.play_session(session.id))
        rename_button.clicked.connect(lambda: self.rename_session(session.id))
        delete_button.clicked.connect(lambda: self.delete_session(session.id))
        row.mousePressEvent = lambda event: self.select_session(session.id)
        layout.addWidget(content, 1, Qt.AlignVCenter)
        layout.addWidget(play_button, 0, Qt.AlignVCenter)
        layout.addWidget(rename_button, 0, Qt.AlignVCenter)
        layout.addWidget(delete_button, 0, Qt.AlignVCenter)
        row.setMinimumHeight(54)
        return row

    def format_duration(self, seconds):
        seconds = int(seconds)
        return f"{seconds // 60:02d}:{seconds % 60:02d}"

    def select_session(self, session_id):
        for index in range(self.recent_list.count()):
            item = self.recent_list.item(index)
            if item.data(Qt.UserRole) == session_id:
                self.recent_list.setCurrentItem(item)
                self.show_selected_session()
                self.history_tabs.setCurrentIndex(1)
                self.update_session_selection_styles()
                return

    def selected_session(self):
        item = self.recent_list.currentItem()
        if not item:
            return None
        session_id = item.data(Qt.UserRole)
        return next((session for session in self.sessions if session.id == session_id), None)

    def show_selected_session(self):
        session = self.selected_session()
        self.transcript_preview.setPlainText(session.transcript if session else "")
        self.copy_button.setEnabled(bool(session and session.transcript))
        self.update_session_selection_styles()

    def update_session_selection_styles(self):
        current = self.recent_list.currentItem()
        for index in range(self.recent_list.count()):
            item = self.recent_list.item(index)
            row = self.recent_list.itemWidget(item)
            selected = item is current
            if row:
                row.setProperty("selected", selected)
                row.style().unpolish(row)
                row.style().polish(row)

    def copy_transcript(self):
        session = self.selected_session()
        if session:
            QApplication.clipboard().setText(session.transcript)

    def rename_session(self, session_id):
        session = next((item for item in self.sessions if item.id == session_id), None)
        if not session:
            return
        title, ok = QInputDialog.getText(self, "Renommer", "Nom de l'enregistrement", text=session.title)
        title = title.strip()
        if ok and title:
            self.storage.rename_session(session.id, title)
            self.load_history()
            self.select_session(session.id)

    def play_session(self, session_id):
        session = next((item for item in self.sessions if item.id == session_id), None)
        if not session:
            return
        if not session.audio_path.exists():
            QMessageBox.warning(self, "Audio introuvable", "Le fichier audio de cette session est introuvable.")
            return
        os.startfile(session.audio_path)

    def delete_session(self, session_id):
        session = next((item for item in self.sessions if item.id == session_id), None)
        if not session:
            return
        answer = QMessageBox.question(self, "Supprimer", f"Supprimer {session.title} ?")
        if answer == QMessageBox.Yes:
            self.storage.delete_session(session.id)
            self.load_history()
            self.transcript_preview.clear()
            self.copy_button.setEnabled(False)

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
            self.timer_label.setMinimumWidth(110)
            self.waveform.setMinimumHeight(86)
            self.waveform.setMaximumHeight(100)
            self.waveform.setMinimumWidth(140)
            self.waveform.setMaximumWidth(16777215)
            self.history_panel.setMinimumHeight(0)
            self.recent_list.setMinimumHeight(110)

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
            #timerLabel { font-size: 21pt; font-weight: 700; color: #ffffff; }
            QListWidget, QTextEdit, QComboBox, QLineEdit, QDoubleSpinBox { background: #101216; border: 1px solid #2a313b; border-radius: 8px; padding: 8px; color: #edf2f6; selection-background-color: #143f35; }
            #languageCombo[selected="true"] { color: #62f0c8; border: 1px solid #14b8a6; background: #101216; }
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
