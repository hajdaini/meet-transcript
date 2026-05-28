import json
import re
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from src.models import Session


class StorageService:
    def __init__(self, base_dir: Path | None = None):
        self.base_dir = base_dir or Path.cwd() / "transcripts"
        self.audio_dir = self.base_dir / "audio"
        self.text_dir = self.base_dir / "text"
        self.history_path = self.base_dir / "history.json"
        self.settings_path = Path.cwd() / "settings.json"
        self.audio_dir.mkdir(parents=True, exist_ok=True)
        self.text_dir.mkdir(parents=True, exist_ok=True)
        if not self.history_path.exists():
            self.history_path.write_text("[]", encoding="utf-8")
        if not self.settings_path.exists():
            self.save_settings(self.default_settings())

    def create_paths(self):
        session_id = datetime.now().strftime("%Y%m%d-%H%M%S") + "-" + uuid4().hex[:8]
        return session_id, self.audio_dir / f"{session_id}.wav", self.text_dir / f"{session_id}.txt"

    def update_base_dir(self, base_dir):
        self.base_dir = Path(base_dir)
        self.audio_dir = self.base_dir / "audio"
        self.text_dir = self.base_dir / "text"
        self.history_path = self.base_dir / "history.json"
        self.settings_path = Path.cwd() / "settings.json"
        self.audio_dir.mkdir(parents=True, exist_ok=True)
        self.text_dir.mkdir(parents=True, exist_ok=True)
        if not self.history_path.exists():
            self.history_path.write_text("[]", encoding="utf-8")
        if not self.settings_path.exists():
            self.save_settings(self.default_settings())

    def save_session(self, session_id, audio_path, transcript, duration_seconds, language):
        transcript_path = self.text_dir / f"{session_id}.txt"
        title = self.next_session_title()
        transcript_path.write_text(transcript, encoding="utf-8")
        session = Session(
            id=session_id,
            title=title,
            created_at=datetime.now(),
            duration_seconds=duration_seconds,
            audio_path=Path(audio_path),
            transcript_path=transcript_path,
            transcript=transcript,
            language=language,
        )
        items = self.load_raw()
        items.insert(0, self.to_dict(session))
        self.history_path.write_text(json.dumps(items, indent=2, ensure_ascii=False), encoding="utf-8")
        return session

    def next_session_title(self):
        highest = 0
        for item in self.load_raw():
            match = re.fullmatch(r"Session (\d+)", item.get("title", ""))
            if match:
                highest = max(highest, int(match.group(1)))
        return f"Session {highest + 1}"

    def load_sessions(self):
        sessions = []
        for item in self.load_raw():
            sessions.append(
                Session(
                    id=item["id"],
                    title=item["title"],
                    created_at=datetime.fromisoformat(item["created_at"]),
                    duration_seconds=int(item["duration_seconds"]),
                    audio_path=Path(item["audio_path"]),
                    transcript_path=Path(item["transcript_path"]),
                    transcript=item.get("transcript", ""),
                    language=item.get("language", "auto"),
                )
            )
        return sessions

    def load_raw(self):
        try:
            return json.loads(self.history_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def save_raw(self, items):
        self.history_path.write_text(json.dumps(items, indent=2, ensure_ascii=False), encoding="utf-8")

    def default_settings(self):
        return {
            "model": "medium",
            "device": "cuda",
            "compute_type": "int8_float16",
            "require_gpu": True,
            "languages": ["auto"],
            "progress_chunk_seconds": 5,
            "microphone": "",
            "mic_gain": 1.8,
            "system_output": "",
            "output_dir": str(self.base_dir),
        }

    def load_settings(self):
        try:
            settings = json.loads(self.settings_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, FileNotFoundError):
            settings = {}
        default = self.default_settings()
        default.update(settings)
        if set(default.get("languages", [])) == {"fr", "en"}:
            default["languages"] = ["auto"]
        return default

    def save_settings(self, settings):
        self.settings_path.write_text(json.dumps(settings, indent=2, ensure_ascii=False), encoding="utf-8")

    def rename_session(self, session_id, title):
        items = self.load_raw()
        for item in items:
            if item["id"] == session_id:
                item["title"] = title
                self.save_raw(items)
                return True
        return False

    def delete_session(self, session_id):
        items = self.load_raw()
        kept = []
        removed = None
        for item in items:
            if item["id"] == session_id:
                removed = item
            else:
                kept.append(item)
        if not removed:
            return False
        self.delete_file(Path(removed.get("audio_path", "")), self.audio_dir)
        self.delete_file(Path(removed.get("transcript_path", "")), self.text_dir)
        self.save_raw(kept)
        return True

    def delete_file(self, path, allowed_dir):
        try:
            resolved = path.resolve()
            allowed = allowed_dir.resolve()
            if resolved.exists() and (resolved == allowed or allowed in resolved.parents):
                resolved.unlink()
        except OSError:
            pass

    def to_dict(self, session):
        return {
            "id": session.id,
            "title": session.title,
            "created_at": session.created_at.isoformat(),
            "duration_seconds": session.duration_seconds,
            "audio_path": str(session.audio_path),
            "transcript_path": str(session.transcript_path),
            "transcript": session.transcript,
            "language": session.language,
        }
