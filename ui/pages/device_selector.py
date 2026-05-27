import os
import subprocess
from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTreeWidget, QTreeWidgetItem, QMessageBox, QFrame, QLineEdit,
    QFileDialog
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QColor

import config.common_variable as cv


class DeviceSelectorPage(QWidget):
    devices_confirmed = pyqtSignal(list)  # [(udid, version), ...]

    def __init__(self):
        super().__init__()
        self.device_cache = {}
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._refresh_devices)
        self._setup_ui()

    def start_monitoring(self):
        # 화면에 진입할 때마다 현재 cv 값으로 경로 표시 갱신
        self.lbl_path.setText(cv.base_log_path)
        self._refresh_devices()
        self.timer.start(2000)

    def stop_monitoring(self):
        self.timer.stop()

    # ── UI ────────────────────────────────────────────────────────────────────

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        # Header
        header = QLabel("기기 선택")
        header.setObjectName("pageTitle")
        layout.addWidget(header)

        desc = QLabel("ADB로 연결된 기기가 자동으로 표시됩니다. 테스트를 시작하면 연결된 모든 기기에서 병렬로 실행됩니다.")
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #475569; font-size: 13px;")
        layout.addWidget(desc)

        # Device tree
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Serial Number", "Model", "Android Ver", "Status"])
        self.tree.setColumnWidth(0, 200)
        self.tree.setColumnWidth(1, 240)
        self.tree.setColumnWidth(2, 130)
        self.tree.setColumnWidth(3, 120)
        self.tree.setRootIsDecorated(False)
        self.tree.setAlternatingRowColors(False)
        layout.addWidget(self.tree)

        # Status label
        self.lbl_status = QLabel("기기를 검색 중...")
        self.lbl_status.setStyleSheet("color: #475569; font-size: 12px;")
        layout.addWidget(self.lbl_status)

        # ── 로그 저장 경로 ──
        path_card = QFrame()
        path_card.setObjectName("infoCard")
        path_layout = QVBoxLayout(path_card)
        path_layout.setContentsMargins(16, 12, 16, 12)
        path_layout.setSpacing(8)

        path_title = QLabel("로그 저장 경로")
        path_title.setStyleSheet("color: #334155; font-size: 12px; font-weight: 700;")
        path_layout.addWidget(path_title)

        path_row = QHBoxLayout()
        path_row.setSpacing(10)

        self.lbl_path = QLabel(cv.base_log_path)
        self.lbl_path.setWordWrap(False)
        self.lbl_path.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.lbl_path.setStyleSheet(
            "color: #334155; font-size: 12px; "
            "background-color: #f1f5f9; border: 1px solid #e2e8f0; "
            "border-radius: 6px; padding: 6px 10px;"
        )
        path_row.addWidget(self.lbl_path, stretch=1)

        btn_change = QPushButton("변경...")
        btn_change.setObjectName("secondaryBtn")
        btn_change.setFixedSize(110, 38)
        btn_change.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_change.clicked.connect(self._change_log_path)
        path_row.addWidget(btn_change)

        path_layout.addLayout(path_row)

        self.lbl_path_warn = QLabel("")
        self.lbl_path_warn.setStyleSheet("color: #dc2626; font-size: 11px;")
        path_layout.addWidget(self.lbl_path_warn)

        layout.addWidget(path_card)

        # Start button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.btn_start = QPushButton("자동화 테스트 구동 시작")
        self.btn_start.setFixedSize(260, 50)
        self.btn_start.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_start.clicked.connect(self._on_start_clicked)
        btn_layout.addWidget(self.btn_start)
        layout.addLayout(btn_layout)

    # ── Log path change ───────────────────────────────────────────────────────

    def _change_log_path(self):
        folder = QFileDialog.getExistingDirectory(
            self, "로그를 저장할 기본 폴더를 선택하세요"
        )
        if not folder:
            return

        date_suffix = datetime.now().strftime("%m%d")
        new_base = f"{folder}/ATRA_{date_suffix}"

        cv.base_log_path = new_base
        cv.log_path = new_base
        self.lbl_path.setText(new_base)
        self.lbl_path_warn.setText("")

    # ── ADB helpers ───────────────────────────────────────────────────────────

    @staticmethod
    def _run_adb(command):
        try:
            kwargs = {}
            if os.name == "nt":
                si = subprocess.STARTUPINFO()
                si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                kwargs["startupinfo"] = si
            return subprocess.check_output(
                command, shell=True, stderr=subprocess.STDOUT, **kwargs
            ).decode("utf-8").strip()
        except Exception:
            return None

    def _get_device_detail(self, serial):
        model = self._run_adb(f"adb -s {serial} shell getprop ro.product.model")
        version = self._run_adb(f"adb -s {serial} shell getprop ro.build.version.release")
        return {
            "model": model or "Unknown",
            "version": version or "?",
        }

    # ── Device polling ────────────────────────────────────────────────────────

    def _refresh_devices(self):
        raw = self._run_adb("adb devices")
        if not raw:
            return

        lines = raw.split("\n")[1:]
        current_serials = []

        for line in lines:
            if not line.strip():
                continue
            parts = line.split()
            if len(parts) < 2:
                continue
            serial, status = parts[0], parts[1]
            current_serials.append(serial)

            if serial not in self.device_cache:
                if status == "device":
                    detail = self._get_device_detail(serial)
                    self.device_cache[serial] = {
                        "model": detail["model"],
                        "version": detail["version"],
                        "status": status,
                    }
                else:
                    self.device_cache[serial] = {"model": "-", "version": "-", "status": status}
            else:
                prev_status = self.device_cache[serial]["status"]
                self.device_cache[serial]["status"] = status
                # unauthorized → device 전환 시 모델/버전 재조회
                if status == "device" and prev_status != "device":
                    detail = self._get_device_detail(serial)
                    self.device_cache[serial]["model"] = detail["model"]
                    self.device_cache[serial]["version"] = detail["version"]

        for s in [k for k in self.device_cache if k not in current_serials]:
            del self.device_cache[s]

        self._update_tree()

    def _update_tree(self):
        self.tree.clear()
        sorted_cache = sorted(
            self.device_cache.items(),
            key=lambda x: int(x[1]["version"].split(".")[0])
            if x[1]["version"].split(".")[0].isdigit()
            else 99,
        )
        for serial, info in sorted_cache:
            item = QTreeWidgetItem([serial, info["model"], info["version"], info["status"]])
            item.setTextAlignment(0, Qt.AlignmentFlag.AlignCenter)
            item.setTextAlignment(1, Qt.AlignmentFlag.AlignCenter)
            item.setTextAlignment(2, Qt.AlignmentFlag.AlignCenter)
            item.setTextAlignment(3, Qt.AlignmentFlag.AlignCenter)
            if info["status"] == "device":
                item.setForeground(3, QColor("#16a34a"))
            else:
                item.setForeground(3, QColor("#dc2626"))
            self.tree.addTopLevelItem(item)

        count = sum(1 for v in self.device_cache.values() if v["status"] == "device")
        self.lbl_status.setText(f"연결된 기기: {count}대")

    # ── Start ─────────────────────────────────────────────────────────────────

    def _on_start_clicked(self):
        collected = [
            (serial, info["version"])
            for serial, info in self.device_cache.items()
            if info["status"] == "device"
        ]
        if not collected:
            QMessageBox.warning(self, "경고", "연결된 기기가 없습니다.")
            return

        # 경로 접근 가능 여부 사전 확인
        parent = os.path.dirname(cv.base_log_path)
        if parent and not os.path.exists(parent):
            self.lbl_path_warn.setText(
                f"⚠  경로에 접근할 수 없습니다. '변경...' 버튼으로 로컬 경로를 선택해 주세요."
            )
            QMessageBox.warning(
                self, "경로 접근 불가",
                f"로그 저장 경로에 접근할 수 없습니다.\n\n"
                f"경로: {cv.base_log_path}\n\n"
                f"'변경...' 버튼을 눌러 로컬 경로로 변경해 주세요."
            )
            return

        self.lbl_path_warn.setText("")

        for serial, version in collected:
            version_key = version.split(".")[0]
            os_name = cv.os_version_dic.get(version_key, version_key)
            model = self.device_cache.get(serial, {}).get("model", "Unknown")
            cv.device_model_map[os_name] = model

        self.stop_monitoring()
        self.devices_confirmed.emit(collected)
