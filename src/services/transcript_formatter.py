import re
from dataclasses import dataclass


@dataclass
class TranscriptSegment:
    start: float
    end: float
    text: str


class SmartTranscriptFormatter:
    TRANSITION_MARKERS = (
        "alors", "ensuite", "maintenant", "concernant", "à propos", "a propos",
        "passons", "autre sujet", "deuxième point", "deuxieme point", "pour conclure",
        "en conclusion", "donc", "du coup", "par contre",
        "now", "next", "regarding", "about", "let's move", "lets move",
        "another point", "to conclude", "in conclusion", "however", "so",
    )

    def __init__(self, max_pause_seconds=1.8, max_block_seconds=45, max_block_words=90):
        self.max_pause_seconds = float(max_pause_seconds or 1.8)
        self.max_block_seconds = int(max_block_seconds or 45)
        self.max_block_words = int(max_block_words or 90)

    @classmethod
    def from_settings(cls, settings):
        settings = settings or {}
        return cls(
            max_pause_seconds=settings.get("transcript_max_pause_seconds", 1.8),
            max_block_seconds=settings.get("transcript_max_block_seconds", 45),
            max_block_words=settings.get("transcript_max_block_words", 90),
        )

    def format(self, segments):
        blocks = self.build_blocks(segments)
        if not blocks:
            return "Aucun texte detecte."
        return "\n\n".join(self.format_block(block) for block in blocks)

    def build_blocks(self, segments):
        blocks = []
        current = None

        for segment in segments:
            segment = self.normalize_segment(segment)
            if not segment:
                continue

            if current is None:
                current = self.new_block(segment)
                continue

            if self.should_start_new_block(current, segment):
                blocks.append(current)
                current = self.new_block(segment)
            else:
                self.append_segment(current, segment)

        if current:
            blocks.append(current)

        return blocks

    def normalize_segment(self, segment):
        text = re.sub(r"\s+", " ", getattr(segment, "text", "") or "").strip()
        if not text:
            return None
        start = max(0.0, float(getattr(segment, "start", 0.0) or 0.0))
        end = max(start, float(getattr(segment, "end", start) or start))
        return TranscriptSegment(start=start, end=end, text=text)

    def new_block(self, segment):
        return {
            "start": segment.start,
            "end": segment.end,
            "texts": [segment.text],
            "words": self.word_count(segment.text),
        }

    def append_segment(self, block, segment):
        block["end"] = max(block["end"], segment.end)
        block["texts"].append(segment.text)
        block["words"] += self.word_count(segment.text)

    def should_start_new_block(self, block, segment):
        pause = segment.start - block["end"]
        duration = block["end"] - block["start"]

        if pause >= self.max_pause_seconds:
            return True
        if duration >= self.max_block_seconds:
            return True
        if block["words"] >= self.max_block_words:
            return True
        if block["words"] >= 20 and self.starts_with_transition(segment.text):
            return True

        return False

    def starts_with_transition(self, text):
        normalized = self.normalize_text(text)
        return any(normalized.startswith(marker) for marker in self.TRANSITION_MARKERS)

    def normalize_text(self, text):
        text = (text or "").lower().strip()
        text = re.sub(r"^[\W_]+", "", text)
        return text

    def word_count(self, text):
        return len(re.findall(r"\b\w+\b", text or ""))

    def format_block(self, block):
        text = self.merge_texts(block["texts"])
        return f"[{self.format_timestamp(block['start'])}]\n{text}"

    def merge_texts(self, texts):
        content = " ".join(text.strip() for text in texts if text and text.strip())
        return re.sub(r"\s+", " ", content).strip()

    def format_timestamp(self, seconds):
        seconds = max(0, int(seconds or 0))
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        rest = seconds % 60
        if hours:
            return f"{hours:02d}:{minutes:02d}:{rest:02d}"
        return f"{minutes:02d}:{rest:02d}"
