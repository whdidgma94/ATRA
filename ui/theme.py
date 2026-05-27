DARK_THEME = """
QMainWindow, QWidget {
    background-color: #1e1e2e;
    color: #cdd6f4;
    font-family: "Segoe UI", "맑은 고딕", sans-serif;
    font-size: 13px;
}

QLabel {
    color: #cdd6f4;
    background-color: transparent;
}
QLabel#appTitle {
    color: #cba6f7;
    font-size: 44px;
    font-weight: 800;
    letter-spacing: 6px;
}
QLabel#subtitle {
    color: #585b70;
    font-size: 13px;
    letter-spacing: 2px;
}
QLabel#pageTitle {
    color: #cdd6f4;
    font-size: 20px;
    font-weight: 700;
}
QLabel#sectionBadge {
    color: #1e1e2e;
    background-color: #cba6f7;
    border-radius: 10px;
    padding: 2px 10px;
    font-size: 11px;
    font-weight: 700;
}
QLabel#counterLabel {
    color: #a6adc8;
    font-size: 14px;
}

QPushButton {
    background-color: #cba6f7;
    color: #1e1e2e;
    border: none;
    border-radius: 8px;
    padding: 10px 28px;
    font-size: 14px;
    font-weight: 700;
    min-height: 38px;
}
QPushButton:hover {
    background-color: #d5b8ff;
}
QPushButton:pressed {
    background-color: #b794e8;
}
QPushButton:disabled {
    background-color: #313244;
    color: #585b70;
}
QPushButton#secondaryBtn {
    background-color: #313244;
    color: #cdd6f4;
}
QPushButton#secondaryBtn:hover {
    background-color: #45475a;
}
QPushButton#dangerBtn {
    background-color: #f38ba8;
    color: #1e1e2e;
}
QPushButton#dangerBtn:hover {
    background-color: #ff9ab8;
}
QPushButton#accentBtn {
    background-color: #89b4fa;
    color: #1e1e2e;
}
QPushButton#accentBtn:hover {
    background-color: #99c4ff;
}
QPushButton#successBtn {
    background-color: #a6e3a1;
    color: #1e1e2e;
}
QPushButton#successBtn:hover {
    background-color: #b6f3b1;
}

QFrame#card {
    background-color: #2a2a3e;
    border-radius: 14px;
    border: 1px solid #313244;
}
QFrame#infoCard {
    background-color: #181825;
    border-radius: 10px;
    border: 1px solid #313244;
}
QFrame#separator {
    background-color: #313244;
    max-height: 1px;
    min-height: 1px;
}

QTableWidget {
    background-color: #181825;
    border: 1px solid #313244;
    border-radius: 10px;
    gridline-color: #2a2a3e;
    selection-background-color: transparent;
}
QTableWidget::item {
    padding: 6px 10px;
    border: none;
    color: #cdd6f4;
    text-align: center;
}
QTableWidget::item:selected {
    background-color: #313244;
}
QHeaderView::section {
    background-color: #313244;
    color: #a6adc8;
    padding: 10px;
    border: none;
    border-right: 1px solid #1e1e2e;
    font-weight: 700;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 1px;
}
QHeaderView::section:last {
    border-right: none;
}
QHeaderView { border-radius: 0; }

QTreeWidget {
    background-color: #181825;
    color: #cdd6f4;
    border: 1px solid #313244;
    border-radius: 10px;
    outline: none;
}
QTreeWidget::item { height: 40px; padding-left: 10px; }
QTreeWidget::item:hover { background-color: #2a2a3e; }
QTreeWidget::item:selected { background-color: #45475a; color: #cdd6f4; }
QTreeWidget QHeaderView::section {
    background-color: #313244;
    color: #a6adc8;
    padding: 10px;
    border: none;
    border-right: 1px solid #1e1e2e;
    font-weight: 700;
    font-size: 12px;
}

QLineEdit {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 8px;
    padding: 9px 14px;
    font-size: 13px;
}
QLineEdit:focus { border: 1px solid #cba6f7; }
QLineEdit:placeholder { color: #585b70; }

QTextEdit, QPlainTextEdit {
    background-color: #181825;
    color: #cdd6f4;
    border: 1px solid #313244;
    border-radius: 8px;
    padding: 8px;
    font-size: 13px;
}
QTextEdit:focus, QPlainTextEdit:focus { border: 1px solid #cba6f7; }

QComboBox {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 8px;
    padding: 6px 12px;
    min-height: 34px;
}
QComboBox:focus { border: 1px solid #cba6f7; }
QComboBox::drop-down { border: none; width: 24px; }
QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid #6c7086;
    margin-right: 8px;
}
QComboBox QAbstractItemView {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    selection-background-color: #cba6f7;
    selection-color: #1e1e2e;
    outline: none;
}

QCheckBox { color: #cdd6f4; spacing: 10px; font-size: 14px; }
QCheckBox::indicator {
    width: 20px; height: 20px;
    border-radius: 5px;
    border: 2px solid #45475a;
    background-color: #313244;
}
QCheckBox::indicator:hover { border-color: #cba6f7; }
QCheckBox::indicator:checked {
    background-color: #cba6f7;
    border-color: #cba6f7;
    image: none;
}

QScrollBar:vertical {
    background-color: #181825;
    width: 8px;
    border-radius: 4px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background-color: #45475a;
    border-radius: 4px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover { background-color: #585b70; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: none; }

QScrollBar:horizontal {
    background-color: #181825;
    height: 8px;
    border-radius: 4px;
}
QScrollBar::handle:horizontal {
    background-color: #45475a;
    border-radius: 4px;
    min-width: 30px;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }

QScrollArea { border: none; background-color: transparent; }
QScrollArea > QWidget > QWidget { background-color: transparent; }

QDialog {
    background-color: #1e1e2e;
}

QMessageBox {
    background-color: #2a2a3e;
}
QMessageBox QLabel { color: #cdd6f4; }
"""

STATUS_COLORS = {
    "FAIL":       "#f38ba8",
    "Minor_Fail": "#fab387",
    "N/A":        "#a6adc8",
    "Error":      "#fab387",
    "Pass":       "#a6e3a1",
    "N/T":        "#89dceb",
    "Pending":    "#585b70",
    "Running":    "#f9e2af",
}

CELL_BG = {
    "Pending": "#45475a",
    "Running": "#f9e2af",
    "Pass":    "#a6e3a1",
    "Fail":    "#f38ba8",
    "Error":   "#fab387",
    "N/T":     "#89dceb",
    "N/A":     "#a6adc8",
}

CELL_FG = {
    "Pending": "#cdd6f4",
    "Running": "#1e1e2e",
    "Pass":    "#1e1e2e",
    "Fail":    "#1e1e2e",
    "Error":   "#1e1e2e",
    "N/T":     "#1e1e2e",
    "N/A":     "#1e1e2e",
}
