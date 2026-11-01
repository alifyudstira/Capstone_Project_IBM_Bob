# styles/theme.py
# Centralized theme and stylesheet definitions for App Preset.
# Edit colors/fonts here to restyle the entire app at once.

# ── Palette ──────────────────────────────────────────────────────────────────
COLOR_BG          = "#FFFFFF"   # main background
COLOR_SURFACE     = "#F0F4FF"   # card / panel background
COLOR_BORDER      = "#D0DCFF"   # subtle borders
COLOR_PRIMARY     = "#2563EB"   # blue accent (buttons, highlights)
COLOR_PRIMARY_HOV = "#1D4ED8"   # primary hover state
COLOR_PRIMARY_TXT = "#FFFFFF"   # text on primary buttons
COLOR_DANGER      = "#EF4444"   # delete / destructive actions
COLOR_DANGER_HOV  = "#DC2626"
COLOR_TEXT        = "#1E293B"   # main body text
COLOR_MUTED       = "#64748B"   # secondary / placeholder text
COLOR_TAG_EXE     = "#DBEAFE"   # badge: .exe app
COLOR_TAG_EXE_TXT = "#1D4ED8"
COLOR_TAG_STORE   = "#EDE9FE"   # badge: store app
COLOR_TAG_STORE_TXT = "#6D28D9"
COLOR_TAG_WEB     = "#DCFCE7"   # badge: browser / URL
COLOR_TAG_WEB_TXT = "#15803D"

FONT_FAMILY = "Segoe UI, SF Pro Display, Helvetica Neue, Arial, sans-serif"
FONT_SIZE_BASE = 14
FONT_SIZE_SMALL = 12
FONT_SIZE_TITLE = 20
FONT_SIZE_HEADER = 16

# ── Global stylesheet (applied to QApplication) ───────────────────────────────
# IMPORTANT: Do NOT set background-color on the base QWidget rule.
# QPushButton IS-A QWidget, so any QWidget{background} in a parent's scoped
# stylesheet cascades into its child buttons and overrides their background.
# Solution: set bg only on specific types; use style_btn_*() helpers for buttons.
GLOBAL_STYLE = f"""
/* ── Base font / color only (no background — prevents cascade into buttons) ── */
QWidget {{
    color: {COLOR_TEXT};
    font-family: {FONT_FAMILY};
    font-size: {FONT_SIZE_BASE}px;
}}

/* ── Window backgrounds (specific types only) ── */
QMainWindow {{
    background-color: {COLOR_BG};
}}
QDialog {{
    background-color: {COLOR_BG};
}}
QStackedWidget {{
    background-color: {COLOR_BG};
}}
QScrollArea {{
    background-color: {COLOR_BG};
}}

/* ── Labels ── */
QLabel {{
    background: transparent;
    color: {COLOR_TEXT};
}}

/* ── Line edits ── */
QLineEdit {{
    background-color: {COLOR_BG};
    border: 1.5px solid {COLOR_BORDER};
    border-radius: 6px;
    padding: 6px 10px;
    color: {COLOR_TEXT};
    font-size: {FONT_SIZE_BASE}px;
}}
QLineEdit:focus {{
    border-color: {COLOR_PRIMARY};
}}
QLineEdit::placeholder {{
    color: {COLOR_MUTED};
}}

/* ── Scroll areas ── */
QScrollArea {{
    border: none;
    background-color: {COLOR_BG};
}}
QScrollBar:vertical {{
    background: {COLOR_SURFACE};
    width: 8px;
    border-radius: 4px;
}}
QScrollBar::handle:vertical {{
    background: {COLOR_BORDER};
    border-radius: 4px;
    min-height: 30px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

/* ── Combo box ── */
QComboBox {{
    background-color: {COLOR_BG};
    border: 1.5px solid {COLOR_BORDER};
    border-radius: 6px;
    padding: 5px 10px;
    font-size: {FONT_SIZE_BASE}px;
    color: {COLOR_TEXT};
}}
QComboBox:focus {{
    border-color: {COLOR_PRIMARY};
}}
QComboBox QAbstractItemView {{
    background-color: {COLOR_BG};
    border: 1.5px solid {COLOR_BORDER};
    border-radius: 6px;
    selection-background-color: {COLOR_SURFACE};
    selection-color: {COLOR_PRIMARY};
}}

/* ── Tool tips ── */
QToolTip {{
    background-color: {COLOR_TEXT};
    color: {COLOR_BG};
    border: none;
    border-radius: 4px;
    padding: 4px 8px;
    font-size: {FONT_SIZE_SMALL}px;
}}

/* ── Message boxes ── */
QMessageBox {{
    background-color: {COLOR_BG};
}}

/* ── Tab widget (used in Tutorial) ── */
QTabWidget::pane {{
    border: 1.5px solid {COLOR_BORDER};
    border-radius: 6px;
    background-color: {COLOR_BG};
}}
QTabBar::tab {{
    background-color: {COLOR_SURFACE};
    color: {COLOR_MUTED};
    border: 1.5px solid {COLOR_BORDER};
    border-bottom: none;
    border-radius: 6px 6px 0 0;
    padding: 6px 16px;
    margin-right: 4px;
    font-size: {FONT_SIZE_BASE}px;
}}
QTabBar::tab:selected {{
    background-color: {COLOR_BG};
    color: {COLOR_PRIMARY};
    font-weight: 600;
}}
QTabBar::tab:hover:!selected {{
    background-color: {COLOR_BG};
}}
"""

# ── Per-widget helper snippets ─────────────────────────────────────────────────
CARD_STYLE = f"""
    QFrame {{
        background-color: {COLOR_SURFACE};
        border: 1.5px solid {COLOR_BORDER};
        border-radius: 10px;
    }}
"""

SIDEBAR_STYLE = f"""
    QWidget {{
        background-color: {COLOR_SURFACE};
        border-right: 1.5px solid {COLOR_BORDER};
    }}
"""

HEADER_LABEL_STYLE = f"""
    font-size: {FONT_SIZE_TITLE}px;
    font-weight: 700;
    color: {COLOR_TEXT};
"""

SUBHEADER_LABEL_STYLE = f"""
    font-size: {FONT_SIZE_HEADER}px;
    font-weight: 600;
    color: {COLOR_TEXT};
"""

MUTED_LABEL_STYLE = f"""
    font-size: {FONT_SIZE_SMALL}px;
    color: {COLOR_MUTED};
"""

def tag_badge_style(bg: str, fg: str) -> str:
    """Return an inline style string for a small colored tag badge."""
    return (
        f"background-color: {bg}; color: {fg}; border-radius: 4px; "
        f"padding: 2px 7px; font-size: {FONT_SIZE_SMALL}px; font-weight: 600;"
    )


# ── Button style helpers ───────────────────────────────────────────────────────
# Always call one of these helpers on EVERY QPushButton after creating it.
# Never rely on global QPushButton{} rules because a parent widget's scoped
# stylesheet will shadow the global rule for all its child buttons.

def style_btn_primary(btn) -> None:
    """
    Apply the primary (blue filled) style to a QPushButton.
    Must be called explicitly — the global stylesheet no longer defines a
    default QPushButton rule to avoid cascade-bleed from parent stylesheets.
    """
    btn.setStyleSheet(f"""
        QPushButton {{
            background-color: {COLOR_PRIMARY};
            color: {COLOR_PRIMARY_TXT};
            border: none;
            border-radius: 6px;
            padding: 7px 18px;
            font-size: {FONT_SIZE_BASE}px;
            font-weight: 600;
        }}
        QPushButton:hover {{
            background-color: {COLOR_PRIMARY_HOV};
        }}
        QPushButton:pressed {{
            background-color: {COLOR_PRIMARY_HOV};
        }}
        QPushButton:disabled {{
            background-color: {COLOR_BORDER};
            color: {COLOR_MUTED};
        }}
    """)


def style_btn_secondary(btn) -> None:
    """
    Apply the outlined secondary style directly to a QPushButton.
    Equivalent to QPushButton[secondary="true"] but works inside any parent stylesheet scope.
    """
    btn.setProperty("secondary", "true")
    btn.setStyleSheet(f"""
        QPushButton {{
            background-color: transparent;
            color: {COLOR_PRIMARY};
            border: 1.5px solid {COLOR_PRIMARY};
            border-radius: 6px;
            padding: 7px 18px;
            font-size: {FONT_SIZE_BASE}px;
            font-weight: 600;
        }}
        QPushButton:hover {{
            background-color: {COLOR_SURFACE};
        }}
        QPushButton:pressed {{
            background-color: {COLOR_SURFACE};
        }}
        QPushButton:disabled {{
            background-color: transparent;
            color: {COLOR_MUTED};
            border-color: {COLOR_BORDER};
        }}
    """)


def style_btn_danger(btn) -> None:
    """
    Apply the danger/destructive style directly to a QPushButton.
    Equivalent to QPushButton[danger="true"] but works inside any parent stylesheet scope.
    """
    btn.setProperty("danger", "true")
    btn.setStyleSheet(f"""
        QPushButton {{
            background-color: {COLOR_DANGER};
            color: #FFFFFF;
            border: none;
            border-radius: 6px;
            padding: 7px 18px;
            font-size: {FONT_SIZE_BASE}px;
            font-weight: 600;
        }}
        QPushButton:hover {{
            background-color: {COLOR_DANGER_HOV};
        }}
        QPushButton:pressed {{
            background-color: {COLOR_DANGER_HOV};
        }}
    """)
