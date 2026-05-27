import os
import subprocess

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTreeWidget, QTreeWidgetItem, QMessageBox, QFrame
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
        self._refresh_devices()
        self.timer.start(2000)

    def stop_monitoring(self):
        self.timer.stop()

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
        desc.setStyleSheet("color: #6c7086; font-size: 13px;")
        layout.addWidget(desc)

        # Device tree
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Serial Number", "Model", "Android Ver", "Status"])
        self.tree.setColumnWidth(0, 200)
        self.tree.setColumnWidth(1, 220)
        self.tree.setColumnWidth(2, 120)
        self.tree.setColumnWidth(3, 120)
        self.tree.setRootIsDecorated(False)
        self.tree.setAlternatingRowColors(False)
        layout.addWidget(self.tree)

        # Status label
        self.lbl_status = QLabel("기기를 검색 중...")
        self.lbl_status.setStyleSheet("color: #6c7086; font-size: 12px;")
        layout.addWidget(self.lbl_status)

        # Button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.btn_start = QPushButton("자동화 테스트 구동 시작")
        self.btn_start.setFixedSize(260, 50)
        self.btn_start.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_start.clicked.connect(self._on_start_clicked)
        btn_layout.addWidget(self.btn_start)
        layout.addLayout(btn_layout)

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
                item.setForeground(3, QColor("#a6e3a1"))
            else:
                item.setForeground(3, QColor("#f38ba8"))
            self.tree.addTopLevelItem(item)

        count = sum(1 for v in self.device_cache.values() if v["status"] == "device")
        self.lbl_status.setText(f"연결된 기기: {count}대")

    def _on_start_clicked(self):
        collected = [
            (serial, info["version"])
            for serial, info in self.device_cache.items()
            if info["status"] == "device"
        ]
        if not collected:
            QMessageBox.warning(self, "경고", "연결된 기기가 없습니다.")
            return

        for serial, version in collected:
            version_key = version.split(".")[0]
            os_name = cv.os_version_dic.get(version_key, version_key)
            model = self.device_cache.get(serial, {}).get("model", "Unknown")
            cv.device_model_map[os_name] = model

        self.stop_monitoring()
        self.devices_confirmed.emit(collected)
