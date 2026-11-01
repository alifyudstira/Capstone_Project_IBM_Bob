# main.py
# Entry point for App Preset.
# Creates the QApplication, builds the MainWindow, and starts the event loop.

import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QHBoxLayout, QVBoxLayout, QLabel, QPushButton,
    QMessageBox, QFrame, QStackedWidget,
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon

from styles.theme import (
    GLOBAL_STYLE, COLOR_SURFACE, COLOR_BORDER, COLOR_PRIMARY,
    COLOR_TEXT, COLOR_MUTED, COLOR_BG, FONT_SIZE_BASE, FONT_SIZE_SMALL,
)
from models.preset import Preset
from utils import storage
from utils.launcher import launch_preset
from ui.List import PresetListPage
from ui.Add import AddPresetDialog
from ui.Edit import EditPresetDialog
from ui.tutorial import TutorialPage


# ── Sidebar navigation button ─────────────────────────────────────────────────
class NavButton(QPushButton):
    """
    Sidebar navigation button.
    Active state is indicated by a left accent bar and bold text.
    """

    def __init__(self, icon: str, label: str, parent=None) -> None:
        super().__init__(f"  {icon}  {label}", parent)
        self._active = False
        self._apply_style()
        self.setCheckable(False)
        self.setFixedHeight(42)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def set_active(self, active: bool) -> None:
        self._active = active
        self._apply_style()

    def _apply_style(self) -> None:
        if self._active:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: #EFF6FF;
                    color: {COLOR_PRIMARY};
                    border: none;
                    border-left: 3px solid {COLOR_PRIMARY};
                    border-radius: 0px;
                    text-align: left;
                    font-size: {FONT_SIZE_BASE}px;
                    font-weight: 700;
                    padding: 0 12px;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {COLOR_TEXT};
                    border: none;
                    border-left: 3px solid transparent;
                    border-radius: 0px;
                    text-align: left;
                    font-size: {FONT_SIZE_BASE}px;
                    font-weight: 400;
                    padding: 0 12px;
                }}
                QPushButton:hover {{
                    background-color: {COLOR_SURFACE};
                    color: {COLOR_PRIMARY};
                }}
            """)


# ── Main Window ───────────────────────────────────────────────────────────────
class MainWindow(QMainWindow):
    """
    Application shell with a fixed left sidebar and a stacked content area.
    Pages:
      0 → PresetListPage  (home / preset list)
      1 → TutorialPage
    """

    # Page index constants
    PAGE_LIST     = 0
    PAGE_TUTORIAL = 1

    def __init__(self) -> None:
        super().__init__()
        self._presets: list[Preset] = storage.load_presets()
        self._build_ui()
        self._navigate_to(self.PAGE_LIST)
        self.list_page.load_presets(self._presets)

    # ── UI construction ───────────────────────────────────────────────────────
    def _build_ui(self) -> None:
        self.setWindowTitle("App Preset")
        self.setMinimumSize(900, 600)
        self.resize(1060, 680)

        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ── Left sidebar ──────────────────────────────────────────────────────
        sidebar = self._build_sidebar()
        main_layout.addWidget(sidebar)

        # ── Vertical separator ────────────────────────────────────────────────
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setStyleSheet(f"color: {COLOR_BORDER};")
        main_layout.addWidget(sep)

        # ── Content area (stacked pages) ──────────────────────────────────────
        self.stack = QStackedWidget()

        self.list_page = PresetListPage()
        self.list_page.add_requested.connect(self._on_add_preset)
        self.list_page.edit_requested.connect(self._on_edit_preset)
        self.list_page.delete_requested.connect(self._on_delete_preset)
        self.list_page.launch_requested.connect(self._on_launch_preset)

        self.tutorial_page = TutorialPage()

        self.stack.addWidget(self.list_page)       # index 0
        self.stack.addWidget(self.tutorial_page)   # index 1

        main_layout.addWidget(self.stack, stretch=1)

    def _build_sidebar(self) -> QWidget:
        """Build the fixed-width left navigation sidebar."""
        sidebar = QWidget()
        sidebar.setFixedWidth(200)
        sidebar.setObjectName("Sidebar")
        # Use an ID selector — avoids cascading background into child QPushButton (NavButton).
        sidebar.setStyleSheet(f"QWidget#Sidebar {{ background-color: {COLOR_SURFACE}; }}")

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 16)
        layout.setSpacing(0)

        # ── App brand / logo area ─────────────────────────────────────────────
        brand = QWidget()
        brand.setObjectName("SidebarBrand")
        brand.setStyleSheet(f"QWidget#SidebarBrand {{ background-color: {COLOR_SURFACE}; }}")
        brand_layout = QVBoxLayout(brand)
        brand_layout.setContentsMargins(16, 20, 16, 16)
        brand_layout.setSpacing(2)

        app_title = QLabel("App Preset")
        app_title.setStyleSheet(
            f"font-size: 17px; font-weight: 700; color: {COLOR_TEXT}; background: transparent;"
        )
        app_version = QLabel("v1.0")
        app_version.setStyleSheet(
            f"font-size: {FONT_SIZE_SMALL}px; color: {COLOR_MUTED}; background: transparent;"
        )
        brand_layout.addWidget(app_title)
        brand_layout.addWidget(app_version)
        layout.addWidget(brand)

        # ── Divider ───────────────────────────────────────────────────────────
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setStyleSheet(f"color: {COLOR_BORDER};")
        layout.addWidget(divider)
        layout.addSpacing(8)

        # ── Navigation section label ──────────────────────────────────────────
        nav_label = QLabel("  MENU")
        nav_label.setStyleSheet(
            f"font-size: 10px; font-weight: 700; color: {COLOR_MUTED}; "
            f"letter-spacing: 1px; background: transparent;"
        )
        layout.addWidget(nav_label)
        layout.addSpacing(4)

        # ── Nav buttons ───────────────────────────────────────────────────────
        self._nav_buttons: list[NavButton] = []

        self.nav_list = NavButton("🗂️", "Preset Saya")
        self.nav_list.clicked.connect(lambda: self._navigate_to(self.PAGE_LIST))

        self.nav_tutorial = NavButton("📖", "Tutorial")
        self.nav_tutorial.clicked.connect(lambda: self._navigate_to(self.PAGE_TUTORIAL))

        for btn in (self.nav_list, self.nav_tutorial):
            self._nav_buttons.append(btn)
            layout.addWidget(btn)

        layout.addStretch()

        # ── Footer: data file location hint ──────────────────────────────────
        footer_lbl = QLabel(f"Data disimpan di:\n{storage.DATA_FILE}")
        footer_lbl.setWordWrap(True)
        footer_lbl.setStyleSheet(
            f"font-size: 10px; color: {COLOR_MUTED}; "
            f"padding: 0 12px; background: transparent;"
        )
        layout.addWidget(footer_lbl)

        return sidebar

    # ── Navigation ────────────────────────────────────────────────────────────
    def _navigate_to(self, page_index: int) -> None:
        """Switch the content area to the given page and update nav button states."""
        self.stack.setCurrentIndex(page_index)
        button_map = {
            self.PAGE_LIST:     self.nav_list,
            self.PAGE_TUTORIAL: self.nav_tutorial,
        }
        for btn in self._nav_buttons:
            btn.set_active(btn is button_map.get(page_index))

    # ── CRUD handlers ─────────────────────────────────────────────────────────
    def _on_add_preset(self) -> None:
        """Open the Add dialog and persist if the user confirms."""
        dialog = AddPresetDialog(self)
        if dialog.exec() and dialog.result_preset:
            preset = dialog.result_preset
            self._presets = storage.add_preset(self._presets, preset)
            self.list_page.add_card(preset)

    def _on_edit_preset(self, preset_id: str) -> None:
        """Open the Edit dialog for the preset with the given id."""
        preset = self._find_preset(preset_id)
        if not preset:
            return
        dialog = EditPresetDialog(preset, self)
        if dialog.exec() and dialog.result_preset:
            updated = dialog.result_preset
            self._presets = storage.update_preset(self._presets, updated)
            self.list_page.update_card(updated)

    def _on_delete_preset(self, preset_id: str) -> None:
        """Remove the preset and refresh the list."""
        self._presets = storage.delete_preset(self._presets, preset_id)
        self.list_page.remove_card(preset_id)

    def _on_launch_preset(self, preset_id: str) -> None:
        """Launch all apps in the preset; show errors if any fail."""
        preset = self._find_preset(preset_id)
        if not preset:
            return
        errors = launch_preset(preset)
        if errors:
            error_text = "\n".join(f"• {e}" for e in errors)
            QMessageBox.warning(
                self,
                "Gagal Membuka Beberapa Aplikasi",
                f"Preset <b>{preset.name}</b> dijalankan, "
                f"tetapi beberapa aplikasi gagal dibuka:\n\n{error_text}",
            )

    # ── Helper ────────────────────────────────────────────────────────────────
    def _find_preset(self, preset_id: str) -> Preset | None:
        """Return the preset matching the given id, or None."""
        return next((p for p in self._presets if p.preset_id == preset_id), None)


# ── Application entry point ───────────────────────────────────────────────────
def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("App Preset")
    app.setApplicationVersion("1.0")
    app.setStyleSheet(GLOBAL_STYLE)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
