DARK_THEME = """
/* ── Base ── */
QMainWindow, QWidget {
    background-color: #f8faff;
    color: #1e293b;
    font-family: "Segoe UI", "맑은 고딕", sans-serif;
    font-size: 13px;
}

/* ── Labels ── */
QLabel {
    color: #1e293b;
    background-color: transparent;
}
QLabel#appTitle {
    color: #1d4ed8;
    font-size: 44px;
    font-weight: 800;
    letter-spacing: 6px;
}
QLabel#subtitle {
    color: #475569;
    font-size: 13px;
    letter-spacing: 2px;
}
QLabel#pageTitle {
    color: #1e293b;
    font-size: 20px;
    font-weight: 700;
}
QLabel#sectionBadge {
    color: #ffffff;
    background-color: #2563eb;
    border-radius: 10px;
    padding: 2px 10px;
    font-size: 11px;
    font-weight: 700;
}
QLabel#counterLabel {
    color: #475569;
    font-size: 14px;
}

/* ── Buttons ── */
QPushButton {
    background-color: #2563eb;
    color: #ffffff;
    border: none;
    border-radius: 8px;
    padding: 10px 28px;
    font-size: 14px;
    font-weight: 700;
    min-height: 38px;
}
QPushButton:hover {
    background-color: #1d4ed8;
}
QPushButton:pressed {
    background-color: #1e40af;
}
QPushButton:disabled {
    background-color: #e2e8f0;
    color: #94a3b8;
}
QPushButton#secondaryBtn {
    background-color: #f1f5f9;
    color: #334155;
    border: 1px solid #e2e8f0;
}
QPushButton#secondaryBtn:hover {
    background-color: #e2e8f0;
}
QPushButton#dangerBtn {
    background-color: #ef4444;
    color: #ffffff;
}
QPushButton#dangerBtn:hover {
    background-color: #dc2626;
}
QPushButton#accentBtn {
    background-color: #3b82f6;
    color: #ffffff;
}
QPushButton#accentBtn:hover {
    background-color: #2563eb;
}
QPushButton#successBtn {
    background-color: #16a34a;
    color: #ffffff;
}
QPushButton#successBtn:hover {
    background-color: #15803d;
}

/* ── Cards ── */
QFrame#card {
    background-color: #ffffff;
    border-radius: 14px;
    border: 1px solid #e2e8f0;
}
QFrame#infoCard {
    background-color: #f8faff;
    border-radius: 10px;
    border: 1px solid #dbeafe;
}
QFrame#separator {
    background-color: #e2e8f0;
    max-height: 1px;
    min-height: 1px;
}

/* ── Table ── */
QTableWidget {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    gridline-color: #f1f5f9;
    selection-background-color: transparent;
}
QTableWidget::item {
    padding: 6px 10px;
    border: none;
    color: #1e293b;
    text-align: center;
}
QTableWidget::item:selected {
    background-color: #eff6ff;
}
QHeaderView::section {
    background-color: #f1f5f9;
    color: #475569;
    padding: 10px;
    border: none;
    border-right: 1px solid #e2e8f0;
    border-bottom: 1px solid #e2e8f0;
    font-weight: 700;
    font-size: 12px;
    letter-spacing: 1px;
}
QHeaderView::section:last {
    border-right: none;
}
QHeaderView { border-radius: 0; }

/* ── Tree Widget ── */
QTreeWidget {
    background-color: #ffffff;
    color: #1e293b;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    outline: none;
}
QTreeWidget::item { height: 40px; padding-left: 10px; }
QTreeWidget::item:hover { background-color: #eff6ff; }
QTreeWidget::item:selected { background-color: #dbeafe; color: #1e40af; }
QTreeWidget QHeaderView::section {
    background-color: #f1f5f9;
    color: #475569;
    padding: 10px;
    border: none;
    border-right: 1px solid #e2e8f0;
    border-bottom: 1px solid #e2e8f0;
    font-weight: 700;
    font-size: 12px;
}

/* ── Input ── */
QLineEdit {
    background-color: #ffffff;
    color: #1e293b;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    padding: 9px 14px;
    font-size: 13px;
}
QLineEdit:focus { border: 2px solid #2563eb; padding: 8px 13px; }

QTextEdit, QPlainTextEdit {
    background-color: #ffffff;
    color: #1e293b;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    padding: 8px;
    font-size: 13px;
}
QTextEdit:focus, QPlainTextEdit:focus { border: 2px solid #2563eb; }

/* ── ComboBox ── */
QComboBox {
    background-color: #ffffff;
    color: #1e293b;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    padding: 6px 12px;
    min-height: 34px;
}
QComboBox:focus { border: 2px solid #2563eb; }
QComboBox::drop-down { border: none; width: 24px; }
QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid #64748b;
    margin-right: 8px;
}
QComboBox QAbstractItemView {
    background-color: #ffffff;
    color: #1e293b;
    border: 1px solid #cbd5e1;
    selection-background-color: #dbeafe;
    selection-color: #1e40af;
    outline: none;
}

/* ── CheckBox ── */
QCheckBox { color: #1e293b; spacing: 10px; font-size: 14px; }
QCheckBox::indicator {
    width: 20px; height: 20px;
    border-radius: 5px;
    border: 2px solid #cbd5e1;
    background-color: #ffffff;
}
QCheckBox::indicator:hover { border-color: #2563eb; }
QCheckBox::indicator:checked {
    background-color: #2563eb;
    border-color: #2563eb;
}

/* ── ScrollBar ── */
QScrollBar:vertical {
    background-color: #f1f5f9;
    width: 8px;
    border-radius: 4px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background-color: #cbd5e1;
    border-radius: 4px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover { background-color: #94a3b8; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: none; }

QScrollBar:horizontal {
    background-color: #f1f5f9;
    height: 8px;
    border-radius: 4px;
}
QScrollBar::handle:horizontal {
    background-color: #cbd5e1;
    border-radius: 4px;
    min-width: 30px;
}
QScrollBar::handle:horizontal:hover { background-color: #94a3b8; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }

/* ── ScrollArea ── */
QScrollArea { border: none; background-color: transparent; }
QScrollArea > QWidget > QWidget { background-color: transparent; }

/* ── Dialog ── */
QDialog { background-color: #ffffff; }

/* ── MessageBox ── */
QMessageBox { background-color: #ffffff; }
QMessageBox QLabel { color: #1e293b; }
"""

STATUS_COLORS = {
    "FAIL":       "#dc2626",
    "Minor_Fail": "#d97706",
    "N/A":        "#475569",
    "Error":      "#d97706",
    "Pass":       "#16a34a",
    "N/T":        "#0891b2",
    "Pending":    "#64748b",
    "Running":    "#ca8a04",
}

CELL_BG = {
    "Pending": "#f1f5f9",
    "Running": "#fef9c3",
    "Pass":    "#dcfce7",
    "Fail":    "#fee2e2",
    "Error":   "#ffedd5",
    "N/T":     "#e0f2fe",
    "N/A":     "#f1f5f9",
}

CELL_FG = {
    "Pending": "#475569",
    "Running": "#854d0e",
    "Pass":    "#166534",
    "Fail":    "#991b1b",
    "Error":   "#9a3412",
    "N/T":     "#0c4a6e",
    "N/A":     "#475569",
}
