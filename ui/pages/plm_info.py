from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QScrollArea, QFrame, QMessageBox,
    QGridLayout
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor

from ui.theme import STATUS_COLORS

_TARGET_STATUSES = {"FAIL", "N/A", "Minor_Fail"}


class PLMInfoPage(QWidget):
    plm_complete = pyqtSignal(dict, dict)  # updated_data, total_result

    def __init__(self):
        super().__init__()
        self.raw_data = {}
        self.entry_map = []
        self.total_result = {}
        self._setup_ui()

    # ── Public API ────────────────────────────────────────────────────────────

    def load_data(self, reviewed_data: dict):
        self.raw_data = reviewed_data
        self.total_result = {
            "total": {"FAIL": 0, "N/A": 0},
            **{
                os_ver: {"FAIL": 0, "N/A": 0, "issue": [], "comment": []}
                for os_ver in ["SOS", "TOS", "UOS", "VOS", "BOS", "COS"]
            },
        }
        self.entry_map = []
        self._populate()

    # ── UI Build ──────────────────────────────────────────────────────────────

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 24, 30, 20)
        layout.setSpacing(16)

        title = QLabel("PLM 정보 입력")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        desc = QLabel("미확인 Fail 항목의 PLM 사례코드와 제목을 입력해 주세요.")
        desc.setStyleSheet("color: #475569; font-size: 13px;")
        layout.addWidget(desc)

        # Scrollable content area
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setSpacing(10)
        self.content_layout.setContentsMargins(4, 4, 4, 4)
        self.scroll.setWidget(self.content_widget)
        layout.addWidget(self.scroll, stretch=1)

        # Save button
        btn_save = QPushButton("💾  저장 및 닫기")
        btn_save.setFixedHeight(48)
        btn_save.clicked.connect(self._on_save)
        layout.addWidget(btn_save)

    def _clear_content(self):
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _populate(self):
        self._clear_content()
        self.entry_map = []

        for category, items in self.raw_data.items():
            # OS section header
            os_header = QLabel(f"  {category}")
            os_header.setStyleSheet(
                "background-color: #2563eb; color: #ffffff; "
                "font-size: 13px; font-weight: 700; "
                "border-radius: 6px; padding: 6px 12px;"
            )
            self.content_layout.addWidget(os_header)

            has_entry = False
            for item in items:
                if (item.get("status") in _TARGET_STATUSES
                        and item.get("is_reviewed") is False):
                    self._add_row(category, item)
                    has_entry = True

            if not has_entry:
                no_fail = QLabel("  문제점이 없습니다")
                no_fail.setStyleSheet("color: #475569; padding: 8px 14px;")
                self.content_layout.addWidget(no_fail)

        self.content_layout.addStretch()

    def _add_row(self, category: str, item_data: dict):
        card = QFrame()
        card.setObjectName("infoCard")
        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(16, 12, 16, 12)
        card_layout.setSpacing(16)

        # Left: info
        color = STATUS_COLORS.get(item_data["status"], "#1e293b")
        info_text = (
            f"<b style='color:{color}'>{item_data['name']}</b><br>"
            f"<span style='color:{color}'>{item_data['status']}</span><br>"
            f"<span style='color:#334155'>{item_data.get('content','')}</span>"
        )
        lbl_info = QLabel(info_text)
        lbl_info.setTextFormat(Qt.TextFormat.RichText)
        lbl_info.setWordWrap(True)
        lbl_info.setMinimumWidth(260)
        card_layout.addWidget(lbl_info, stretch=1)

        # Right: inputs
        input_frame = QFrame()
        input_frame.setStyleSheet("background: transparent;")
        input_grid = QGridLayout(input_frame)
        input_grid.setSpacing(8)
        input_grid.setContentsMargins(0, 0, 0, 0)

        # Status dropdown (only for FAIL)
        entry = {
            "data_ref": item_data,
            "old_status": item_data["status"],
            "os_ver": category,
            "status_widget": None,
        }

        if item_data["status"] == "FAIL":
            combo_status = QComboBox()
            combo_status.addItems(["FAIL", "N/A"])
            combo_status.setCurrentText(item_data["status"])
            combo_status.setFixedWidth(120)
            input_grid.addWidget(QLabel("상태:"), 0, 0, Qt.AlignmentFlag.AlignRight)
            input_grid.addWidget(combo_status, 0, 1)
            entry["status_widget"] = combo_status

        lbl_num = QLabel("사례코드:")
        lbl_num.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        entry_num = QLineEdit()
        entry_num.setPlaceholderText("PLM 사례코드")
        entry_num.setFixedWidth(280)
        if "plm_num" in item_data:
            entry_num.setText(item_data["plm_num"])

        lbl_title = QLabel("제목:")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        entry_title = QLineEdit()
        entry_title.setPlaceholderText("PLM 제목")
        entry_title.setFixedWidth(280)
        if "plm_title" in item_data:
            entry_title.setText(item_data["plm_title"])

        r = 1 if item_data["status"] == "FAIL" else 0
        input_grid.addWidget(lbl_num, r, 0)
        input_grid.addWidget(entry_num, r, 1)
        input_grid.addWidget(lbl_title, r + 1, 0)
        input_grid.addWidget(entry_title, r + 1, 1)

        card_layout.addWidget(input_frame)

        entry["num_widget"] = entry_num
        entry["title_widget"] = entry_title
        self.entry_map.append(entry)
        self.content_layout.addWidget(card)

    # ── Save ──────────────────────────────────────────────────────────────────

    def _on_save(self):
        reply = QMessageBox.question(
            self, "PLM Info update 종료 알림",
            "Fail 항목 PLM 정보를 이대로 저장하시겠습니까?",
            QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel,
        )
        if reply != QMessageBox.StandardButton.Ok:
            return

        for entry in self.entry_map:
            p_title = entry["title_widget"].text().strip()
            p_num = entry["num_widget"].text().strip()
            old_status = entry["old_status"]
            os_ver = entry["os_ver"]

            try:
                if entry["status_widget"] is not None:
                    new_status = entry["status_widget"].currentText()
                else:
                    new_status = old_status

                entry["data_ref"]["status"] = new_status
                if os_ver in self.total_result:
                    self.total_result[os_ver][old_status] = (
                        self.total_result[os_ver].get(old_status, 0) - 1
                    )
                    self.total_result[os_ver][new_status] = (
                        self.total_result[os_ver].get(new_status, 0) + 1
                    )
                self.total_result["total"][old_status] = (
                    self.total_result["total"].get(old_status, 0) - 1
                )
                self.total_result["total"][new_status] = (
                    self.total_result["total"].get(new_status, 0) + 1
                )

                if p_title or p_num:
                    if new_status == "FAIL":
                        entry["data_ref"]["plm_title"] = p_title
                        entry["data_ref"]["plm_num"] = p_num
                        if os_ver in self.total_result:
                            self.total_result[os_ver]["issue"].append(
                                f" - [{p_num}] {p_title}"
                            )
                    elif new_status == "N/A":
                        entry["data_ref"]["plm_title"] = p_title
                        if os_ver in self.total_result:
                            self.total_result[os_ver]["comment"].append(f" - {p_title}")
            except KeyError:
                pass

        self.plm_complete.emit(self.raw_data, self.total_result)
