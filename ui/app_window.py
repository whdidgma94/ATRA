import multiprocessing
import os

from PyQt6.QtWidgets import QMainWindow, QStackedWidget, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

import config.common_variable as cv
from ui.pages.mode_selector import ModeSelectorPage
from ui.pages.device_selector import DeviceSelectorPage
from ui.pages.test_progress import TestProgressPage
from ui.pages.fail_reviewer import FailReviewerPage
from ui.pages.plm_info import PLMInfoPage
from ui.pages.email_form import EmailFormPage


class AppWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ATRA — Android Test Report Automation")
        self.resize(1100, 750)
        self.setMinimumSize(800, 600)

        # ── Shared state ──
        self.device_list = []
        self.log_dir = ""
        self.processes = []
        self._mp_manager = None
        self.shared_status = None
        self.parsed_results = None
        self.result_cases = None
        self.test_case_data = None
        self.total_result = None
        self.reviewed_data = None
        self.reviewed_results = None
        self.plm_info = {}
        self.plm_differ = None

        # ── Pages ──
        self.page_mode = ModeSelectorPage()
        self.page_device = DeviceSelectorPage()
        self.page_progress = TestProgressPage()
        self.page_fail = FailReviewerPage()
        self.page_plm = PLMInfoPage()
        self.page_email = EmailFormPage()

        # ── Stack ──
        self.stack = QStackedWidget()
        for page in (
            self.page_mode, self.page_device, self.page_progress,
            self.page_fail, self.page_plm, self.page_email,
        ):
            self.stack.addWidget(page)
        self.setCentralWidget(self.stack)

        # ── Signals ──
        self.page_mode.mode_selected.connect(self._on_mode_selected)
        self.page_device.devices_confirmed.connect(self._on_devices_confirmed)
        self.page_progress.test_finished.connect(self._on_test_finished)
        self.page_fail.review_complete.connect(self._on_review_complete)
        self.page_plm.plm_complete.connect(self._on_plm_complete)

        self._goto(self.page_mode)

    # ── Navigation helper ─────────────────────────────────────────────────────

    def _goto(self, page):
        self.stack.setCurrentWidget(page)

    # ── Mode selector ─────────────────────────────────────────────────────────

    def _on_mode_selected(self, mode: int, log_path: str):
        if mode == 1:
            self._goto(self.page_device)
            self.page_device.start_monitoring()
        elif mode == 2:
            cv.base_log_path = log_path
            self._start_report_generation()

    # ── Device confirmed → start test ─────────────────────────────────────────

    def _on_devices_confirmed(self, device_list: list):
        self.device_list = device_list
        self.log_dir = self._setup_log_directory()
        if not self.log_dir:
            # 경로 생성 실패 — 오류 메시지는 _setup_log_directory에서 이미 표시
            return

        from core.test_runner import get_testcases, run_device_process
        from config.common_variable import os_version_dic

        script_list = get_testcases()
        if not script_list:
            QMessageBox.warning(self, "경고", "실행할 테스트 케이스(TC)가 없습니다.")
            return

        self._mp_manager = multiprocessing.Manager()
        self.shared_status = self._mp_manager.dict()
        self.processes = []

        BASE_PORT = 4723
        for idx, (udid, os_version) in enumerate(device_list):
            port = BASE_PORT + (idx * 2)
            p = multiprocessing.Process(
                target=run_device_process,
                args=(udid, port, os_version, self.log_dir, self.shared_status),
            )
            p.daemon = True
            p.start()
            self.processes.append(p)

        sorted_devices = sorted(
            device_list,
            key=lambda x: int(x[1].split(".")[0]) if x[1].split(".")[0].isdigit() else 99,
        )
        devices_display = [
            os_version_dic[d[1].split(".")[0]]
            for d in sorted_devices
            if d[1].split(".")[0] in os_version_dic
        ]

        self.page_progress.setup_test(
            devices_display, script_list, self.shared_status, self.processes
        )
        self._goto(self.page_progress)

    @staticmethod
    def _setup_log_directory() -> str:
        base = cv.base_log_path
        try:
            if not os.path.exists(base):
                os.makedirs(base)
                return base
            for num in range(100):
                new_path = f"{base}_{num + 2}"
                if not os.path.exists(new_path):
                    cv.base_log_path = new_path
                    cv.log_path = f"{cv.log_path}_{num + 2}"
                    os.makedirs(new_path)
                    return new_path
            return base
        except OSError as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(
                None, "로그 경로 생성 실패",
                f"로그 저장 폴더를 만들 수 없습니다.\n\n"
                f"경로: {base}\n"
                f"오류: {e}\n\n"
                f"기기 선택 화면의 '변경...' 버튼으로 로컬 경로를 선택해 주세요."
            )
            return ""

    # ── Test finished → parse logs ────────────────────────────────────────────

    def _on_test_finished(self):
        self._start_report_generation()

    def _start_report_generation(self):
        from report.report_controller import parse_report_data

        parsed, result_cases, tc_data, total = parse_report_data()
        self.parsed_results = parsed
        self.result_cases = result_cases
        self.test_case_data = tc_data
        self.total_result = total

        has_fail = any(
            item.get("status") in {"FAIL", "Minor_Fail", "N/A", "Error"}
            for items in result_cases.values()
            for item in items
        )

        if has_fail:
            self.page_fail.load_data(result_cases, tc_data, parsed)
            self._goto(self.page_fail)
        else:
            # No fails: aggregate directly and finalize
            import copy
            from report.report_controller import aggregate_results
            self.reviewed_data = copy.deepcopy(result_cases)
            self.reviewed_results = copy.deepcopy(parsed)
            aggregate_results(self.reviewed_results, self.reviewed_data, self.total_result)
            self.total_result["pass_rate"] = 100
            self._finalize_report(plm_differ=None)

    # ── Fail reviewer done ────────────────────────────────────────────────────

    def _on_review_complete(self, reviewed_data: dict, modified_parsed: dict):
        from report.report_controller import aggregate_results

        self.reviewed_data = reviewed_data
        self.reviewed_results = modified_parsed
        aggregate_results(modified_parsed, reviewed_data, self.total_result)

        has_remaining = any(
            item.get("status") not in {"Pass", "N/T"}
            and item.get("is_reviewed") is False
            for items in reviewed_data.values()
            for item in items
        )

        if has_remaining:
            self.page_plm.load_data(reviewed_data)
            self._goto(self.page_plm)
        else:
            self._finalize_report(plm_differ=None)

    # ── PLM info done ─────────────────────────────────────────────────────────

    def _on_plm_complete(self, updated_data: dict, plm_total: dict):
        self.reviewed_data = updated_data
        self.plm_differ = plm_total

        for os_ver, data in plm_total.items():
            if os_ver == "total":
                continue
            if os_ver in self.reviewed_results:
                self.reviewed_results[os_ver]["fail"] = (
                    self.reviewed_results[os_ver].get("fail", 0) + data.get("FAIL", 0)
                )
                self.reviewed_results[os_ver]["na"] = (
                    self.reviewed_results[os_ver].get("na", 0) + data.get("N/A", 0)
                )
            self.plm_info[os_ver] = data.get("issue", [])

        self.total_result["fail"] = (
            self.total_result.get("fail", 0) + plm_total["total"].get("FAIL", 0)
        )
        self.total_result["na"] = (
            self.total_result.get("na", 0) + plm_total["total"].get("N/A", 0)
        )

        self._finalize_report(plm_differ=plm_total)

    # ── Finalize: HTML → email ────────────────────────────────────────────────

    def _finalize_report(self, plm_differ):
        from report.report_controller import finalize_report
        from email_feature.process_report import generate_email_form

        # Build comment_info
        comment_info = {
            os_ver: {"N/A": [], "N/T": []}
            for os_ver in ["SOS", "TOS", "UOS", "VOS", "BOS", "COS"]
        }
        for key, items in self.reviewed_data.items():
            if plm_differ and key in plm_differ:
                comment_info.setdefault(key, {})["N/A"] = plm_differ[key].get("comment", [])
            for tc in items:
                if tc.get("status") == "N/T":
                    comment_info.setdefault(key, {}).setdefault("N/T", []).append(
                        f" - {tc.get('content', '')}"
                    )

        html_content, html_path = finalize_report(
            reviewed_data=self.reviewed_data,
            reviewed_results=self.reviewed_results,
            plm_info=self.plm_info,
            total_result=self.total_result,
            comment_info=comment_info,
            device_info=cv.device_model_map,
            test_case_data=self.test_case_data,
        )

        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        table_form = generate_email_form(os.path.abspath(html_path))
        self.page_email.load_data(table_form)
        self._goto(self.page_email)
