from PySide6.QtCore import QTimer
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QMainWindow, QSystemTrayIcon

from src.resources import asset_path
from src.services.audio import AudioRecorder
from src.services.audio_importer import AudioImportService
from src.services.storage import StorageService
from src.services.transcription import TranscriptionService

from .audio_player import MainWindowAudioPlayerMixin
from .history_controller import MainWindowHistoryMixin
from .recording_controller import MainWindowRecordingMixin
from .responsive import MainWindowResponsiveMixin
from .settings_controller import MainWindowSettingsMixin
from .styles import MainWindowStyleMixin
from .translations import TRANSLATIONS
from .ui_builder import MainWindowUiBuilderMixin


class MainWindow(
    MainWindowUiBuilderMixin,
    MainWindowSettingsMixin,
    MainWindowRecordingMixin,
    MainWindowAudioPlayerMixin,
    MainWindowHistoryMixin,
    MainWindowResponsiveMixin,
    MainWindowStyleMixin,
    QMainWindow,
):
    def __init__(self):
        super().__init__()
        self.storage = StorageService()
        self.settings = self.storage.load_settings()
        self.ui_language = self.settings.get("interface_language", "en")
        self.storage.update_base_dir(self.settings.get("output_dir", self.storage.base_dir))
        self.recorder = AudioRecorder()
        self.audio_importer = AudioImportService()
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
        self.setWindowIcon(QIcon(str(asset_path("app-icon.svg"))))
        self.setup_notifications()
        self.setMinimumSize(480, 670)
        self.resize(960, 810)
        self.setAcceptDrops(True)
        self.build_ui()
        self.setup_audio_player()
        self.apply_style()
        self.load_settings_to_ui()
        self.bind_auto_save()
        self.loading_settings = False
        self.refresh_devices()
        self.load_history()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)

    def tr(self, key, **values):
        language = self.settings.get("interface_language", self.ui_language)
        text = TRANSLATIONS.get(language, TRANSLATIONS["en"]).get(key, TRANSLATIONS["en"].get(key, key))
        return text.format(**values) if values else text

    def setup_notifications(self):
        self.tray_icon = QSystemTrayIcon(QIcon(str(asset_path("app-icon.svg"))), self)
        self.tray_icon.setToolTip("Meet Transcript")
        self.tray_icon.show()

    def notify_user(self, title, message, icon=QSystemTrayIcon.Information):
        if hasattr(self, "tray_icon") and QSystemTrayIcon.isSystemTrayAvailable():
            self.tray_icon.showMessage(title, message, icon, 4000)
