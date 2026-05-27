import os

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFileDialog, QMessageBox, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont


class ModeSelectorPage(QWidget):
    mode_selected = pyqtSignal(int, str)  # (mode, log_path)

    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(60, 60, 60, 60)
        layout.setSpacing(0)

        layout.addStretch(2)

        # Logo / Title
        title = QLabel("ATRA")
        title.setObjectName("appTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("ANDROID TEST REPORT AUTOMATION")
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)

        layout.addSpacing(60)

        # Buttons
        btn_test = QPushButton("자동화 테스트 실행")
        btn_test.setFixedSize(340, 56)
        btn_test.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_test.clicked.connect(lambda: self.mode_selected.emit(1, ""))

        btn_report = QPushButton("기존 로그로 리포트 생성")
        btn_report.setFixedSize(340, 56)
        btn_report.setObjectName("secondaryBtn")
        btn_report.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_report.clicked.connect(self._select_log)

        btn_maintenance = QPushButton("스크립트 유지보수 (미구현)")
        btn_maintenance.setFixedSize(340, 56)
        btn_maintenance.setObjectName("secondaryBtn")
        btn_maintenance.setEnabled(False)

        for btn in (btn_test, btn_report, btn_maintenance):
            layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)
            layout.addSpacing(12)

        layout.addStretch(3)

    def _select_log(self):
        selected_dir = QFileDialog.getExistingDirectory(
            self, "리포트를 생성할 기존 로그 폴더를 선택하세요"
        )
        if not selected_dir:
            return
        html_path = os.path.join(selected_dir, "test_result.html")
        if os.path.exists(html_path):
            reply = QMessageBox.question(
                self, "리포트 삭제 주의 알림",
                "기존 리포트가 삭제됩니다. 그대로 진행하시겠습니까?",
                QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel
            )
            if reply != QMessageBox.StandardButton.Ok:
                return
        self.mode_selected.emit(2, selected_dir)
