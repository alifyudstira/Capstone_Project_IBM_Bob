# ui/List.py
# Main preset list page — the home screen of App Preset.
# Shows all saved presets as cards with Launch / Edit / Delete actions.

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QSizePolicy, QMessageBox, QSpacerItem,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from models.preset import Preset
from styles.theme import (
    HEADER_LABEL_STYLE, MUTED_LABEL_STYLE,
    COLOR_SURFACE, COLOR_BORDER, COLOR_PRIMARY, COLOR_DANGER, COLOR_DANGER_HOV,
    COLOR_TEXT, COLOR_MUTED, COLOR_BG,
    COLOR_TAG_EXE, COLOR_TAG_EXE_TXT,
    COLOR_TAG_STORE, COLOR_TAG_STORE_TXT,
    COLOR_TAG_WEB, COLOR_TAG_WEB_TXT,
    FONT_SIZE_BASE, FONT_SIZE_SMALL,
    tag_badge_style, style_btn_primary, style_btn_secondary, style_btn_danger,
)


# ── Tag badge helper ──────────────────────────────────────────────────────────
_TAG_COLORS = {
    "exe":     (COLOR_TAG_EXE,   COLOR_TAG_EXE_TXT),
    "store":   (COLOR_TAG_STORE, COLOR_TAG_STORE_TXT),
    "browser": (COLOR_TAG_WEB,   COLOR_TAG_WEB_TXT),
}
_TAG_LABELS = {
    "exe":     "EXE",
    "store":   "Store",
    "browser": "Web",
}


# ── Individual Preset Card ────────────────────────────────────────────────────
class PresetCard(QFrame):
    """
    A card widget that displays a single Preset with its app entries.
    Emits signals when the user clicks Launch, Edit, or Delete.
    """

    launch_requested = pyqtSignal(str)   # preset_id
    edit_requested   = pyqtSignal(str)   # preset_id
    delete_requested = pyqtSignal(str)   # preset_id

    def __init__(self, preset: Preset, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._preset = preset
        self._build_ui()

    def _build_ui(self) -> None:
        self.setObjectName("PresetCard")
        # Use an ID selector (#PresetCard) so the rule is scoped to this frame only
        # and does NOT cascade into child QPushButton widgets.
        self.setStyleSheet(f"""
            QFrame#PresetCard {{
                background-color: {COLOR_BG};
                border: 1.5px solid {COLOR_BORDER};
                border-radius: 12px;
            }}
            QFrame#PresetCard:hover {{
                border-color: {COLOR_PRIMARY};
            }}
        """)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(18, 16, 18, 14)
        outer.setSpacing(10)

        # ── Top row: icon + name + action buttons ─────────────────────────────
        top_row = QHBoxLayout()
        top_row.setSpacing(10)

        # Icon + Name
        icon_lbl = QLabel(self._preset.icon)
        icon_lbl.setStyleSheet("font-size: 26px; background: transparent;")
        top_row.addWidget(icon_lbl)

        name_lbl = QLabel(self._preset.name)
        name_lbl.setStyleSheet(
            f"font-size: 16px; font-weight: 700; color: {COLOR_TEXT}; background: transparent;"
        )
        top_row.addWidget(name_lbl)
        top_row.addStretch()

        # Action buttons — always call a style helper so the style is applied
        # directly on the button instance, independent of parent stylesheet scope.
        launch_btn = QPushButton("▶  Jalankan")
        style_btn_primary(launch_btn)
        launch_btn.setToolTip("Buka semua aplikasi dalam preset ini")
        launch_btn.clicked.connect(lambda: self.launch_requested.emit(self._preset.preset_id))

        edit_btn = QPushButton("Edit")
        style_btn_secondary(edit_btn)
        edit_btn.setToolTip("Edit preset")
        edit_btn.clicked.connect(lambda: self.edit_requested.emit(self._preset.preset_id))

        delete_btn = QPushButton("Hapus")
        style_btn_danger(delete_btn)
        delete_btn.setToolTip("Hapus preset")
        delete_btn.clicked.connect(lambda: self.delete_requested.emit(self._preset.preset_id))

        top_row.addWidget(launch_btn)
        top_row.addWidget(edit_btn)
        top_row.addWidget(delete_btn)
        outer.addLayout(top_row)

        # ── Entry count info ──────────────────────────────────────────────────
        count = self._preset.entry_count()
        count_lbl = QLabel(f"{count} aplikasi / URL")
        count_lbl.setStyleSheet(MUTED_LABEL_STYLE + " background: transparent;")
        outer.addWidget(count_lbl)

        # ── Entry tags ────────────────────────────────────────────────────────
        tags_row = QHBoxLayout()
        tags_row.setSpacing(6)

        for entry in self._preset.entries:
            # App type badge
            bg, fg = _TAG_COLORS.get(entry.app_type, ("#E5E7EB", "#374151"))
            type_lbl = QLabel(_TAG_LABELS.get(entry.app_type, entry.app_type))
            type_lbl.setStyleSheet(tag_badge_style(bg, fg))

            # Name
            name_lbl = QLabel(entry.name)
            name_lbl.setStyleSheet(
                f"background: transparent; color: {COLOR_TEXT}; "
                f"font-size: {FONT_SIZE_SMALL}px;"
            )

            tags_row.addWidget(type_lbl)
            tags_row.addWidget(name_lbl)
            # Separator dot (except after last entry)
            if entry is not self._preset.entries[-1]:
                sep = QLabel("·")
                sep.setStyleSheet(f"background: transparent; color: {COLOR_MUTED}; "
                                  f"font-size: {FONT_SIZE_SMALL}px;")
                tags_row.addWidget(sep)

        tags_row.addStretch()
        outer.addLayout(tags_row)

    def update_preset(self, preset: Preset) -> None:
        """Replace displayed data with an updated preset (rebuild UI)."""
        self._preset = preset
        # Rebuild by clearing and re-running _build_ui
        for i in reversed(range(self.layout().count())):
            item = self.layout().itemAt(i)
            if item.widget():
                item.widget().deleteLater()
        self._build_ui()


# ── Empty state widget ────────────────────────────────────────────────────────
class EmptyState(QWidget):
    """Shown when there are no presets yet."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(12)

        icon = QLabel("📂")
        icon.setStyleSheet("font-size: 52px; background: transparent;")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("Belum ada preset")
        title.setStyleSheet(
            f"font-size: 18px; font-weight: 600; color: {COLOR_TEXT}; background: transparent;"
        )
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        desc = QLabel("Klik <b>+ Preset Baru</b> di pojok kanan atas untuk membuat preset pertamamu.")
        desc.setWordWrap(True)
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setStyleSheet(f"color: {COLOR_MUTED}; font-size: {FONT_SIZE_BASE}px; background: transparent;")

        layout.addStretch()
        layout.addWidget(icon)
        layout.addWidget(title)
        layout.addWidget(desc)
        layout.addStretch()


# ── Main PresetListPage widget ────────────────────────────────────────────────
class PresetListPage(QWidget):
    """
    The home page of App Preset.
    Displays all presets and delegates CRUD actions to the MainWindow via signals.
    """

    # Signals forwarded upward to MainWindow
    add_requested    = pyqtSignal()
    edit_requested   = pyqtSignal(str)   # preset_id
    delete_requested = pyqtSignal(str)   # preset_id
    launch_requested = pyqtSignal(str)   # preset_id

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._cards: dict[str, PresetCard] = {}  # preset_id → card widget
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Page header ───────────────────────────────────────────────────────
        header = QWidget()
        header.setObjectName("ListPageHeader")
        # Use object-name selector so background only applies to this widget,
        # not to QPushButton children (which are also QWidgets).
        header.setStyleSheet(f"QWidget#ListPageHeader {{ background-color: {COLOR_SURFACE}; "
                             f"border-bottom: 1.5px solid {COLOR_BORDER}; }}")
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(28, 20, 28, 16)
        h_layout.setSpacing(12)

        title_col = QVBoxLayout()
        title_col.setSpacing(2)
        title_lbl = QLabel("🗂️  App Preset")
        title_lbl.setStyleSheet(HEADER_LABEL_STYLE + " background: transparent;")
        subtitle_lbl = QLabel("Kelola dan jalankan kumpulan aplikasi sesuai aktivitasmu.")
        subtitle_lbl.setStyleSheet(MUTED_LABEL_STYLE + " background: transparent;")
        title_col.addWidget(title_lbl)
        title_col.addWidget(subtitle_lbl)

        h_layout.addLayout(title_col, stretch=1)

        add_btn = QPushButton("+ Preset Baru")
        style_btn_primary(add_btn)
        add_btn.setFixedHeight(36)
        add_btn.clicked.connect(self.add_requested.emit)
        h_layout.addWidget(add_btn, alignment=Qt.AlignmentFlag.AlignVCenter)

        root.addWidget(header)

        # ── Scrollable cards area ─────────────────────────────────────────────
        self._cards_container = QWidget()
        self._cards_container.setObjectName("CardsContainer")
        self._cards_container.setStyleSheet(f"QWidget#CardsContainer {{ background-color: {COLOR_BG}; }}")
        self._cards_layout = QVBoxLayout(self._cards_container)
        self._cards_layout.setContentsMargins(28, 20, 28, 20)
        self._cards_layout.setSpacing(14)
        self._cards_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self._cards_container)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        root.addWidget(scroll, stretch=1)

        # ── Empty state (shown when no cards) ─────────────────────────────────
        self._empty_state = EmptyState()
        root.addWidget(self._empty_state)

    # ── Public API called by MainWindow ───────────────────────────────────────
    def load_presets(self, presets: list[Preset]) -> None:
        """Replace the entire card list with the given presets."""
        # Clear existing cards
        for card in self._cards.values():
            self._cards_layout.removeWidget(card)
            card.deleteLater()
        self._cards.clear()

        # Build new cards
        for preset in presets:
            self._add_card(preset)

        self._refresh_empty_state()

    def add_card(self, preset: Preset) -> None:
        """Append a new card for the given preset."""
        self._add_card(preset)
        self._refresh_empty_state()

    def update_card(self, preset: Preset) -> None:
        """Refresh the card for the updated preset."""
        if preset.preset_id in self._cards:
            old_card = self._cards[preset.preset_id]
            idx = self._cards_layout.indexOf(old_card)
            self._cards_layout.removeWidget(old_card)
            old_card.deleteLater()

            new_card = self._create_card(preset)
            self._cards_layout.insertWidget(idx, new_card)
            self._cards[preset.preset_id] = new_card

    def remove_card(self, preset_id: str) -> None:
        """Remove the card with the given preset_id."""
        if preset_id in self._cards:
            card = self._cards.pop(preset_id)
            self._cards_layout.removeWidget(card)
            card.deleteLater()
        self._refresh_empty_state()

    # ── Private helpers ───────────────────────────────────────────────────────
    def _create_card(self, preset: Preset) -> PresetCard:
        """Instantiate a PresetCard and wire its signals."""
        card = PresetCard(preset)
        card.launch_requested.connect(self.launch_requested.emit)
        card.edit_requested.connect(self.edit_requested.emit)
        card.delete_requested.connect(self._confirm_delete)
        return card

    def _add_card(self, preset: Preset) -> None:
        card = self._create_card(preset)
        self._cards_layout.addWidget(card)
        self._cards[preset.preset_id] = card

    def _confirm_delete(self, preset_id: str) -> None:
        """Show a confirmation dialog before emitting delete_requested."""
        card = self._cards.get(preset_id)
        name = card._preset.name if card else "preset ini"
        reply = QMessageBox.question(
            self,
            "Hapus Preset",
            f"Yakin ingin menghapus preset <b>{name}</b>?<br>"
            "Tindakan ini tidak dapat dibatalkan.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.delete_requested.emit(preset_id)

    def _refresh_empty_state(self) -> None:
        """Show or hide the empty state based on whether there are cards."""
        has_cards = bool(self._cards)
        self._cards_container.setVisible(has_cards)
        self._empty_state.setVisible(not has_cards)
