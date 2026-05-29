# Changelog

## v1.0.11

### Features

- Audio file import from the recording page.
- Drag and drop audio import.
- Built-in audio player in the transcript tab.
- Clickable audio timeline with direct seek support.
- TXT transcript export.
- Session search.
- Automatic session title generation.
- Timestamped transcript sections.
- Transcript stats with word count and words per minute.
- Configurable transcript formatting settings.
- Optional system-audio-only recording when no microphone is selected.
- English and French interface language setting.
- Windows release workflow with PyInstaller executable build.
- Direct latest Windows download link and README badges.
- Embedded Windows executable icon.

### Fixes

- Fixed session deletion leaving audio files behind.
- Fixed deletion when the audio player still had the file loaded.
- Fixed temporary audio files left after failed transcription.
- Fixed temporary audio files left when quitting during recording.
- Fixed duplicate transcript storage in `history.json`.
- Fixed direct click seeking on the audio timeline.
- Fixed accidental settings changes caused by mouse wheel scrolling.
- Fixed session row sizing and unwanted horizontal scrolling.
- Fixed cropped plus/minus buttons in settings.
- Fixed player button icon display.
