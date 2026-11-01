# ui/tutorial.py
# Tutorial page — explains how to add the three types of app entries
# on both Windows and macOS.

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTabWidget, QScrollArea, QFrame, QSizePolicy,
)
from PyQt6.QtCore import Qt

from styles.theme import (
    HEADER_LABEL_STYLE, SUBHEADER_LABEL_STYLE, MUTED_LABEL_STYLE,
    COLOR_SURFACE, COLOR_BORDER, COLOR_PRIMARY, COLOR_TEXT, COLOR_MUTED,
    COLOR_TAG_EXE, COLOR_TAG_EXE_TXT,
    COLOR_TAG_STORE, COLOR_TAG_STORE_TXT,
    COLOR_TAG_WEB, COLOR_TAG_WEB_TXT,
    FONT_SIZE_BASE, FONT_SIZE_SMALL,
)


# ── Re-usable building blocks ─────────────────────────────────────────────────
def _section_card(title: str, icon: str, tag_color: str, tag_txt: str,
                  paragraphs: list[str], steps: list[str]) -> QFrame:
    """
    Build a styled card for one tutorial section.
    paragraphs → introductory text blocks
    steps      → numbered step instructions
    """
    card = QFrame()
    card.setStyleSheet(f"""
        QFrame {{
            background-color: {COLOR_SURFACE};
            border: 1.5px solid {COLOR_BORDER};
            border-radius: 10px;
        }}
    """)

    layout = QVBoxLayout(card)
    layout.setContentsMargins(20, 18, 20, 18)
    layout.setSpacing(10)

    # ── Header row ────────────────────────────────────────────────────────────
    header_row = QHBoxLayout()
    header_row.setSpacing(10)

    icon_lbl = QLabel(icon)
    icon_lbl.setStyleSheet(f"font-size: 24px; background: transparent;")
    header_row.addWidget(icon_lbl)

    title_lbl = QLabel(title)
    title_lbl.setStyleSheet(SUBHEADER_LABEL_STYLE + " background: transparent;")
    header_row.addWidget(title_lbl)

    tag_lbl = QLabel(title.split()[0])
    tag_lbl.setStyleSheet(
        f"background-color: {tag_color}; color: {tag_txt}; border-radius: 4px;"
        f"padding: 2px 8px; font-size: {FONT_SIZE_SMALL}px; font-weight: 600;"
    )
    header_row.addWidget(tag_lbl)
    header_row.addStretch()
    layout.addLayout(header_row)

    # ── Description paragraphs ────────────────────────────────────────────────
    for text in paragraphs:
        p = QLabel(text)
        p.setWordWrap(True)
        p.setStyleSheet(f"background: transparent; color: {COLOR_TEXT}; "
                        f"font-size: {FONT_SIZE_BASE}px;")
        layout.addWidget(p)

    # ── Numbered steps ────────────────────────────────────────────────────────
    if steps:
        step_lbl = QLabel("Langkah-langkah:")
        step_lbl.setStyleSheet(
            f"background: transparent; font-weight: 600; color: {COLOR_TEXT};"
        )
        layout.addWidget(step_lbl)

        for i, step in enumerate(steps, start=1):
            row = QHBoxLayout()
            row.setSpacing(10)

            num = QLabel(str(i))
            num.setFixedSize(24, 24)
            num.setAlignment(Qt.AlignmentFlag.AlignCenter)
            num.setStyleSheet(
                f"background-color: {COLOR_PRIMARY}; color: #FFFFFF; "
                f"border-radius: 12px; font-weight: 700; font-size: {FONT_SIZE_SMALL}px;"
            )

            text_lbl = QLabel(step)
            text_lbl.setWordWrap(True)
            text_lbl.setStyleSheet(
                f"background: transparent; color: {COLOR_TEXT}; "
                f"font-size: {FONT_SIZE_BASE}px;"
            )
            text_lbl.setSizePolicy(
                QSizePolicy.Policy.Expanding,
                QSizePolicy.Policy.Preferred,
            )

            row.addWidget(num, alignment=Qt.AlignmentFlag.AlignTop)
            row.addWidget(text_lbl)
            layout.addLayout(row)

    return card


def _hint_box(text: str) -> QFrame:
    """Light blue info box for tips."""
    box = QFrame()
    box.setStyleSheet("""
        QFrame {
            background-color: #EFF6FF;
            border-left: 4px solid #2563EB;
            border-radius: 6px;
        }
    """)
    layout = QVBoxLayout(box)
    layout.setContentsMargins(14, 10, 14, 10)
    lbl = QLabel(text)
    lbl.setWordWrap(True)
    lbl.setStyleSheet(f"background: transparent; color: {COLOR_TEXT}; "
                      f"font-size: {FONT_SIZE_BASE}px;")
    layout.addWidget(lbl)
    return box


def _scrollable_page(content_widget: QWidget) -> QScrollArea:
    """Wrap a widget in a scroll area."""
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setWidget(content_widget)
    scroll.setFrameShape(QFrame.Shape.NoFrame)
    return scroll


# ── OS-specific page builders ─────────────────────────────────────────────────
def _build_windows_page() -> QScrollArea:
    page = QWidget()
    layout = QVBoxLayout(page)
    layout.setContentsMargins(24, 24, 24, 24)
    layout.setSpacing(16)

    # ── Intro ─────────────────────────────────────────────────────────────────
    intro = QLabel(
        "Panduan ini menjelaskan cara menambahkan aplikasi ke dalam sebuah preset "
        "di sistem operasi <b>Windows</b>."
    )
    intro.setWordWrap(True)
    intro.setStyleSheet(f"color: {COLOR_TEXT}; font-size: {FONT_SIZE_BASE}px;")
    layout.addWidget(intro)

    # ── Section 1: EXE ────────────────────────────────────────────────────────
    layout.addWidget(_section_card(
        title      = "EXE  –  Aplikasi Desktop (.exe)",
        icon       = "⚙️",
        tag_color  = COLOR_TAG_EXE,
        tag_txt    = COLOR_TAG_EXE_TXT,
        paragraphs = [
            "Aplikasi desktop klasik di Windows memiliki file .exe sebagai titik masuk. "
            "Kamu perlu menentukan path lengkap ke file tersebut.",
        ],
        steps = [
            "Klik kanan ikon aplikasi di Desktop atau Start Menu → pilih "
            "<b>Open file location</b> (Buka lokasi file).",
            "Jika muncul folder Shortcut, klik kanan lagi pada file .lnk → "
            "<b>Open file location</b> sekali lagi untuk sampai ke .exe asli.",
            "Salin path lengkap dari address bar Explorer, "
            "contoh: <code>C:\\Program Files\\Microsoft VS Code\\Code.exe</code>",
            "Di App Preset, pilih tipe <b>EXE / App</b>, lalu tempel path tersebut "
            "di kolom <b>Target / Path</b>.",
        ],
    ))

    layout.addWidget(_hint_box(
        "💡  Tip: Kamu juga bisa drag & drop file .exe dari Explorer "
        "ke kolom Target / Path pada dialog tambah aplikasi."
    ))

    # ── Section 2: Microsoft Store ────────────────────────────────────────────
    layout.addWidget(_section_card(
        title      = "Store  –  Aplikasi Microsoft Store",
        icon       = "🏪",
        tag_color  = COLOR_TAG_STORE,
        tag_txt    = COLOR_TAG_STORE_TXT,
        paragraphs = [
            "Aplikasi dari Microsoft Store tidak memiliki path .exe yang dapat diakses "
            "langsung. Sebagai gantinya, gunakan <b>URI scheme</b> yang disediakan oleh "
            "aplikasi tersebut.",
        ],
        steps = [
            "Cari nama URI scheme aplikasi. Contoh umum:\n"
            "  • Spotify → <code>spotify:</code>\n"
            "  • WhatsApp → <code>whatsapp:</code>\n"
            "  • Microsoft Store itu sendiri → <code>ms-windows-store:</code>\n"
            "  • Slack → <code>slack:</code>",
            "Untuk mencari URI scheme, ketik nama aplikasi + 'URI scheme Windows' di "
            "mesin pencari, atau buka <b>Pengaturan → Aplikasi → Aplikasi Default → "
            "Pilih aplikasi default berdasarkan protokol</b>.",
            "Di App Preset, pilih tipe <b>Store App</b>, lalu masukkan URI scheme "
            "(termasuk titik dua di akhir), contoh: <code>spotify:</code>",
        ],
    ))

    layout.addWidget(_hint_box(
        "💡  Tip: Jika kamu tidak menemukan URI scheme, coba tekan "
        "Win + R lalu ketik URI-nya (misal spotify:) dan tekan OK. "
        "Jika aplikasi terbuka, URI scheme tersebut valid."
    ))

    # ── Section 3: Browser ────────────────────────────────────────────────────
    layout.addWidget(_section_card(
        title      = "Browser  –  Buka Website Tertentu",
        icon       = "🌐",
        tag_color  = COLOR_TAG_WEB,
        tag_txt    = COLOR_TAG_WEB_TXT,
        paragraphs = [
            "Gunakan tipe ini untuk membuka sebuah URL secara langsung di browser default "
            "kamu. Cocok untuk membuka dashboard, dokumentasi, atau tool berbasis web.",
        ],
        steps = [
            "Buka halaman website yang ingin kamu simpan di browser.",
            "Salin URL lengkap dari address bar, "
            "contoh: <code>https://docs.python.org/3/</code>",
            "Di App Preset, pilih tipe <b>Browser / URL</b>, lalu tempel URL tersebut "
            "di kolom <b>Target / Path</b>.",
            "App Preset akan membuka URL tersebut di browser default Windows saat preset "
            "dijalankan.",
        ],
    ))

    layout.addStretch()
    return _scrollable_page(page)


def _build_macos_page() -> QScrollArea:
    page = QWidget()
    layout = QVBoxLayout(page)
    layout.setContentsMargins(24, 24, 24, 24)
    layout.setSpacing(16)

    intro = QLabel(
        "Panduan ini menjelaskan cara menambahkan aplikasi ke dalam sebuah preset "
        "di sistem operasi <b>macOS</b>."
    )
    intro.setWordWrap(True)
    intro.setStyleSheet(f"color: {COLOR_TEXT}; font-size: {FONT_SIZE_BASE}px;")
    layout.addWidget(intro)

    # ── Section 1: .app bundle ─────────────────────────────────────────────────
    layout.addWidget(_section_card(
        title      = "EXE  –  Aplikasi Desktop (.app)",
        icon       = "⚙️",
        tag_color  = COLOR_TAG_EXE,
        tag_txt    = COLOR_TAG_EXE_TXT,
        paragraphs = [
            "Aplikasi di macOS dikemas dalam bundle <code>.app</code> yang terletak di "
            "folder <b>/Applications</b>. Kamu cukup menentukan path ke bundle tersebut.",
        ],
        steps = [
            "Buka <b>Finder → Applications</b>.",
            "Temukan aplikasi yang diinginkan, klik kanan → "
            "<b>Get Info</b>, lalu lihat field <b>Where</b> untuk mendapatkan path.",
            "Path lengkap biasanya berupa: <code>/Applications/NamaAplikasi.app</code>",
            "Di App Preset, pilih tipe <b>EXE / App</b>, lalu masukkan path tersebut, "
            "contoh: <code>/Applications/Visual Studio Code.app</code>",
        ],
    ))

    layout.addWidget(_hint_box(
        "💡  Tip: Di macOS, kamu juga bisa drag & drop bundle .app dari Finder "
        "langsung ke kolom Target / Path pada dialog."
    ))

    # ── Section 2: Mac App Store ───────────────────────────────────────────────
    layout.addWidget(_section_card(
        title      = "Store  –  Aplikasi Mac App Store",
        icon       = "🏪",
        tag_color  = COLOR_TAG_STORE,
        tag_txt    = COLOR_TAG_STORE_TXT,
        paragraphs = [
            "Aplikasi dari Mac App Store umumnya disimpan di <b>/Applications</b> seperti "
            "aplikasi biasa, sehingga bisa diluncurkan dengan perintah "
            "<code>open -a NamaApp</code>. Cukup masukkan <b>nama bundle aplikasi</b>.",
        ],
        steps = [
            "Buka <b>Finder → Applications</b> dan catat nama persisnya, "
            "contoh: <b>Xcode</b>, <b>Spotify</b>, <b>Notion</b>.",
            "Di App Preset, pilih tipe <b>Store App</b>.",
            "Masukkan nama aplikasi persis seperti yang tertulis di Finder "
            "(tanpa ekstensi .app), contoh: <code>Spotify</code>",
            "App Preset akan menjalankan perintah <code>open -a Spotify</code> "
            "secara otomatis.",
        ],
    ))

    # ── Section 3: Browser ────────────────────────────────────────────────────
    layout.addWidget(_section_card(
        title      = "Browser  –  Buka Website Tertentu",
        icon       = "🌐",
        tag_color  = COLOR_TAG_WEB,
        tag_txt    = COLOR_TAG_WEB_TXT,
        paragraphs = [
            "Sama seperti Windows, kamu bisa membuka URL langsung di browser default macOS.",
        ],
        steps = [
            "Salin URL lengkap dari address bar browser.",
            "Di App Preset, pilih tipe <b>Browser / URL</b>.",
            "Tempel URL tersebut di kolom Target / Path.",
            "App Preset akan membuka URL di browser default kamu saat preset dijalankan.",
        ],
    ))

    layout.addStretch()
    return _scrollable_page(page)


# ── Main TutorialPage widget ──────────────────────────────────────────────────
class TutorialPage(QWidget):
    """
    Full tutorial page presented as a tab widget with Windows and macOS tabs.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Page header ───────────────────────────────────────────────────────
        header = QWidget()
        header.setObjectName("TutorialHeader")
        header.setStyleSheet(f"QWidget#TutorialHeader {{ background-color: #F0F4FF; border-bottom: 1.5px solid {COLOR_BORDER}; }}")
        h_layout = QVBoxLayout(header)
        h_layout.setContentsMargins(28, 20, 28, 16)
        h_layout.setSpacing(4)

        title = QLabel("📖  Tutorial")
        title.setStyleSheet(HEADER_LABEL_STYLE + " background: transparent;")
        subtitle = QLabel("Pelajari cara menambahkan tiga jenis aplikasi ke dalam preset kamu.")
        subtitle.setStyleSheet(MUTED_LABEL_STYLE + " background: transparent;")

        h_layout.addWidget(title)
        h_layout.addWidget(subtitle)
        root.addWidget(header)

        # ── OS Tabs ───────────────────────────────────────────────────────────
        tabs = QTabWidget()
        tabs.setStyleSheet("QTabWidget { background: transparent; }")
        tabs.addTab(_build_windows_page(), "🪟  Windows")
        tabs.addTab(_build_macos_page(),   "🍎  macOS")

        root.addWidget(tabs)
