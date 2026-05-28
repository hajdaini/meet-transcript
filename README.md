# Meet Transcript

Meet Transcript is a Windows desktop app built with Python and PySide6. It records microphone audio and Windows system audio, then generates meeting transcripts with faster-whisper.

## Features

- Dark PySide6 desktop UI
- Start/Stop recording
- Microphone detection and selection
- Windows system audio capture with WASAPI loopback
- Recent sessions list
- Transcript preview
- Copy transcript button
- Rename and delete sessions
- Automatic settings save
- CPU/GPU selection from the app
- GPU status check with green/red popup
- Transcription progress bar
- Whisper model selection
- Whisper language selection with Auto mode
- Output folder selection


## Setup

Create the local virtual environment:

```powershell
python -m venv .venv
```

Install dependencies inside the local environment:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Run the app:

```powershell
.\run.ps1
```

`run.ps1` only prepares CUDA/cuDNN DLL paths and starts the app. Model, CPU/GPU, language, microphone, and output settings are managed inside the UI.

## Default Settings

```text
model: medium
device: GPU
compute type: int8_float16
languages: Auto
output directory: transcripts/
```

The settings are saved automatically when changed in the app.

## GPU Requirements

GPU transcription uses `faster-whisper`, which uses CTranslate2. On Windows, the current GPU setup needs:

- NVIDIA driver
- CUDA Toolkit 12.x
- cuDNN 9 for CUDA 12

Recommended paths:

```text
C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.8
C:\Program Files\NVIDIA\CUDNN\v9.22
```

Download pages:

- CUDA Toolkit archive: https://developer.nvidia.com/cuda-toolkit-archive
- cuDNN downloads: https://developer.nvidia.com/cudnn-downloads

The app scans:

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

If GPU is selected, the Settings screen has a `Verifier GPU` button. It shows a green popup when GPU is ready and a red popup with the missing dependency when it is not ready.

## Runtime Notes

- The first Whisper run downloads the selected model to the Hugging Face cache.
- The Hugging Face symlink warning on Windows is not blocking; it only means the cache may use more disk space.
- `medium` is the default model for speed and quality balance.
- `large-v3` can be selected for better accuracy.
- CPU mode uses `int8`.
- Language `Auto` lets Whisper detect the spoken language.
- Selecting one language forces Whisper to use that language.
- Selecting multiple languages keeps automatic detection because faster-whisper does not limit detection to a custom language subset.
- The progress bar uses faster-whisper internal progress and updates by 5-second audio chunks.
