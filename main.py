import os
import sys
import multiprocessing
# ==========================================
# 1. 외부 스크립트 하위 호환성 패치 (가장 먼저 실행)
# ==========================================
import customtkinter as tk
import api.actions
from email_feature.email_controller import process_email_form
from report.report_controller import process_test_report

sys.modules['main'] = api.actions
# ==========================================
# 2. 분리된 내부 모듈들 Import
# ==========================================

from config import common_variable
from ui.device_selector import get_connected_devices_gui
from ui.progress_view import MatrixDashboard
from core.test_runner import run_device_process, get_testcases
from ui.mode_selector import ExecutionModeSelector

def setup_log_directory():
    """테스트 결과 로그를 저장할 디렉토리를 셋업합니다."""
    if not os.path.exists(common_variable.base_log_path):
        os.makedirs(common_variable.base_log_path)
    else:
        for num in range(100):
            new_path = f"{common_variable.base_log_path}_{num + 2}"
            if not os.path.exists(new_path):
                common_variable.base_log_path = new_path
                common_variable.log_path = f"{common_variable.log_path}_{num + 2}"
                os.makedirs(common_variable.base_log_path)
                break
    return common_variable.base_log_path


def run_test():
    print("=== ATRA 자동화 테스트 프레임워크 시작 ===")
    # 1. 로그 폴더 초기화
    log_dir = setup_log_directory()
    # 2. 기기 연결 확인 및 선택
    device_list = get_connected_devices_gui()
    if not device_list:
        print("선택된 기기가 없습니다. 프로그램을 종료합니다.")
        return
    # 3. 실행할 테스트 케이스 로드
    script_list = get_testcases()
    if not script_list:
        print("실행할 테스트 케이스(TC)가 없습니다.")
        return
    # 4. 멀티프로세싱 상태 공유 자원 세팅
    manager = multiprocessing.Manager()
    shared_status = manager.dict()
    processes = []
    BASE_PORT = 4723
    # 5. 기기별 병렬 프로세스 실행 (Appium 서버 + 테스트 스크립트 실행)
    for idx, (udid, os_version) in enumerate(device_list):
        port = BASE_PORT + (idx * 2)
        p = multiprocessing.Process(
            target=run_device_process,
            args=(udid, port, os_version, log_dir, shared_status)
        )
        p.daemon = True
        p.start()
        processes.append(p)
    # 6. 실시간 UI 대시보드 렌더링

    root = tk.CTk()
    for i in range(len(device_list) + 1):
        root.grid_columnconfigure(i, weight=1)
    MatrixDashboard(root, device_list, script_list, shared_status, processes)
    try:
        root.mainloop()  # UI 창이 닫힐 때까지 여기서 대기
    except KeyboardInterrupt:
        pass
    # ==========================================
    # UI 종료 후 (테스트 완료 또는 강제 종료 시)
    # ==========================================
    print("\n=== 테스트 종료: 결과 분석 및 리포트 생성 중 ===")
    # 7. HTML 결과 리포트 분석 및 생성
    analyze_existing_logs(log_dir)




def analyze_existing_logs(selected_log_path):
    common_variable.base_log_path = selected_log_path
    html_content, html_path = process_test_report()
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    absolute_html_path = os.path.abspath(html_path)

    process_email_form(absolute_html_path)



def maintenance_script():


    return


def main():
    selector = ExecutionModeSelector()
    mode, selected_log_path = selector.show_and_get_mode()
    if mode is None:
        return
    elif mode == 1:
        run_test()
    elif mode == 2:
        analyze_existing_logs(selected_log_path)
    elif mode == 3:
        maintenance_script()



if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
