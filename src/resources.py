import sys
from pathlib import Path


def app_root():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


def resource_root():
    if getattr(sys, "frozen", False):
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            return Path(meipass)
        root = app_root()
        internal = root / "_internal"
        if internal.exists():
            return internal
        return root
    return app_root()


def asset_path(name):
    candidates = [
        resource_root() / "assets" / name,
        app_root() / "assets" / name,
        app_root() / "_internal" / "assets" / name,
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]
