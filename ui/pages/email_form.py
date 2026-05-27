from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QFrame, QApplication
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal

from email_feature.template_generator import generate_html, generate_title


class EmailFormPage(QWidget):
    def __init__(self):
        super().__init__()
        self.table_form = ""
        self._setup_ui()

    # ── Public API ────────────────────────────────────────────────────────────

    def load_data(self, table_form: str):
        self.table_form = table_form

    # ── UI Build ──────────────────────────────────────────────────────────────

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(60, 40, 60, 40)
        layout.setSpacing(16)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        title = QLabel("이메일 템플릿 생성")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        desc = QLabel("발신 정보와 버전 정보를 입력하면 이메일 제목과 본문 HTML을 클립보드에 복사합니다.")
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #64748b; font-size: 13px;")
        layout.addWidget(desc)

        layout.addSpacing(10)

        # Card
        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(28, 24, 28, 24)
        card_layout.setSpacing(14)

        # Row 1 — Name + rank
        row1 = QHBoxLayout()
        row1.setSpacing(12)

        self.entry_name = QLineEdit()
        self.entry_name.setPlaceholderText("이름 입력")
        self.entry_name.setText("김혜숙")
        self.entry_name.setFixedWidth(160)

        self.combo_rank = QComboBox()
        self.combo_rank.addItems(["연구원", "주임", "선임", "책임", "수석"])
        self.combo_rank.setCurrentText("선임")
        self.combo_rank.setFixedWidth(110)

        row1.addWidget(QLabel("발신자"))
        row1.addWidget(self.entry_name)
        row1.addWidget(self.combo_rank)
        row1.addStretch()
        card_layout.addLayout(row1)

        self._add_field(card_layout, "Release 버전", "release",
                        "예: 2026 R1", 360)
        self._add_field(card_layout, "SmartThings 버전", "app_ver",
                        "예: 1.8.45.17 RC1", 360)

        layout.addWidget(card)

        # Action buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(14)

        self.btn_title = QPushButton("📋  이메일 제목 복사")
        self.btn_title.setObjectName("secondaryBtn")
        self.btn_title.setFixedHeight(50)
        self.btn_title.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_title.clicked.connect(self._copy_title)

        self.btn_html = QPushButton("📨  이메일 본문 HTML 복사")
        self.btn_html.setFixedHeight(50)
        self.btn_html.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_html.clicked.connect(self._copy_html)

        btn_row.addWidget(self.btn_title)
        btn_row.addWidget(self.btn_html)
        layout.addLayout(btn_row)

        # Status label
        self.lbl_status = QLabel("")
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_status.setStyleSheet("color: #a6e3a1; font-size: 13px;")
        layout.addWidget(self.lbl_status)

        layout.addStretch()

    def _add_field(self, parent_layout, label_text, attr, placeholder, width):
        row = QHBoxLayout()
        row.setSpacing(12)
        lbl = QLabel(label_text)
        lbl.setFixedWidth(130)
        entry = QLineEdit()
        entry.setPlaceholderText(placeholder)
        entry.setFixedWidth(width)
        row.addWidget(lbl)
        row.addWidget(entry)
        row.addStretch()
        parent_layout.addLayout(row)
        setattr(self, f"entry_{attr}", entry)

    # ── Actions ───────────────────────────────────────────────────────────────

    def _validate(self):
        name = self.entry_name.text().strip()
        rank = self.combo_rank.currentText()
        release = self.entry_release.text().strip()
        app_ver = self.entry_app_ver.text().strip()
        if not name:
            return None, "이름을 입력해 주세요."
        if not release:
            return None, "Release 버전을 입력해 주세요."
        if not app_ver:
            return None, "SmartThings 버전을 입력해 주세요."
        return (name, rank, release, app_ver), None

    def _copy_title(self):
        release = self.entry_release.text().strip()
        app_ver = self.entry_app_ver.text().strip()
        if not release or not app_ver:
            self._show_status("⚠  Release 버전과 ST 버전을 입력해 주세요.", error=True)
            return
        result = generate_title(release, app_ver)
        QApplication.clipboard().setText(result)
        self._show_status("✅  이메일 제목이 클립보드에 복사되었습니다!")

    def _copy_html(self):
        data, err = self._validate()
        if err:
            self._show_status(f"⚠  {err}", error=True)
            return
        name, rank, release, app_ver = data
        html_result = generate_html(name, rank, release, app_ver, self.table_form)
        QApplication.clipboard().setText(html_result)
        self._show_status("✅  이메일 본문 HTML이 클립보드에 복사되었습니다!")

    def _show_status(self, msg, error=False):
        color = "#f38ba8" if error else "#a6e3a1"
        self.lbl_status.setStyleSheet(f"color: {color}; font-size: 13px;")
        self.lbl_status.setText(msg)
        QTimer.singleShot(3000, lambda: self.lbl_status.setText(""))
