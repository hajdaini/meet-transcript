from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class Session:
    id: str
    title: str
    created_at: datetime
    duration_seconds: int
    audio_path: Path
    transcript_path: Path
    transcript: str
    language: str
