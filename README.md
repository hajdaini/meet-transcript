# Meet Transcript

[![Latest Release](https://img.shields.io/github/v/release/hajdaini/meet-transcript?label=latest%20release)](https://github.com/hajdaini/meet-transcript/releases/latest)
[![Windows Download](https://img.shields.io/badge/download-Windows%20latest-14b8a6)](https://github.com/hajdaini/meet-transcript/releases/latest/download/MeetTranscript-Windows-latest.zip)
[![Release Workflow](https://github.com/hajdaini/meet-transcript/actions/workflows/release.yml/badge.svg)](https://github.com/hajdaini/meet-transcript/actions/workflows/release.yml)
![Python](https://img.shields.io/badge/python-3.11-blue)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)

Meet Transcript is a Windows desktop app built with Python and PySide6. It records microphone audio and Windows system audio, then generates local meeting transcripts with faster-whisper.

![Meet Transcript screenshot](docs/app-screenshot.png)

## Current Features

- Modern dark PySide6 interface
- Microphone and Windows system audio recording
- WASAPI loopback capture for meeting audio
- Start/Stop recording workflow
- Live waveform based on microphone and system audio levels
- Local faster-whisper transcription
- GPU or CPU transcription mode
- GPU readiness check from the app
- Whisper model selection: `small`, `medium`, `large-v3`
- Automatic Whisper language detection
- Interface language setting: English or French
- Real transcription progress from faster-whisper internal progress
- Recent sessions list with compact metadata
- Default session names: `Session 1`, `Session 2`, `Session 3`
- Session actions: play audio, rename, delete
- Transcript preview with copy action
- Automatic settings save
- Configurable output folder
- Microphone gain calibration, default `1.8x`

## Run The App

You can run Meet Transcript in two ways:

- from source with the local Python environment
- from the Windows release executable

## From Source

Create the local virtual environment:

```powershell
python -m venv .venv
```

Install dependencies inside the project environment:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Run the app:

```powershell
.\run.ps1
```

`run.ps1` prepares CUDA/cuDNN DLL paths and starts the app. Model, device, interface language, microphone, gain, and output settings are managed directly inside the UI.

## From Windows Release

The repository includes a GitHub Actions workflow at `.github/workflows/release.yml`.

Download the latest Windows executable:

[Download Meet Transcript for Windows](https://github.com/hajdaini/meet-transcript/releases/latest/download/MeetTranscript-Windows-latest.zip)

Create and push a version tag to publish a GitHub release:

```powershell
git tag v1.0.0
git push origin v1.0.0
```

The workflow builds the Windows app with PyInstaller and uploads:

```text
MeetTranscript-Windows-v1.0.0.zip
MeetTranscript-Windows-latest.zip
```

Inside the archive, launch:

```text
MeetTranscript.exe
```

The release is published automatically on GitHub with generated release notes.

## Default Settings

```text
model: medium
device: GPU
compute type: int8_float16
interface language: English
transcription language detection: Auto
microphone: Auto
microphone gain: 1.8x
system output: Auto
output directory: transcripts/
```

Settings are saved automatically in `settings.json`.

## GPU Setup

GPU transcription uses `faster-whisper` through CTranslate2. On Windows, the app expects:

- NVIDIA driver
- CUDA Toolkit 12.x
- cuDNN 9 for CUDA 12

Recommended installed paths:

```text
C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.8
C:\Program Files\NVIDIA\CUDNN\v9.22
```

Download pages:

- CUDA Toolkit archive: https://developer.nvidia.com/cuda-toolkit-archive
- cuDNN downloads: https://developer.nvidia.com/cudnn-downloads

The app scans these locations:

```text
gpu-libs/
C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.*\bin
C:\Program Files\NVIDIA\CUDNN\v9*\**\cudnn*_9.dll
```

Expected DLLs include:

```text
cublas64_12.dll
cudnn_ops64_9.dll
```

Use `Settings > Verify GPU` to check the runtime. The app shows a green popup when GPU is ready, or a red popup with the missing dependency.

## Storage

Generated files are stored under the selected output folder:

```text
transcripts/
  audio/
    Session audio files as .wav
  text/
    Transcript files as .txt
  history.json
```

The app stores session metadata in `history.json`. Deleting a session from the app also removes its audio and transcript files.

## Runtime Notes

- The first Whisper run downloads the selected model to the Hugging Face cache.
- The Hugging Face symlink warning on Windows is not blocking; it only means the cache may use more disk space.
- `medium` is the default model for speed and accuracy balance.
- `large-v3` is available for better accuracy.
- GPU mode uses `int8_float16` by default.
- CPU mode uses `int8`.
- Whisper language detection is always automatic.
- The app interface can be switched between English and French.
- The progress bar updates from faster-whisper internal progress.
