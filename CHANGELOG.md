# Changelog

## Current development version

### Added

- Audio file import from the recording page.
- Drag & drop audio import.
- Built-in audio player inside the transcript tab.
- Play / pause support without opening the system media player.
- TXT export button next to copy.
- Session search above the recent sessions list.
- Search support across title, transcript, date, and language.
- Automatic title generation with YAKE.
- Duplicate title handling with `(2)`, `(3)`, etc.
- Desktop notifications for transcription success and failure.
- Timestamped transcript sections.
- Transcript stats:
  - word count
  - words per minute
- Smart transcript formatter without external AI.
- Configurable transcript section settings:
  - pause threshold
  - maximum block duration
  - maximum block word count
- Optional `No microphone` mode for system-audio-only recording.
- No-wheel combo boxes and spin boxes to prevent accidental settings changes while scrolling.
- Reusable UI widgets folder.
- SVG icons for start, stop, import, export, and player actions.

### Changed

- Refactored `main_window.py` into focused modules.
- Moved reusable UI widgets out of the main window logic.
- Simplified the layout to a compact single-column view.
- Reduced the recording controls size.
- Reduced waveform density and horizontal footprint.
- Improved recent session row responsiveness.
- Improved session action buttons visibility in small windows.
- Improved transcript tab and sessions tab background consistency.
- Improved settings layout for transcript section controls.
- Improved GPU check placement inside the transcription settings area.
- Improved transcript readability by grouping Whisper segments into larger sections.
- Updated default window sizing to better fit compact layouts.

### Fixed

- Fixed accidental settings changes caused by mouse wheel scrolling.
- Fixed export button hover icon behavior.
- Fixed transcript tab black background.
- Fixed sessions tab black background.
- Fixed horizontal scrollbar caused by fixed-width session content.
- Fixed cropped plus / minus buttons in settings.
- Fixed player button showing both emoji/text and SVG icon.
- Fixed rename action forcing the transcript tab to open.
- Fixed system-audio echo workflow by allowing microphone disable mode.

### Notes

- AI summarization is not included by default.
- Automatic titles use YAKE, not a heavy local LLM.
- Smart transcript sections use timestamps, pauses, block duration, word count, and simple transition markers.
- Speaker diarization is not included because Whisper alone cannot reliably identify speakers.
