# utils/launcher.py
# Cross-platform application launch logic.
# Handles three target types: exe/app paths, store URIs, and browser URLs.

import os
import sys
import subprocess
import webbrowser
from typing import List

from models.preset import AppEntry, Preset


def launch_entry(entry: AppEntry) -> str | None:
    """
    Launch a single AppEntry.
    Returns None on success, or an error message string on failure.
    """
    try:
        if entry.app_type == "browser":
            _open_url(entry.target)

        elif entry.app_type == "exe":
            _open_executable(entry.target)

        elif entry.app_type == "store":
            _open_store_app(entry.target)

        return None  # success

    except Exception as exc:
        return str(exc)


def launch_preset(preset: Preset) -> List[str]:
    """
    Launch all entries in a preset.
    Returns a list of error messages for any entries that failed to start.
    """
    errors = []
    for entry in preset.entries:
        error = launch_entry(entry)
        if error:
            errors.append(f"'{entry.name}': {error}")
    return errors


# ── Private helpers ────────────────────────────────────────────────────────────
def _open_url(url: str) -> None:
    """Open a URL in the system's default browser."""
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    webbrowser.open(url)


def _open_executable(path: str) -> None:
    """Launch a .exe (Windows) or .app / binary (macOS/Linux)."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")

    if sys.platform == "win32":
        os.startfile(path)  # type: ignore[attr-defined]
    elif sys.platform == "darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen([path])


def _open_store_app(identifier: str) -> None:
    """
    Launch an app installed from an official store.

    Windows: Microsoft Store apps expose a URI scheme (e.g. "spotify:").
             We use os.startfile which hands it to the Shell URI handler.
    macOS:   Use 'open -a <AppName>' where identifier is the app bundle name,
             e.g. "Spotify" or "Xcode".
    """
    if sys.platform == "win32":
        # On Windows: identifier is a URI scheme like "spotify:" or "ms-windows-store:"
        os.startfile(identifier)  # type: ignore[attr-defined]
    elif sys.platform == "darwin":
        # On macOS: identifier is the app name as it appears in /Applications
        subprocess.Popen(["open", "-a", identifier])
    else:
        # On Linux (Flatpak / Snap): identifier is the app ID
        subprocess.Popen(["xdg-open", identifier])
