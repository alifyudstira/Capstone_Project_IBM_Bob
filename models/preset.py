# models/preset.py
# Data models for App Preset.
# A Preset is a named collection of AppEntry items.

from dataclasses import dataclass, field
from typing import Literal
import uuid


# ── App entry types ───────────────────────────────────────────────────────────
AppType = Literal["exe", "store", "browser"]
# exe     → a local executable (.exe on Windows, .app on macOS)
# store   → an app installed from an official store (MS Store / Mac App Store)
#           launched by its URI scheme or "open" command
# browser → opens a URL in the default browser


@dataclass
class AppEntry:
    """
    Represents a single application or URL inside a preset.

    Fields:
        entry_id   – unique identifier (auto-generated)
        name       – display name shown in the UI
        app_type   – one of "exe", "store", or "browser"
        target     – the launch target:
                       exe     → absolute path to the executable
                       store   → URI scheme (e.g. "spotify:")  or app identifier
                       browser → full URL (e.g. "https://docs.python.org")
    """
    name: str
    app_type: AppType
    target: str
    entry_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    # ── Serialization ─────────────────────────────────────────────────────────
    def to_dict(self) -> dict:
        return {
            "entry_id": self.entry_id,
            "name":     self.name,
            "app_type": self.app_type,
            "target":   self.target,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AppEntry":
        return cls(
            entry_id = data.get("entry_id", str(uuid.uuid4())),
            name     = data["name"],
            app_type = data["app_type"],
            target   = data["target"],
        )


@dataclass
class Preset:
    """
    A named preset that groups multiple AppEntry items.

    Fields:
        preset_id – unique identifier (auto-generated)
        name      – display name (e.g. "Programming")
        icon      – optional single emoji used as icon in the list
        entries   – ordered list of AppEntry objects
    """
    name: str
    icon: str = "🗂️"
    entries: list = field(default_factory=list)
    preset_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    # ── Convenience ───────────────────────────────────────────────────────────
    def entry_count(self) -> int:
        return len(self.entries)

    # ── Serialization ─────────────────────────────────────────────────────────
    def to_dict(self) -> dict:
        return {
            "preset_id": self.preset_id,
            "name":      self.name,
            "icon":      self.icon,
            "entries":   [e.to_dict() for e in self.entries],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Preset":
        entries = [AppEntry.from_dict(e) for e in data.get("entries", [])]
        return cls(
            preset_id = data.get("preset_id", str(uuid.uuid4())),
            name      = data["name"],
            icon      = data.get("icon", "🗂️"),
            entries   = entries,
        )
