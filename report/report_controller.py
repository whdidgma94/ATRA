import os
import customtkinter as ctk
import config.common_variable as cv
from report.log_analyzer import parse_result_file
from report.html_builder import generate_html_report, get_screenshot_info
from report.tc_parser import load_all_tc_data
from ui.add_plm_info import PLMUpdaterApp
from ui.fail_reviewer import MultiCategoryFailViewer


def get_device_info():
    return cv.device_model_map


def _parse_logs():
    """로그 디렉토리를 순회하여 OS별 파싱 결과와 result_cases를 반환합니다."""
    parsed_results = {}
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
        parsed_results[single_os] = parse_result_file(result_file)

    result_cases = {}
    for key, value in parsed_results.items():
        cases = []
        for case in value['test_cases']:
            status = case['status']
            screenshot_file = ""
            content = ""
            if status == 'Fail':
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
            cases.append({
                'name': case['name'],
                'execution_time': case['execution_time'],
                'content': content,
                'screenshot_file': screenshot_file,
                'status': status
            })
        result_cases[key] = cases

    return parsed_results, result_cases


def _aggregate_results(reviewed_results, reviewed_data, total_result):
    """리뷰 결과를 total_result에 집계하고 pass_rate를 계산합니다."""
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


def _run_fail_review_ui(result_cases, parsed_results, test_case_data, total_result):
    """Fail 검토 UI → PLM 입력 UI를 실행하고 최종 reviewed_data, reviewed_results, plm_info를 반환합니다."""
    root = ctk.CTk()
    app = MultiCategoryFailViewer(root, result_cases, test_case_data)
    root.mainloop()
    reviewed_data, reviewed_results = app.get_reviewed_results(parsed_results)

    _aggregate_results(reviewed_results, reviewed_data, total_result)

    plm_info = {}
    plm_differ = None
    for key, value in reviewed_data.items():
        for result in value:
            if result["status"] not in ["Pass", "N/T"] and result["is_reviewed"] == False:
                plm_app = PLMUpdaterApp(reviewed_data)
                plm_app.mainloop()
                reviewed_data, plm_differ = plm_app.get_data()
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
                break
        else:
            continue
        break

    return reviewed_data, reviewed_results, plm_info, plm_differ


def process_test_report():
    html_path = f"{cv.base_log_path}/test_result.html"
    if os.path.exists(html_path):
        os.remove(html_path)

    parsed_results, result_cases = _parse_logs()
    test_case_data = load_all_tc_data()

    total_result = {
        'total': 0, 'pass': 0, 'fail': 0, 'minor_fail': 0,
        'na': 0, 'nt': 0, 'no_run': 0, 'error': 0,
        'result_cases': result_cases
    }

    has_fail = any(
        item.get("status") in ["FAIL", "Minor_Fail", "N/A", "Error"]
        for items in result_cases.values()
        for item in items
    )

    plm_differ = None
    if has_fail:
        reviewed_data, reviewed_results, plm_info, plm_differ = _run_fail_review_ui(
            result_cases, parsed_results, test_case_data, total_result
        )
    else:
        root = ctk.CTk()
        app = MultiCategoryFailViewer(root, result_cases, test_case_data)
        reviewed_data, reviewed_results = app.get_reviewed_results(parsed_results)
        for key, value in reviewed_results.items():
            for stat in ['total', 'pass', 'fail', 'minor_fail', 'na', 'nt', 'no_run', 'error']:
                total_result[stat] += value[stat]
        total_result['pass_rate'] = 100
        plm_info = {}

    comment_info = {
        "SOS": {"N/A": [], "N/T": []},
        "TOS": {"N/A": [], "N/T": []},
        "UOS": {"N/A": [], "N/T": []},
        "VOS": {"N/A": [], "N/T": []},
        "BOS": {"N/A": [], "N/T": []},
        "COS": {"N/A": [], "N/T": []}
    }
    for key in reviewed_data:
        if plm_differ is not None:
            comment_info[key]["N/A"] = plm_differ[key]["comment"]
        for single_tc in reviewed_data[key]:
            if single_tc['status'] == "N/T":
                comment_info[key]["N/T"].append(f" - {single_tc['content']}")

    html_content = generate_html_report(
        total_result=total_result,
        reviewed_data=reviewed_data,
        reviewed_results=reviewed_results,
        plm_info=plm_info,
        test_case_data=test_case_data,
        comment_info=comment_info,
        device_info=get_device_info()
    )
    return html_content, html_path
