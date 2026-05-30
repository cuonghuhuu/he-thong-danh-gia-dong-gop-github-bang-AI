import sys
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]


def resource_path(relative_path):
    """Return a bundled resource path for source mode and PyInstaller exe mode."""
    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / relative_path
    return PROJECT_DIR / relative_path


def app_base_dir():
    """Return the writable runtime directory for source mode or the exe folder."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return PROJECT_DIR


def ensure_reports_dir(base_dir=None):
    reports_dir = Path(base_dir or app_base_dir()) / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    return reports_dir
