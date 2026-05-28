import shutil
import wave
from pathlib import Path


class AudioImportService:
    ALLOWED_EXTENSIONS = {".wav", ".mp3", ".m4a", ".flac", ".ogg", ".aac", ".wma"}

    def is_supported(self, source_path):
        return Path(source_path).suffix.lower() in self.ALLOWED_EXTENSIONS

    def import_file(self, source_path, storage):
        source = Path(source_path)
        if not source.exists() or not source.is_file():
            raise FileNotFoundError(str(source))
        if source.suffix.lower() not in self.ALLOWED_EXTENSIONS:
            raise ValueError("Format audio non supporte.")
        session_id, audio_path, _ = storage.create_paths()
        destination = audio_path.with_suffix(source.suffix.lower())
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        return session_id, destination, self.duration_seconds(destination)

    def duration_seconds(self, path):
        if Path(path).suffix.lower() != ".wav":
            return 0
        try:
            with wave.open(str(path), "rb") as audio:
                frames = audio.getnframes()
                rate = audio.getframerate()
                return int(frames / rate) if rate else 0
        except (wave.Error, OSError, EOFError):
            return 0
