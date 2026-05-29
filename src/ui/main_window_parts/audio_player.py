from pathlib import Path

from PySide6.QtCore import QSize, QUrl
from PySide6.QtGui import QIcon
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
from PySide6.QtWidgets import QMessageBox

from src.resources import asset_path


class MainWindowAudioPlayerMixin:
    def setup_audio_player(self):
        self.audio_output = QAudioOutput(self)
        self.audio_player = QMediaPlayer(self)
        self.audio_player.setAudioOutput(self.audio_output)
        self.audio_output.setVolume(0.8)
        self.audio_player.positionChanged.connect(self.on_audio_position_changed)
        self.audio_player.durationChanged.connect(self.on_audio_duration_changed)
        self.audio_player.playbackStateChanged.connect(self.on_audio_state_changed)
        self.loaded_audio_session_id = None
        self.audio_duration_ms = 0
        self.audio_play_button.setText("")
        self.audio_play_button.setFixedSize(30, 30)
        self.audio_play_button.setIconSize(QSize(16, 16))
        self.reset_audio_player_ui()

    def load_audio_player_session(self, session):
        if not hasattr(self, "audio_player"):
            return
        if not session or not session.audio_path or not Path(session.audio_path).exists():
            self.audio_player.stop()
            self.audio_player.setSource(QUrl())
            self.loaded_audio_session_id = None
            self.audio_duration_ms = 0
            self.reset_audio_player_ui()
            return
        if self.loaded_audio_session_id == session.id:
            return
        self.audio_player.stop()
        self.loaded_audio_session_id = session.id
        self.audio_duration_ms = 0
        self.audio_player.setSource(QUrl.fromLocalFile(str(Path(session.audio_path))))
        self.audio_play_button.setEnabled(True)
        self.audio_position_slider.setEnabled(True)
        self.audio_position_slider.setRange(0, max(0, int(session.duration_seconds * 1000)))
        self.audio_position_slider.setValue(0)
        self.audio_time_label.setText(f"00:00 / {self.format_duration(session.duration_seconds)}")
        self.audio_play_button.setIcon(QIcon(str(asset_path("play.svg"))))
        self.audio_play_button.setToolTip(self.tr("play_audio"))

    def reset_audio_player_ui(self):
        if not hasattr(self, "audio_play_button"):
            return
        self.audio_play_button.setText("")
        self.audio_play_button.setIcon(QIcon(str(asset_path("play.svg"))))
        self.audio_play_button.setToolTip(self.tr("play_audio"))
        self.audio_play_button.setEnabled(False)
        self.audio_position_slider.blockSignals(True)
        self.audio_position_slider.setRange(0, 0)
        self.audio_position_slider.setValue(0)
        self.audio_position_slider.blockSignals(False)
        self.audio_position_slider.setEnabled(False)
        self.audio_time_label.setText("00:00 / 00:00")

    def toggle_audio_playback(self):
        if not self.loaded_audio_session_id:
            return
        if self.audio_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.audio_player.pause()
        else:
            self.audio_player.play()

    def play_selected_audio(self):
        session = self.selected_session()
        if not session:
            return
        if not session.audio_path.exists():
            self.audio_player.stop()
            self.reset_audio_player_ui()
            QMessageBox.warning(self, self.tr("audio_missing_title"), self.tr("audio_missing_message"))
            return
        self.load_audio_player_session(session)
        self.audio_player.play()

    def seek_audio_position(self, position):
        if self.loaded_audio_session_id:
            self.audio_player.setPosition(int(position))

    def on_audio_position_changed(self, position):
        if self.audio_position_slider.isSliderDown():
            return
        self.audio_position_slider.blockSignals(True)
        self.audio_position_slider.setValue(int(position))
        self.audio_position_slider.blockSignals(False)
        self.update_audio_time_label(position, self.audio_duration_ms)

    def on_audio_duration_changed(self, duration):
        self.audio_duration_ms = max(0, int(duration))
        self.audio_position_slider.setRange(0, self.audio_duration_ms)
        self.update_audio_time_label(self.audio_player.position(), self.audio_duration_ms)

    def on_audio_state_changed(self, state):
        if state == QMediaPlayer.PlaybackState.PlayingState:
            self.audio_play_button.setIcon(QIcon(str(asset_path("stop.svg"))))
            self.audio_play_button.setToolTip(self.tr("pause_audio"))
        else:
            self.audio_play_button.setIcon(QIcon(str(asset_path("play.svg"))))
            self.audio_play_button.setToolTip(self.tr("play_audio"))

    def update_audio_time_label(self, position, duration):
        self.audio_time_label.setText(f"{self.format_duration_ms(position)} / {self.format_duration_ms(duration)}")

    def format_duration_ms(self, milliseconds):
        seconds = max(0, int(milliseconds / 1000))
        return f"{seconds // 60:02d}:{seconds % 60:02d}"

    def stop_audio_player(self):
        if hasattr(self, "audio_player"):
            self.audio_player.stop()
            self.audio_player.setSource(QUrl())
            self.loaded_audio_session_id = None
