import base64
import copy
import os

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QCheckBox, QScrollArea, QFrame, QTextEdit,
    QMessageBox, QDialog, QSizePolicy, QGridLayout
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QPixmap, QColor
from PyQt6.QtWidgets import QApplication

import config.common_variable as cv
from ui.theme import STATUS_COLORS

_FAIL_STATUSES = {"FAIL", "Minor_Fail", "N/A", "Error"}


class ScreenshotDialog(QDialog):
    def __init__(self, b64_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("스크린샷")
        self.setStyleSheet("background-color: #ffffff;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        pixmap = QPixmap()
        pixmap.loadFromData(base64.b64decode(b64_data))
        pixmap = pixmap.scaled(800, 800, Qt.AspectRatioMode.KeepAspectRatio,
                               Qt.TransformationMode.SmoothTransformation)
        lbl = QLabel()
        lbl.setPixmap(pixmap)
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl)

        btn_close = QPushButton("닫기")
        btn_close.setFixedWidth(100)
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close, alignment=Qt.AlignmentFlag.AlignCenter)


class FailReviewerPage(QWidget):
    review_complete = pyqtSignal(dict, dict)  # reviewed_data, modified_parsed_results

    def __init__(self):
        super().__init__()
        self.result_cases = {}
        self.parsed_results = {}
        self.tc_data = {}
        self.failed_data = {}
        self.check_states = {}   # {category: [bool, ...]}
        self.categories = []
        self.current_category = ""
        self.current_index = 0
        self._setup_ui()

    # ── Public API ────────────────────────────────────────────────────────────

    def load_data(self, result_cases: dict, tc_data: dict, parsed_results: dict):
        self.result_cases = result_cases
        self.tc_data = tc_data
        self.parsed_results = parsed_results

        self.failed_data = {}
        self.check_states = {}
        for category, items in result_cases.items():
            fails = [item for item in items if item.get("status") in _FAIL_STATUSES]
            if fails:
                self.failed_data[category] = fails
                self.check_states[category] = [False] * len(fails)

        self.categories = list(self.failed_data.keys())
        self.combo_os.blockSignals(True)
        self.combo_os.clear()
        self.combo_os.addItems(self.categories)
        self.combo_os.blockSignals(False)

        if self.categories:
            self.current_category = self.categories[0]
            self.current_index = 0
            self._load_item()

    # ── UI Build ──────────────────────────────────────────────────────────────

    def _setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(30, 24, 30, 20)
        root.setSpacing(14)

        # ── Top bar ──
        top = QHBoxLayout()
        title = QLabel("Fail 검토")
        title.setObjectName("pageTitle")
        top.addWidget(title)
        top.addStretch()

        os_lbl = QLabel("OS:")
        os_lbl.setStyleSheet("color: #475569;")
        top.addWidget(os_lbl)
        self.combo_os = QComboBox()
        self.combo_os.setMinimumWidth(130)
        self.combo_os.currentTextChanged.connect(self._on_os_changed)
        top.addWidget(self.combo_os)
        root.addLayout(top)

        # ── Navigation ──
        nav = QHBoxLayout()
        self.btn_prev = QPushButton("← Prev")
        self.btn_prev.setObjectName("secondaryBtn")
        self.btn_prev.setFixedSize(100, 36)
        self.btn_prev.clicked.connect(self._prev)

        self.lbl_counter = QLabel("0 / 0")
        self.lbl_counter.setObjectName("counterLabel")
        self.lbl_counter.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.btn_next = QPushButton("Next →")
        self.btn_next.setObjectName("secondaryBtn")
        self.btn_next.setFixedSize(100, 36)
        self.btn_next.clicked.connect(self._next)

        nav.addWidget(self.btn_prev)
        nav.addStretch()
        nav.addWidget(self.lbl_counter)
        nav.addStretch()
        nav.addWidget(self.btn_next)
        root.addLayout(nav)

        # ── Manual-pass checkbox ──
        chk_frame = QFrame()
        chk_frame.setObjectName("card")
        chk_frame.setFixedHeight(52)
        chk_layout = QHBoxLayout(chk_frame)
        chk_layout.setContentsMargins(20, 0, 20, 0)
        self.chk_pass = QCheckBox("수동 테스트 결과 Pass 시 체크")
        self.chk_pass.stateChanged.connect(self._on_check_changed)
        chk_layout.addWidget(self.chk_pass)
        root.addWidget(chk_frame)

        # ── Detail info card ──
        detail_card = QFrame()
        detail_card.setObjectName("card")
        detail_layout = QVBoxLayout(detail_card)
        detail_layout.setContentsMargins(20, 16, 20, 16)
        detail_layout.setSpacing(10)

        grid = QGridLayout()
        grid.setSpacing(8)
        grid.setColumnMinimumWidth(0, 185)
        grid.setColumnStretch(1, 1)

        FIELDS = [
            ("TC ID",              "name"),
            ("Result",             "status"),
            ("Actual Result",      "content"),
            ("Middle Category",    "middle_category"),
            ("Small Category",     "small_category"),
            ("Detail Function",    "detail_function"),
            ("Test Objective",     "test_objectives"),
            ("Test Procedure",     "test_procedure"),
            ("Input Specification","input_specification"),
            ("Pre-condition",      "pre_condition"),
            ("Expected Result",    "expected_result"),
        ]

        self._field_widgets = {}
        for row, (label_text, key) in enumerate(FIELDS):
            lbl = QLabel(label_text)
            lbl.setStyleSheet("color: #334155; font-size: 12px; font-weight: 700;")
            lbl.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
            grid.addWidget(lbl, row, 0)

            if key == "content":
                widget = QTextEdit()
                widget.setReadOnly(True)
                widget.setMinimumHeight(80)
                widget.setMaximumHeight(120)
                widget.setStyleSheet("font-size: 13px;")
                row_layout = QHBoxLayout()
                row_layout.setSpacing(8)
                row_layout.addWidget(widget, stretch=1)
                self.btn_copy = QPushButton("복사")
                self.btn_copy.setObjectName("secondaryBtn")
                self.btn_copy.setFixedSize(60, 32)
                self.btn_copy.clicked.connect(self._copy_content)
                row_layout.addWidget(self.btn_copy, alignment=Qt.AlignmentFlag.AlignTop)
                container = QWidget()
                container.setLayout(row_layout)
                grid.addWidget(container, row, 1)
            else:
                widget = QLabel()
                widget.setWordWrap(True)
                widget.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
                widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
                grid.addWidget(widget, row, 1)

            self._field_widgets[key] = widget

        scroll_detail = QScrollArea()
        scroll_detail.setWidgetResizable(True)
        inner = QWidget()
        inner.setLayout(grid)
        scroll_detail.setWidget(inner)
        detail_layout.addWidget(scroll_detail)
        root.addWidget(detail_card, stretch=1)

        # ── Bottom buttons ──
        media_row = QHBoxLayout()
        self.btn_screenshot = QPushButton("📷 스크린샷 확인")
        self.btn_screenshot.setObjectName("accentBtn")
        self.btn_screenshot.setFixedHeight(44)
        self.btn_screenshot.clicked.connect(self._open_screenshot)

        self.btn_video = QPushButton("📹 영상 확인")
        self.btn_video.setObjectName("accentBtn")
        self.btn_video.setFixedHeight(44)
        self.btn_video.clicked.connect(self._open_video)

        media_row.addWidget(self.btn_screenshot)
        media_row.addWidget(self.btn_video)
        root.addLayout(media_row)

        btn_save = QPushButton("💾  저장 및 닫기")
        btn_save.setFixedHeight(48)
        btn_save.clicked.connect(self._on_save)
        root.addWidget(btn_save)

    # ── Data Loading ──────────────────────────────────────────────────────────

    def _load_item(self):
        if not self.current_category or not self.failed_data:
            return
        items = self.failed_data[self.current_category]
        if not items:
            return
        item = items[self.current_index]
        tc_id = item["name"]
        status = item["status"]
        tc_info = self.tc_data.get(tc_id, {})

        self.lbl_counter.setText(f"{self.current_index + 1} / {len(items)}")

        # Update checkbox without triggering signal
        self.chk_pass.blockSignals(True)
        self.chk_pass.setChecked(self.check_states[self.current_category][self.current_index])
        self.chk_pass.blockSignals(False)

        # Status color
        color = STATUS_COLORS.get(status, "#1e293b")

        self._field_widgets["name"].setText(tc_id)
        self._field_widgets["name"].setStyleSheet("color: #1e293b; font-weight: 700;")

        status_lbl = self._field_widgets["status"]
        status_lbl.setText(status)
        status_lbl.setStyleSheet(f"color: {color}; font-weight: 700; font-size: 14px;")

        content = item.get("content", "")
        content_widget = self._field_widgets["content"]
        content_widget.setPlainText(content)
        content_widget.setStyleSheet(f"font-size: 13px; color: {color};")

        for key in ["middle_category", "small_category", "detail_function",
                    "test_objectives", "test_procedure", "input_specification",
                    "pre_condition", "expected_result"]:
            self._field_widgets[key].setText(tc_info.get(key, "N/A"))

        # Nav buttons
        self.btn_prev.setEnabled(self.current_index > 0)
        self.btn_next.setEnabled(self.current_index < len(items) - 1)

        # Screenshot button
        self._screenshot_data = item.get("screenshot_file")
        self.btn_screenshot.setEnabled(bool(self._screenshot_data))

    # ── Interactions ──────────────────────────────────────────────────────────

    def _on_os_changed(self, choice):
        if choice and choice != self.current_category:
            self.current_category = choice
            self.current_index = 0
            self._load_item()

    def _prev(self):
        if self.current_index > 0:
            self.current_index -= 1
            self._load_item()

    def _next(self):
        items = self.failed_data.get(self.current_category, [])
        if self.current_index < len(items) - 1:
            self.current_index += 1
            self._load_item()

    def _on_check_changed(self, state):
        if self.current_category in self.check_states:
            self.check_states[self.current_category][self.current_index] = (
                state == Qt.CheckState.Checked.value
            )

    def _copy_content(self):
        items = self.failed_data.get(self.current_category, [])
        if not items:
            return
        text = items[self.current_index].get("content", "")
        if text:
            QApplication.clipboard().setText(text)
            self.btn_copy.setText("✅")
            QTimer.singleShot(2000, lambda: self.btn_copy.setText("복사"))

    def _open_screenshot(self):
        if not self._screenshot_data:
            return
        dlg = ScreenshotDialog(self._screenshot_data, self)
        dlg.exec()

    def _open_video(self):
        items = self.failed_data.get(self.current_category, [])
        if not items:
            return
        tc_id = items[self.current_index]["name"]
        video_path = os.path.join(
            cv.base_log_path, self.current_category, tc_id, "recording.mp4"
        )
        if not os.path.exists(video_path):
            QMessageBox.critical(self, "파일 없음", f"영상 파일을 찾을 수 없습니다.\n{video_path}")
            return
        if not hasattr(os, "startfile"):
            QMessageBox.critical(self, "에러", "이 환경에서는 영상을 직접 열 수 없습니다.")
            return
        try:
            os.startfile(video_path)
        except Exception as e:
            QMessageBox.critical(self, "에러", f"영상을 여는 중 오류가 발생했습니다:\n{e}")

    # ── Save ──────────────────────────────────────────────────────────────────

    def _on_save(self):
        reply = QMessageBox.question(
            self, "Fail reviewer 종료 알림",
            "테스트 결과를 이대로 저장하시겠습니까?",
            QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel,
        )
        if reply != QMessageBox.StandardButton.Ok:
            return

        reviewed_data, modified_parsed = self._compute_results()
        self.review_complete.emit(reviewed_data, modified_parsed)

    def _compute_results(self):
        final_output = copy.deepcopy(self.result_cases)
        removed_contents_map = {}

        for category, items in final_output.items():
            if category not in self.check_states:
                continue
            fail_idx = 0
            filtered = []
            removed_contents_map[category] = []

            for item in items:
                status = item.get("status")
                if status in _FAIL_STATUSES:
                    is_checked = self.check_states[category][fail_idx]
                    item["is_reviewed"] = is_checked
                    fail_idx += 1
                if status == "Minor_Fail" and item.get("is_reviewed"):
                    removed_contents_map[category].append(item.get("content"))
                    continue
                filtered.append(item)
            final_output[category] = filtered

        modified = copy.deepcopy(self.parsed_results)
        for category, removed in removed_contents_map.items():
            if category in modified and "test_cases" in modified[category]:
                orig = modified[category]["test_cases"]
                new_cases = [c for c in orig if c.get("error_msg") not in removed]
                modified[category]["minor_fail"] -= len(orig) - len(new_cases)
                modified[category]["test_cases"] = new_cases

        return final_output, modified
