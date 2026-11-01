# utils/storage.py
# JSON-based persistence layer for App Preset.
# All presets are saved to a single presets.json file next to the executable.

import json
import os
from pathlib import Path
from typing import List

from models.preset import Preset


# ── Storage file location ─────────────────────────────────────────────────────
# Place the data file in the user's app-data directory so it survives
# reinstallation and does not require admin rights.
def _get_data_path() -> Path:
    """Return the path to the presets.json data file."""
    # Use XDG_DATA_HOME or APPDATA on Windows, ~/Library on macOS, ~/.local on Linux
    if os.name == "nt":  # Windows
        base = Path(os.environ.get("APPDATA", Path.home()))
    else:  # macOS / Linux
        base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))

    app_dir = base / "AppPreset"
    app_dir.mkdir(parents=True, exist_ok=True)
    return app_dir / "presets.json"


DATA_FILE = _get_data_path()


# ── Public API ────────────────────────────────────────────────────────────────
def load_presets() -> List[Preset]:
    """Load all presets from disk.  Returns an empty list if no file exists."""
    if not DATA_FILE.exists():
        return []
    try:
        with DATA_FILE.open("r", encoding="utf-8") as fh:
            raw = json.load(fh)
        return [Preset.from_dict(item) for item in raw]
    except (json.JSONDecodeError, KeyError, TypeError):
        # Corrupted data – start fresh rather than crash.
        return []


def save_presets(presets: List[Preset]) -> None:
    """Serialize and save all presets to disk (atomic write via temp file)."""
    payload = json.dumps(
        [p.to_dict() for p in presets],
        ensure_ascii=False,
        indent=2,
    )
    # Write to a temp file first, then rename – prevents data loss on crash.
    tmp = DATA_FILE.with_suffix(".tmp")
    tmp.write_text(payload, encoding="utf-8")
    tmp.replace(DATA_FILE)


def add_preset(presets: List[Preset], preset: Preset) -> List[Preset]:
    """Append a preset and persist the updated list."""
    presets.append(preset)
    save_presets(presets)
    return presets


def update_preset(presets: List[Preset], updated: Preset) -> List[Preset]:
    """Replace the preset with matching preset_id and persist."""
    for i, p in enumerate(presets):
        if p.preset_id == updated.preset_id:
            presets[i] = updated
            break
    save_presets(presets)
    return presets


def delete_preset(presets: List[Preset], preset_id: str) -> List[Preset]:
    """Remove the preset with the given id and persist."""
    presets = [p for p in presets if p.preset_id != preset_id]
    save_presets(presets)
    return presets
