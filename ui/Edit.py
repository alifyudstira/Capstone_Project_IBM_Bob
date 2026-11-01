# ui/Edit.py
# Dialog for editing an existing preset.
# Inherits AddPresetDialog and pre-fills all fields from the given Preset.

from PyQt6.QtWidgets import QWidget, QLabel

from models.preset import Preset
from styles.theme import HEADER_LABEL_STYLE, MUTED_LABEL_STYLE, COLOR_SURFACE, COLOR_BORDER
from ui.Add import AddPresetDialog, ICON_OPTIONS


class EditPresetDialog(AddPresetDialog):
    """
    Reuses the AddPresetDialog UI but pre-populates it with an existing Preset.
    After accept(), the updated Preset (preserving the original preset_id) is
    available via .result_preset.
    """

    def __init__(self, preset: Preset, parent: QWidget | None = None) -> None:
        # Call the parent __init__ which builds the UI and adds one blank row.
        super().__init__(parent)
        self._original_preset = preset
        self._populate(preset)

    def _populate(self, preset: Preset) -> None:
        """Fill all dialog fields from the given preset."""
        # ── Update window title & header labels ───────────────────────────────
        self.setWindowTitle(f"Edit Preset – {preset.name}")

        # Swap out the header title and subtitle labels (first two children of h_layout)
        # We use findChildren with objectName approach to keep it simple:
        # The dialog header is the very first widget in the root layout.
        # We re-set the labels directly via setObjectName-aware search.
        title_labels = self.findChildren(QLabel)
        for lbl in title_labels:
            if "Buat Preset Baru" in lbl.text():
                lbl.setText("✏️  Edit Preset")
                lbl.setStyleSheet(HEADER_LABEL_STYLE + " background: transparent;")
                break
        for lbl in title_labels:
            if "Isi nama preset" in lbl.text():
                lbl.setText("Perbarui nama, ikon, atau daftar aplikasi dalam preset.")
                lbl.setStyleSheet(MUTED_LABEL_STYLE + " background: transparent;")
                break

        # ── Preset name & icon ────────────────────────────────────────────────
        self.name_edit.setText(preset.name)

        if preset.icon in ICON_OPTIONS:
            self.icon_combo.setCurrentIndex(ICON_OPTIONS.index(preset.icon))

        # ── Entries ───────────────────────────────────────────────────────────
        # Remove the blank row that __init__ added
        if self._entry_rows:
            blank_row = self._entry_rows[0]
            self._remove_entry_row(blank_row)

        # Add one row per existing entry
        for entry in preset.entries:
            self._add_entry_row(entry)

    # ── Override save to preserve preset_id ──────────────────────────────────
    def _on_save(self) -> None:
        """Save normally, then patch the preset_id to match the original."""
        super()._on_save()
        # If the parent save succeeded, result_preset is set and dialog accepted.
        if self.result_preset is not None:
            self.result_preset.preset_id = self._original_preset.preset_id
