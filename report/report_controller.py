import os
import subprocess
import customtkinter as ctk
import config.common_variable as cv
from report.log_analyzer import parse_result_file
from report.html_builder import generate_html_report, get_screenshot_info
from report.tc_parser import load_all_tc_data
from ui.add_plm_info import PLMUpdaterApp
from ui.fail_reviewer import MultiCategoryFailViewer


def get_device_info():
    """common_variable에 저장된 시리얼로 기기 모델명을 직접 ADB로 조회"""
    return cv.device_model_map

def process_test_report():
    # 1. 파일 경로 확인 및 로그 파싱 (log_analyzer 사용)
    plm_differ = None
    parsed_results = {}
    html_path = f"{cv.base_log_path}/test_result.html"
    if os.path.exists(html_path):
        os.remove(html_path)
    os_list = [d for d in os.listdir(cv.base_log_path) if os.path.isdir(os.path.join(cv.base_log_path, d))]
    if "BOS" in os_list and os_list[0] == "BOS":
        os_list.remove("BOS")
        os_list.append("BOS")
    if "COS" in os_list and os_list[0] == "COS":
        os_list.remove("COS")
        os_list.append("COS")
    for single_os in os_list:
        if single_os.endswith("exe"):
            continue
        result_file = f"{cv.base_log_path}/{single_os}/log.txt"
        if not os.path.exists(result_file):
            print(f"[{single_os}] log 파일이 존재하지 않아 분석에서 제외합니다.")
            continue
        result = parse_result_file(result_file)
        parsed_results[single_os] = result
    # 2. 결과 데이터 1차 가공 및 스크린샷 매핑 (기존 html_builder 에서 이동)
    total_result = {
        'total': 0, 'pass': 0, 'fail': 0, 'minor_fail': 0,
        'na': 0, 'nt': 0, 'no_run': 0, 'error': 0,
        'result_cases': {}
    }
    for key, value in parsed_results.items():
        result_cases = []
        for case in value['test_cases']:
            status = case['status']
            screenshot_file = ""
            content = ""
            if status == 'Pass':
                pass
            elif status == 'Fail':
                screenshot = f"{cv.base_log_path}/{key}/{case['name']}/screenshot.png"
                if os.path.exists(screenshot):
                    screenshot_file = get_screenshot_info(screenshot)
                content = case['error_msg']
                status = 'FAIL'
            elif status == 'Minor_Fail':
                screenshot = f"{cv.base_log_path}/{key}/{case['name']}/{case['screenshot_folder']}/screenshot.png"
                if os.path.exists(screenshot):
                    screenshot_file = get_screenshot_info(screenshot)
                content = case['error_msg']
            elif status in ['N/T', 'N/A', 'Error']:
                content = case['error_msg']
                screenshot_file = case.get('screenshot_file', '')
            result_cases.append({
                'name': case['name'],
                'execution_time': case['execution_time'],
                'content': content,
                'screenshot_file': screenshot_file,
                'status': status
            })
        total_result['result_cases'][key] = result_cases
    # 3. Fail 데이터 확인 및 UI 팝업 실행 결정 (기존 html_builder 에서 이동)
    has_fail = False
    for cat, items in total_result['result_cases'].items():
        if any(item.get("status") in ["FAIL", "Minor_Fail", "N/A", "Error"] for item in items):
            has_fail = True
            break
    plm_info = {}
    test_case_data = load_all_tc_data()
    # 팝업 UI 실행 및 사용자가 수정한 데이터 받아오기
    if has_fail:
        root = ctk.CTk()
        app = MultiCategoryFailViewer(root, total_result['result_cases'], test_case_data)
        root.mainloop()
        reviewed_data, reviewed_results = app.get_reviewed_results(parsed_results)
        # 4. 재집계 로직 (기존 html_builder 에서 이동)
        for key, value in reviewed_results.items():
            for stat in ['total', 'pass', 'fail', 'minor_fail', 'na', 'nt', 'no_run', 'error']:
                total_result[stat] += value[stat]
        for cat, items in reviewed_data.items():
            for item in items:
                status = item['status']
                reviewed = item.get('is_reviewed', 'Key Not Found')
                if reviewed and reviewed != "Key Not Found":
                    if status == "FAIL":
                        reviewed_results[cat]['pass'] += 1
                        reviewed_results[cat]['fail'] -= 1
                        total_result['pass'] += 1
                        total_result['fail'] -= 1
                    elif status == "Minor_Fail":
                        reviewed_results[cat]['minor_fail'] -= 1
                        total_result['minor_fail'] -= 1
                    elif status == "N/A":
                        reviewed_results[cat]['pass'] += 1
                        reviewed_results[cat]['na'] -= 1
                        total_result['pass'] += 1
                        total_result['na'] -= 1
                    elif status == "Error":
                        reviewed_results[cat]['pass'] += 1
                        reviewed_results[cat]['error'] -= 1
                        total_result['pass'] += 1
                        total_result['error'] -= 1
                elif not reviewed and reviewed != "Key Not Found":
                    if status == "Error":
                        reviewed_results[cat]['fail'] += 1
                        reviewed_results[cat]['error'] -= 1
                        total_result['fail'] += 1
                        total_result['error'] -= 1
            denom = reviewed_results[cat]['total'] - reviewed_results[cat]['nt']
            reviewed_results[cat]['pass_rate'] = round((reviewed_results[cat]['pass'] / denom * 100), 2) if denom > 0 else 0
        denom_total = total_result['total'] - total_result['nt']
        total_result['pass_rate'] = round((total_result['pass'] / denom_total * 100), 2) if denom_total > 0 else 0
        # PLM 팝업 실행 로직
        breaker = False
        for key, value in reviewed_data.items():
            for result in value:
                if result["status"] not in ["Pass", "N/T"] and result["is_reviewed"] == False:
                    app = PLMUpdaterApp(reviewed_data)
                    app.mainloop()
                    reviewed_data, plm_differ = app.get_data()
                    total_result['fail'] += plm_differ['total']["FAIL"]
                    total_result['na'] += plm_differ['total']["N/A"]
                    for os_ver in plm_differ:
                        if os_ver != "total":
                            try:
                                reviewed_results[os_ver]['fail'] += plm_differ[os_ver]["FAIL"]
                                reviewed_results[os_ver]['na'] += plm_differ[os_ver]["N/A"]
                                plm_info[os_ver] = plm_differ[os_ver]["issue"]
                            except KeyError:
                                pass
                    breaker = True
                    break
            if breaker:
                break
    else:
        root = ctk.CTk()
        app = MultiCategoryFailViewer(root, total_result['result_cases'], test_case_data)
        reviewed_data, reviewed_results = app.get_reviewed_results(parsed_results)
        for key, value in reviewed_results.items():
            for stat in ['total', 'pass', 'fail', 'minor_fail', 'na', 'nt', 'no_run', 'error']:
                total_result[stat] += value[stat]
        total_result['pass_rate'] = 100

    comment_info = {
        "SOS": {"N/A":[], "N/T":[]},
        "TOS": {"N/A":[], "N/T":[]},
        "UOS": {"N/A":[], "N/T":[]},
        "VOS": {"N/A":[], "N/T":[]},
        "BOS": {"N/A":[], "N/T":[]},
        "COS": {"N/A":[], "N/T":[]}
    }

    for key, value in reviewed_data.items():
        if plm_differ is not None:
            comment_info[key]["N/A"] = plm_differ[key]["comment"]
        for single_tc in reviewed_data[key]:
            if single_tc['status'] == "N/T":
                comment_info[key]["N/T"].append(f" - {single_tc['content']}")

    device_info = get_device_info()

    # 5. 모든 재계산이 완료된 순수 데이터를 HTML 생성기에 전달!
    html_content = generate_html_report(
        total_result=total_result,
        reviewed_data=reviewed_data,
        reviewed_results=reviewed_results,
        plm_info=plm_info,
        test_case_data=test_case_data,
        comment_info=comment_info,
        device_info=device_info
    )
    return html_content, html_path

