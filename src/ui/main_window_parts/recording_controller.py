from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QFileDialog, QMessageBox

from src.resources import asset_path

from .workers import TranscriptionWorker


class MainWindowRecordingMixin:
    def import_audio_file(self):
        if self.recorder.running or self.transcription_running:
            return
        selected, _ = QFileDialog.getOpenFileName(self, self.tr("import_audio"), "", self.tr("audio_files"))
        if selected:
            self.import_audio_path(selected)

    def import_audio_path(self, path):
        if self.recorder.running or self.transcription_running:
            return
        try:
            self.settings = self.collect_settings()
            self.storage.save_settings(self.settings)
            self.storage.update_base_dir(self.settings["output_dir"])
            self.transcription.configure(self.settings)
            self.current_session_id, self.current_audio_path, duration = self.audio_importer.import_file(path, self.storage)
            self.start_transcription(self.current_audio_path, duration)
        except Exception as exc:
            QMessageBox.warning(self, self.tr("import_error_title"), str(exc))

    def dragEnterEvent(self, event):
        if self.can_accept_audio_drop(event):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if self.can_accept_audio_drop(event):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        if not self.can_accept_audio_drop(event):
            event.ignore()
            return
        urls = event.mimeData().urls()
        if urls:
            self.import_audio_path(urls[0].toLocalFile())
            event.acceptProposedAction()

    def can_accept_audio_drop(self, event):
        if self.recorder.running or self.transcription_running or not event.mimeData().hasUrls():
            return False
        urls = event.mimeData().urls()
        if len(urls) != 1 or not urls[0].isLocalFile():
            return False
        return self.audio_importer.is_supported(urls[0].toLocalFile())

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
            self.start_button.setText(self.tr("stop"))
            self.start_button.setIcon(QIcon(str(asset_path("stop.svg"))))
            self.status_label.setText(self.tr("recording_active"))
            self.status_label.setProperty("state", "recording")
            self.status_label.style().unpolish(self.status_label)
            self.status_label.style().polish(self.status_label)
            self.transcription_progress.setRange(0, 100)
            self.transcription_progress.setVisible(False)
            self.transcription_progress.setValue(0)
            self.start_button.setProperty("recording", True)
            self.import_button.setEnabled(False)
            self.start_button.style().unpolish(self.start_button)
            self.start_button.style().polish(self.start_button)
        except Exception as exc:
            QMessageBox.warning(self, self.tr("record_impossible"), str(exc))
            self.refresh_devices()

    def stop_recording(self):
        self.timer.stop()
        self.start_button.setEnabled(False)
        self.start_button.setText(self.tr("transcribing"))
        self.start_button.setIcon(QIcon(str(asset_path("transcribing.svg"))))
        self.start_button.setProperty("recording", False)
        self.start_button.style().unpolish(self.start_button)
        self.start_button.style().polish(self.start_button)
        audio_path, duration = self.recorder.stop()
        self.start_transcription(audio_path, duration)

    def start_transcription(self, audio_path, duration):
        self.refresh_runtime_status()
        self.start_button.setEnabled(False)
        self.start_button.setText(self.tr("transcribing"))
        self.start_button.setIcon(QIcon(str(asset_path("transcribing.svg"))))
        self.import_button.setEnabled(False)
        self.status_label.setText(self.tr("transcribing_status"))
        self.status_label.setProperty("state", "working")
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)
        self.transcription_progress.setRange(0, 100)
        self.transcription_progress.setFormat("%p%")
        self.transcription_progress.setValue(0)
        self.transcription_progress.setVisible(True)
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
        self.status_label.setText(self.tr("transcription_done"))
        self.status_label.setProperty("state", "done")
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)
        self.transcription_progress.setVisible(False)
        self.transcription_progress.setValue(0)
        self.start_button.setText(self.tr("start"))
        self.start_button.setIcon(QIcon(str(asset_path("start.svg"))))
        self.start_button.setProperty("recording", False)
        self.start_button.style().unpolish(self.start_button)
        self.start_button.style().polish(self.start_button)
        self.start_button.setEnabled(True)
        self.import_button.setEnabled(True)
        self.timer_label.setText("00:00")
        self.load_history()
        self.select_session(session.id)

    def on_transcription_failed(self, message):
        self.transcription_running = False
        self.status_label.setText(self.tr("transcription_error"))
        self.status_label.setProperty("state", "error")
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)
        self.transcription_progress.setRange(0, 100)
        self.transcription_progress.setFormat("%p%")
        self.transcription_progress.setVisible(False)
        self.transcription_progress.setValue(0)
        self.start_button.setText(self.tr("start"))
        self.start_button.setIcon(QIcon(str(asset_path("start.svg"))))
        self.start_button.setProperty("recording", False)
        self.start_button.style().unpolish(self.start_button)
        self.start_button.style().polish(self.start_button)
        self.start_button.setEnabled(True)
        self.import_button.setEnabled(True)
        QMessageBox.critical(self, self.tr("error"), message)

    def on_transcription_progress(self, value):
        self.transcription_progress.setVisible(True)
        self.transcription_progress.setRange(0, 100)
        self.transcription_progress.setFormat("%p%")
        self.transcription_progress.setValue(max(0, min(100, int(value))))

    def closeEvent(self, event):
        if not self.recorder.running and not self.transcription_running:
            event.accept()
            return
        message = self.tr("close_recording") if self.recorder.running else self.tr("close_transcription")
        answer = QMessageBox.question(self, self.tr("close_title"), message, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if answer == QMessageBox.Yes:
            if self.recorder.running:
                self.recorder.stop()
            event.accept()
        else:
            event.ignore()

