# ui/Add.py
# Dialog for creating a new preset with multiple app entries.
# Users can add as many entries as they want before saving.

import sys
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QFrame, QScrollArea, QWidget,
    QFileDialog, QSizePolicy, QMessageBox,
)
from PyQt6.QtCore import Qt

from models.preset import Preset, AppEntry
from styles.theme import (
    GLOBAL_STYLE, HEADER_LABEL_STYLE, SUBHEADER_LABEL_STYLE, MUTED_LABEL_STYLE,
    COLOR_SURFACE, COLOR_BORDER, COLOR_PRIMARY, COLOR_DANGER,
    COLOR_TEXT, COLOR_MUTED, COLOR_BG,
    COLOR_TAG_EXE, COLOR_TAG_EXE_TXT,
    COLOR_TAG_STORE, COLOR_TAG_STORE_TXT,
    COLOR_TAG_WEB, COLOR_TAG_WEB_TXT,
    FONT_SIZE_BASE, FONT_SIZE_SMALL,
    tag_badge_style, style_btn_primary, style_btn_secondary, style_btn_danger,
)


# ── Emoji options for preset icon ─────────────────────────────────────────────
ICON_OPTIONS = ["🗂️", "💻", "🎵", "🎮", "📊", "📝", "🎨", "🌐", "📚", "🔧", "🚀", "💼"]

# ── App type display metadata ─────────────────────────────────────────────────
APP_TYPE_META = {
    "exe":     ("EXE / App",       COLOR_TAG_EXE,   COLOR_TAG_EXE_TXT),
    "store":   ("Store App",       COLOR_TAG_STORE, COLOR_TAG_STORE_TXT),
    "browser": ("Browser / URL",   COLOR_TAG_WEB,   COLOR_TAG_WEB_TXT),
}

APP_TYPE_PLACEHOLDERS = {
    "exe":     "Masukkan path file, misal:  C:\\Program Files\\Code\\Code.exe",
    "store":   "Masukkan URI scheme atau nama app, misal:  spotify:",
    "browser": "Masukkan URL, misal:  https://docs.python.org",
}


# ── Single-entry row widget ───────────────────────────────────────────────────
class EntryRow(QFrame):
    """
    A self-contained row representing one AppEntry in the 'add entries' list.
    Emits no signals — the parent dialog reads .get_entry() when saving.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self) -> None:
        self.setObjectName("EntryRowFrame")
        # ID selector prevents the QFrame rule from cascading into child buttons.
        self.setStyleSheet(f"""
            QFrame#EntryRowFrame {{
                background-color: {COLOR_SURFACE};
                border: 1.5px solid {COLOR_BORDER};
                border-radius: 8px;
            }}
        """)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(14, 12, 14, 12)
        outer.setSpacing(8)

        # ── Row 1: name + type selector + delete ──────────────────────────────
        row1 = QHBoxLayout()
        row1.setSpacing(8)

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Nama aplikasi (misal: VS Code)")
        self.name_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self.type_combo = QComboBox()
        for key, (label, _, _) in APP_TYPE_META.items():
            self.type_combo.addItem(label, userData=key)
        self.type_combo.setFixedWidth(160)
        self.type_combo.currentIndexChanged.connect(self._on_type_changed)

        self.delete_btn = QPushButton("Hapus")
        style_btn_danger(self.delete_btn)
        self.delete_btn.setToolTip("Hapus entri ini")

        row1.addWidget(self.name_edit)
        row1.addWidget(self.type_combo)
        row1.addWidget(self.delete_btn)
        outer.addLayout(row1)

        # ── Row 2: target path / URL + browse button ──────────────────────────
        row2 = QHBoxLayout()
        row2.setSpacing(8)

        self.target_edit = QLineEdit()
        self.target_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self.browse_btn = QPushButton("Browse…")
        style_btn_secondary(self.browse_btn)
        self.browse_btn.setFixedWidth(90)
        self.browse_btn.clicked.connect(self._browse_file)

        row2.addWidget(self.target_edit)
        row2.addWidget(self.browse_btn)
        outer.addLayout(row2)

        # Set initial placeholder
        self._on_type_changed()

    # ── Slots ─────────────────────────────────────────────────────────────────
    def _on_type_changed(self) -> None:
        """Update placeholder text and browse button visibility when type changes."""
        key = self.type_combo.currentData()
        self.target_edit.setPlaceholderText(APP_TYPE_PLACEHOLDERS.get(key, ""))
        # Browse button only makes sense for exe/app files
        self.browse_btn.setVisible(key == "exe")

    def _browse_file(self) -> None:
        """Open a file picker and populate the target field."""
        if sys.platform == "darwin":
            # On macOS: allow selecting .app bundles (which are directories)
            path = QFileDialog.getExistingDirectory(
                self, "Pilih Aplikasi (.app)",
                "/Applications",
            )
        else:
            path, _ = QFileDialog.getOpenFileName(
                self, "Pilih File Executable",
                "", "Executable (*.exe);;All Files (*.*)",
            )
        if path:
            self.target_edit.setText(path)

    # ── Data accessor ─────────────────────────────────────────────────────────
    def get_entry(self) -> AppEntry | None:
        """
        Build and return an AppEntry from current input values.
        Returns None if required fields are empty.
        """
        name   = self.name_edit.text().strip()
        target = self.target_edit.text().strip()
        key    = self.type_combo.currentData()
        if not name or not target:
            return None
        return AppEntry(name=name, app_type=key, target=target)

    def populate(self, entry: AppEntry) -> None:
        """Fill the row fields from an existing AppEntry (used when editing)."""
        self.name_edit.setText(entry.name)
        self.target_edit.setText(entry.target)
        # Set the combo box to match app_type
        for i in range(self.type_combo.count()):
            if self.type_combo.itemData(i) == entry.app_type:
                self.type_combo.setCurrentIndex(i)
                break


# ── Add Preset dialog ─────────────────────────────────────────────────────────
class AddPresetDialog(QDialog):
    """
    Modal dialog for creating a brand-new preset.
    On accept, the created Preset is available via .result_preset.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.result_preset: Preset | None = None
        self._entry_rows: list[EntryRow] = []
        self._build_ui()
        self._add_entry_row()  # start with one empty row

    def _build_ui(self) -> None:
        self.setWindowTitle("Buat Preset Baru")
        self.setMinimumWidth(620)
        self.setMinimumHeight(480)
        self.resize(660, 560)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Dialog header ─────────────────────────────────────────────────────
        header = QWidget()
        header.setObjectName("AddDialogHeader")
        header.setStyleSheet(f"QWidget#AddDialogHeader {{ background-color: {COLOR_SURFACE}; "
                             f"border-bottom: 1.5px solid {COLOR_BORDER}; }}")
        h_layout = QVBoxLayout(header)
        h_layout.setContentsMargins(24, 18, 24, 14)
        h_layout.setSpacing(2)

        title = QLabel("✨  Buat Preset Baru")
        title.setStyleSheet(HEADER_LABEL_STYLE + " background: transparent;")
        subtitle = QLabel("Isi nama preset lalu tambahkan aplikasi yang ingin dibuka sekaligus.")
        subtitle.setStyleSheet(MUTED_LABEL_STYLE + " background: transparent;")

        h_layout.addWidget(title)
        h_layout.addWidget(subtitle)
        root.addWidget(header)

        # ── Preset meta section ───────────────────────────────────────────────
        meta_widget = QWidget()
        meta_widget.setObjectName("AddDialogMeta")
        meta_widget.setStyleSheet(f"QWidget#AddDialogMeta {{ background-color: {COLOR_BG}; }}")
        meta_layout = QHBoxLayout(meta_widget)
        meta_layout.setContentsMargins(24, 16, 24, 8)
        meta_layout.setSpacing(12)

        # Icon picker
        icon_col = QVBoxLayout()
        icon_col.setSpacing(4)
        icon_col.addWidget(QLabel("Ikon"))
        self.icon_combo = QComboBox()
        self.icon_combo.setFixedWidth(80)
        for emoji in ICON_OPTIONS:
            self.icon_combo.addItem(emoji)
        icon_col.addWidget(self.icon_combo)
        meta_layout.addLayout(icon_col)

        # Name field
        name_col = QVBoxLayout()
        name_col.setSpacing(4)
        name_col.addWidget(QLabel("Nama Preset  *"))
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("misal: Programming, Gaming, Design…")
        self.name_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        name_col.addWidget(self.name_edit)
        meta_layout.addLayout(name_col)

        root.addWidget(meta_widget)

        # ── Entries list section ──────────────────────────────────────────────
        entries_header = QWidget()
        entries_header.setObjectName("AddDialogEntriesHeader")
        entries_header.setStyleSheet(f"QWidget#AddDialogEntriesHeader {{ background-color: {COLOR_BG}; }}")
        e_layout = QHBoxLayout(entries_header)
        e_layout.setContentsMargins(24, 4, 24, 4)

        entries_label = QLabel("Aplikasi dalam Preset  *")
        entries_label.setStyleSheet(f"font-weight: 600; color: {COLOR_TEXT};")
        e_layout.addWidget(entries_label)
        e_layout.addStretch()

        add_entry_btn = QPushButton("+ Tambah Aplikasi")
        style_btn_secondary(add_entry_btn)
        add_entry_btn.clicked.connect(self._add_entry_row)
        e_layout.addWidget(add_entry_btn)

        root.addWidget(entries_header)

        # Scroll area for entry rows
        self.entries_container = QWidget()
        self.entries_container.setObjectName("AddDialogEntriesContainer")
        self.entries_container.setStyleSheet(f"QWidget#AddDialogEntriesContainer {{ background-color: {COLOR_BG}; }}")
        self.entries_layout = QVBoxLayout(self.entries_container)
        self.entries_layout.setContentsMargins(24, 8, 24, 8)
        self.entries_layout.setSpacing(10)
        self.entries_layout.addStretch()  # keeps rows top-aligned

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.entries_container)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setMinimumHeight(200)
        root.addWidget(scroll, stretch=1)

        # ── Action buttons ────────────────────────────────────────────────────
        footer = QWidget()
        footer.setObjectName("AddDialogFooter")
        footer.setStyleSheet(f"QWidget#AddDialogFooter {{ background-color: {COLOR_SURFACE}; "
                             f"border-top: 1.5px solid {COLOR_BORDER}; }}")
        f_layout = QHBoxLayout(footer)
        f_layout.setContentsMargins(24, 12, 24, 12)
        f_layout.setSpacing(10)
        f_layout.addStretch()

        cancel_btn = QPushButton("Batal")
        style_btn_secondary(cancel_btn)
        cancel_btn.clicked.connect(self.reject)

        save_btn = QPushButton("💾  Simpan Preset")
        style_btn_primary(save_btn)
        save_btn.clicked.connect(self._on_save)

        f_layout.addWidget(cancel_btn)
        f_layout.addWidget(save_btn)
        root.addWidget(footer)

    # ── Entry management ──────────────────────────────────────────────────────
    def _add_entry_row(self, entry: AppEntry | None = None) -> None:
        """Append a new EntryRow (optionally pre-filled) to the entries list."""
        row = EntryRow()
        if entry:
            row.populate(entry)
        # Wire the row's delete button before inserting
        row.delete_btn.clicked.connect(lambda: self._remove_entry_row(row))
        # Insert before the trailing stretch (last item)
        insert_pos = self.entries_layout.count() - 1
        self.entries_layout.insertWidget(insert_pos, row)
        self._entry_rows.append(row)

    def _remove_entry_row(self, row: EntryRow) -> None:
        """Remove an EntryRow from the layout and tracking list."""
        if row in self._entry_rows:
            self._entry_rows.remove(row)
        self.entries_layout.removeWidget(row)
        row.deleteLater()

    # ── Save logic ────────────────────────────────────────────────────────────
    def _on_save(self) -> None:
        """Validate inputs, build a Preset, and accept the dialog."""
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Validasi", "Nama preset tidak boleh kosong.")
            self.name_edit.setFocus()
            return

        entries = []
        for row in self._entry_rows:
            entry = row.get_entry()
            if entry:
                entries.append(entry)

        if not entries:
            QMessageBox.warning(
                self, "Validasi",
                "Tambahkan minimal satu aplikasi ke dalam preset.",
            )
            return

        icon = self.icon_combo.currentText()
        self.result_preset = Preset(name=name, icon=icon, entries=entries)
        self.accept()
