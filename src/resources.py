import sys
from pathlib import Path


def app_root():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


def asset_path(name):
    return app_root() / "assets" / name
