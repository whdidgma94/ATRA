from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QFrame, QScrollArea
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QColor, QFont

from ui.theme import CELL_BG, CELL_FG

_POLL_MS = 500


class TestProgressPage(QWidget):
    test_finished = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.manager_dict = None
        self.devices = []
        self.scripts = []
        self.process_list = []
        self.cells = {}
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._poll)
        self._setup_ui()

    def setup_test(self, devices, scripts, shared_status, processes):
        self.devices = devices
        self.scripts = scripts
        self.manager_dict = shared_status
        self.process_list = processes
        self._build_table()
        self.btn_finish.setEnabled(False)
        self.btn_finish.setText("테스트 진행 중...")
        self.timer.start(_POLL_MS)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(16)

        # Header row
        header_row = QHBoxLayout()
        title = QLabel("테스트 진행 현황")
        title.setObjectName("pageTitle")
        header_row.addWidget(title)
        header_row.addStretch()

        self.btn_stop = QPushButton("테스트 강제 종료")
        self.btn_stop.setObjectName("dangerBtn")
        self.btn_stop.setFixedSize(160, 40)
        self.btn_stop.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_stop.clicked.connect(self._on_force_stop)
        header_row.addWidget(self.btn_stop)

        self.btn_finish = QPushButton("리포트 생성")
        self.btn_finish.setObjectName("successBtn")
        self.btn_finish.setFixedSize(160, 40)
        self.btn_finish.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_finish.clicked.connect(self._on_finish)
        header_row.addWidget(self.btn_finish)

        layout.addLayout(header_row)

        # Legend
        legend_row = QHBoxLayout()
        legend_row.setSpacing(16)
        for label, color in [
            ("Pending", "#45475a"), ("Running", "#f9e2af"),
            ("Pass", "#a6e3a1"), ("Fail", "#f38ba8"),
            ("Error", "#fab387"), ("N/T", "#89dceb"), ("N/A", "#a6adc8"),
        ]:
            dot = QLabel("●")
            dot.setStyleSheet(f"color: {color}; font-size: 16px;")
            lbl = QLabel(label)
            lbl.setStyleSheet("color: #6c7086; font-size: 12px;")
            legend_row.addWidget(dot)
            legend_row.addWidget(lbl)
        legend_row.addStretch()
        layout.addLayout(legend_row)

        # Table container (scrollable)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self.table = QTableWidget(0, 0)
        self.table.horizontalHeader().setMinimumSectionSize(100)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        scroll.setWidget(self.table)
        layout.addWidget(scroll)

        # Status bar
        self.lbl_stat = QLabel("대기 중...")
        self.lbl_stat.setStyleSheet("color: #6c7086; font-size: 12px;")
        layout.addWidget(self.lbl_stat)

    def _build_table(self):
        self.cells = {}
        self.table.clear()
        self.table.setRowCount(len(self.scripts))
        self.table.setColumnCount(len(self.devices) + 1)

        headers = ["TC Script"] + self.devices
        self.table.setHorizontalHeaderLabels(headers)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for col in range(1, len(self.devices) + 1):
            self.table.horizontalHeader().setSectionResizeMode(col, QHeaderView.ResizeMode.Fixed)
            self.table.setColumnWidth(col, 120)
        self.table.verticalHeader().setDefaultSectionSize(36)

        for row, script in enumerate(self.scripts):
            script_item = QTableWidgetItem(script)
            script_item.setForeground(QColor("#cdd6f4"))
            self.table.setItem(row, 0, script_item)

            for col, dev_id in enumerate(self.devices, start=1):
                cell = QTableWidgetItem("Pending")
                cell.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                cell.setBackground(QColor(CELL_BG["Pending"]))
                cell.setForeground(QColor(CELL_FG["Pending"]))
                self.table.setItem(row, col, cell)
                self.cells[(dev_id, script)] = cell

    def _poll(self):
        if self.manager_dict is None:
            return

        all_done = True
        total = pass_c = fail_c = 0

        for dev_id in self.devices:
            if dev_id not in self.manager_dict:
                all_done = False
                continue
            dev_status = self.manager_dict[dev_id]

            for script in self.scripts:
                status = dev_status.get(script, "Pending")
                if status in ("Pending", "Running"):
                    all_done = False

                cell = self.cells.get((dev_id, script))
                if cell:
                    bg = CELL_BG.get(status, "#45475a")
                    fg = CELL_FG.get(status, "#cdd6f4")
                    if cell.text() != status:
                        cell.setText(status)
                        cell.setBackground(QColor(bg))
                        cell.setForeground(QColor(fg))

                total += 1
                if status == "Pass":
                    pass_c += 1
                elif status in ("Fail", "Error"):
                    fail_c += 1

        done_c = pass_c + fail_c
        self.lbl_stat.setText(
            f"완료: {done_c} / {total}  |  Pass: {pass_c}  |  Fail/Error: {fail_c}"
        )

        if all_done and self.scripts:
            self.timer.stop()
            self.btn_finish.setEnabled(True)
            self.btn_finish.setText("✅ 테스트 완료 — 리포트 생성")
            self.btn_stop.setEnabled(False)

    def _on_force_stop(self):
        reply = QMessageBox.question(
            self, "테스트 종료 알림",
            "자동화 테스트를 강제 종료하시겠습니까?\n현재까지의 결과로 리포트를 생성합니다.",
            QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel,
        )
        if reply != QMessageBox.StandardButton.Ok:
            return
        self.timer.stop()
        for p in self.process_list:
            if p.is_alive():
                p.terminate()
        self.test_finished.emit()

    def _on_finish(self):
        self.test_finished.emit()
