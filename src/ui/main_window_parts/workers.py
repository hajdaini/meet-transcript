from PySide6.QtCore import QThread, Signal


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
