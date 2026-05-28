import os
import sys
from pathlib import Path

from src.resources import app_root
from src.services.transcript_formatter import SmartTranscriptFormatter


class ProgressTqdm:
    def __init__(self, *args, progress_callback=None, **kwargs):
        self.total = float(kwargs.get("total") or 0)
        self.n = 0.0
        self.progress_callback = progress_callback
        self.disabled = kwargs.get("disable", False)

    def update(self, value=1):
        self.n += float(value or 0)
        if self.progress_callback and self.total > 0 and not self.disabled:
            percent = int(max(0, min(99, (self.n / self.total) * 100)))
            self.progress_callback(percent)

    def close(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        self.close()


class RuntimeStatus:
    def __init__(self, gpu_detected=False, cuda_ready=False, backend="CPU", message="", model="", compute_type=""):
        self.gpu_detected = gpu_detected
        self.cuda_ready = cuda_ready
        self.backend = backend
        self.message = message
        self.model = model
        self.compute_type = compute_type


class TranscriptionResult:
    def __init__(self, text, language="auto"):
        self.text = text
        self.language = language


class GpuRequiredError(RuntimeError):
    pass


def installed_cuda_bins():
    if sys.platform != "win32":
        return []
    root = Path(os.environ.get("ProgramFiles", "C:\\Program Files")) / "NVIDIA GPU Computing Toolkit" / "CUDA"
    if not root.exists():
        return []
    return [path / "bin" for path in sorted(root.glob("v12.*"), reverse=True)]


def installed_cudnn_bins():
    if sys.platform != "win32":
        return []
    root = Path(os.environ.get("ProgramFiles", "C:\\Program Files")) / "NVIDIA" / "CUDNN"
    if not root.exists():
        return []
    bins = []
    for version in sorted(root.glob("v9*"), reverse=True):
        bins.extend(path for path in version.rglob("*") if path.is_dir() and any(path.glob("cudnn*_9.dll")))
    return bins


class MockTranscriptionProvider:
    def transcribe(self, audio_path: Path, progress_callback=None):
        name = Path(audio_path).name
        text = (
            "[00:00] Transcript de demonstration.\n\n"
            f"[00:05] Audio source: {name}\n\n"
            "[00:10] Whisper local est pret a etre branche avec faster-whisper. "
            "La detection automatique utilisera language=None."
        )
        if progress_callback:
            progress_callback(100)
        return TranscriptionResult(text=text, language="mock")


class FasterWhisperProvider:
    def __init__(self, settings=None, model_name=None):
        settings = settings or {}
        self.configure_dll_paths()
        from faster_whisper import WhisperModel
        self.model_name = model_name or settings.get("model") or os.getenv("MEET_TRANSCRIPT_MODEL", "medium")
        self.device = settings.get("device") or os.getenv("MEET_TRANSCRIPT_DEVICE", "cuda")
        self.compute_type = settings.get("compute_type") or os.getenv("MEET_TRANSCRIPT_COMPUTE_TYPE", "int8_float16")
        self.require_gpu = bool(settings.get("require_gpu", os.getenv("MEET_TRANSCRIPT_REQUIRE_GPU", "1") == "1"))
        self.progress_chunk_seconds = int(settings.get("progress_chunk_seconds", 5) or 5)
        self.formatter = SmartTranscriptFormatter.from_settings(settings)
        self.WhisperModel = WhisperModel
        if self.require_gpu and self.device != "cuda":
            raise GpuRequiredError("GPU required: MEET_TRANSCRIPT_DEVICE must be cuda.")
        try:
            self.model = self.WhisperModel(self.model_name, device=self.device, compute_type=self.compute_type)
        except Exception as exc:
            if self.require_gpu:
                raise GpuRequiredError(self.gpu_error_message(exc)) from exc
            self.load_cpu_model()

    def configure_dll_paths(self):
        if sys.platform != "win32":
            return
        root = app_root()
        candidates = [root / "gpu-libs"]
        cuda_path = os.getenv("CUDA_PATH")
        if cuda_path:
            candidates.append(Path(cuda_path) / "bin")
        candidates.extend(installed_cuda_bins())
        candidates.extend(installed_cudnn_bins())
        for candidate in candidates:
            if candidate and candidate.exists():
                os.environ["PATH"] = f"{candidate}{os.pathsep}{os.environ.get('PATH', '')}"
                os.add_dll_directory(str(candidate))

    def gpu_error_message(self, exc):
        return (
            "GPU transcription is required, but CUDA could not load.\n\n"
            f"Original error: {exc}\n\n"
            "Install CUDA 12 runtime libraries with cuBLAS and cuDNN 9, then make sure the folder containing "
            "cublas64_12.dll and cudnn_ops64_9.dll is in PATH.\n\n"
            "Local option: create a gpu-libs folder at the project root and put the NVIDIA DLLs there. "
            "The app will load that folder automatically."
        )

    def load_cpu_model(self):
        self.device = "cpu"
        self.compute_type = "int8"
        self.model = self.WhisperModel(self.model_name, device=self.device, compute_type=self.compute_type)

    def transcribe(self, audio_path: Path, progress_callback=None):
        try:
            segments, info = self.model.transcribe(str(audio_path), language=None, vad_filter=True, log_progress=bool(progress_callback), chunk_length=self.chunk_length(progress_callback))
        except Exception:
            if self.device != "cpu" and not self.require_gpu:
                self.load_cpu_model()
                segments, info = self.model.transcribe(str(audio_path), language=None, vad_filter=True, log_progress=bool(progress_callback), chunk_length=self.chunk_length(progress_callback))
            else:
                raise
        collected_segments = self.consume_segments(segments, progress_callback)
        if progress_callback:
            progress_callback(100)
        text = self.formatter.format(collected_segments)
        return TranscriptionResult(text=text, language=info.language or "auto")

    def consume_segments(self, segments, progress_callback):
        collected = []
        if not progress_callback:
            for segment in segments:
                collected.append(segment)
            return collected
        import faster_whisper.transcribe as transcribe_module

        original_tqdm = transcribe_module.tqdm

        def factory(*args, **kwargs):
            return ProgressTqdm(*args, progress_callback=progress_callback, **kwargs)

        transcribe_module.tqdm = factory
        try:
            for segment in segments:
                collected.append(segment)
        finally:
            transcribe_module.tqdm = original_tqdm
        return collected

    def chunk_length(self, progress_callback):
        if progress_callback:
            return max(5, min(30, self.progress_chunk_seconds))
        return None


class TranscriptionService:
    def __init__(self):
        self.provider = None
        self.settings = {}
        self.last_status = self.runtime_status()

    def configure(self, settings):
        self.settings = settings or {}
        self.provider = None
        self.last_status = self.runtime_status()

    def create_provider(self):
        provider = os.getenv("MEET_TRANSCRIPT_PROVIDER", "whisper").lower()
        if provider == "whisper":
            try:
                return FasterWhisperProvider(self.settings)
            except GpuRequiredError:
                raise
            except Exception:
                if os.getenv("MEET_TRANSCRIPT_REQUIRE_GPU", "1") == "1":
                    raise
                return MockTranscriptionProvider()
        return MockTranscriptionProvider()

    def transcribe(self, audio_path: Path, progress_callback=None):
        self.last_status = self.runtime_status()
        if self.provider is None:
            self.provider = self.create_provider()
        return self.provider.transcribe(audio_path, progress_callback)

    def runtime_status(self):
        provider = os.getenv("MEET_TRANSCRIPT_PROVIDER", "whisper").lower()
        model = self.settings.get("model") or os.getenv("MEET_TRANSCRIPT_MODEL", "medium")
        device = self.settings.get("device") or os.getenv("MEET_TRANSCRIPT_DEVICE", "cuda")
        compute_type = self.settings.get("compute_type") or os.getenv("MEET_TRANSCRIPT_COMPUTE_TYPE", "int8_float16")
        require_gpu = bool(self.settings.get("require_gpu", os.getenv("MEET_TRANSCRIPT_REQUIRE_GPU", "1") == "1"))
        if provider != "whisper":
            return RuntimeStatus(False, False, "Mock", "Provider mock actif.", model, compute_type)
        gpu_count = self.cuda_device_count()
        gpu_detected = gpu_count > 0
        missing = self.missing_gpu_dlls()
        cuda_ready = gpu_detected and not missing
        if device == "cuda" and cuda_ready:
            return RuntimeStatus(True, True, "GPU", f"GPU pret. Whisper utilisera CUDA avec {model}.", model, compute_type)
        if require_gpu:
            if not gpu_detected:
                return RuntimeStatus(False, False, "GPU bloque", "Aucun GPU CUDA detecte. Transcription GPU impossible.", model, compute_type)
            return RuntimeStatus(True, False, "GPU bloque", f"GPU detecte, mais DLL manquantes: {', '.join(missing)}.", model, compute_type)
        if gpu_detected and missing:
            return RuntimeStatus(True, False, "CPU", f"GPU detecte, CUDA incomplet. Fallback CPU prevu. DLL manquantes: {', '.join(missing)}.", model, "int8")
        return RuntimeStatus(gpu_detected, False, "CPU", "Fallback CPU prevu.", model, "int8")

    def cuda_device_count(self):
        try:
            import ctranslate2

            return ctranslate2.get_cuda_device_count()
        except Exception:
            return 0

    def missing_gpu_dlls(self):
        if sys.platform != "win32":
            return []
        required = ["cublas64_12.dll", "cudnn_ops64_9.dll"]
        paths = self.gpu_library_paths()
        return [name for name in required if not any((path / name).exists() for path in paths)]

    def gpu_library_paths(self):
        paths = []
        root = app_root()
        paths.append(root / "gpu-libs")
        cuda_path = os.getenv("CUDA_PATH")
        if cuda_path:
            paths.append(Path(cuda_path) / "bin")
        paths.extend(installed_cuda_bins())
        paths.extend(installed_cudnn_bins())
        paths.extend(Path(path) for path in os.getenv("PATH", "").split(os.pathsep) if path)
        return paths
