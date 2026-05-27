import os

import config.common_variable as cv
from report.log_analyzer import parse_result_file
from report.html_builder import generate_html_report, get_screenshot_info
from report.tc_parser import load_all_tc_data


def get_device_info():
    return cv.device_model_map


def _parse_logs():
    parsed_results = {}
    os_list = [
        d for d in os.listdir(cv.base_log_path)
        if os.path.isdir(os.path.join(cv.base_log_path, d))
    ]
    # BOS / COS를 마지막으로 정렬
    for late_os in ("BOS", "COS"):
        if late_os in os_list and os_list[0] == late_os:
            os_list.remove(late_os)
            os_list.append(late_os)

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
        for case in value["test_cases"]:
            status = case["status"]
            screenshot_file = ""
            content = ""
            if status == "Fail":
                screenshot = f"{cv.base_log_path}/{key}/{case['name']}/screenshot.png"
                if os.path.exists(screenshot):
                    screenshot_file = get_screenshot_info(screenshot)
                content = case["error_msg"]
                status = "FAIL"
            elif status == "Minor_Fail":
                screenshot = (
                    f"{cv.base_log_path}/{key}/{case['name']}"
                    f"/{case['screenshot_folder']}/screenshot.png"
                )
                if os.path.exists(screenshot):
                    screenshot_file = get_screenshot_info(screenshot)
                content = case["error_msg"]
            elif status in ("N/T", "N/A", "Error"):
                content = case["error_msg"]
                screenshot_file = case.get("screenshot_file", "")
            cases.append(
                {
                    "name": case["name"],
                    "execution_time": case["execution_time"],
                    "content": content,
                    "screenshot_file": screenshot_file,
                    "status": status,
                }
            )
        result_cases[key] = cases

    return parsed_results, result_cases


def parse_report_data():
    """로그 파싱 + TC 데이터 로드. UI 없이 순수 데이터를 반환합니다."""
    parsed_results, result_cases = _parse_logs()
    test_case_data = load_all_tc_data()
    total_result = {
        "total": 0, "pass": 0, "fail": 0, "minor_fail": 0,
        "na": 0, "nt": 0, "no_run": 0, "error": 0,
        "result_cases": result_cases,
    }
    return parsed_results, result_cases, test_case_data, total_result


def aggregate_results(reviewed_results: dict, reviewed_data: dict, total_result: dict):
    """리뷰 결과를 total_result에 집계하고 OS별 pass_rate를 계산합니다."""
    for key, value in reviewed_results.items():
        for stat in ("total", "pass", "fail", "minor_fail", "na", "nt", "no_run", "error"):
            total_result[stat] += value[stat]

    for cat, items in reviewed_data.items():
        for item in items:
            status = item.get("status")
            reviewed = item.get("is_reviewed", "Key Not Found")
            if reviewed and reviewed != "Key Not Found":
                if status == "FAIL":
                    reviewed_results[cat]["pass"] += 1
                    reviewed_results[cat]["fail"] -= 1
                    total_result["pass"] += 1
                    total_result["fail"] -= 1
                elif status == "Minor_Fail":
                    reviewed_results[cat]["minor_fail"] -= 1
                    total_result["minor_fail"] -= 1
                elif status == "N/A":
                    reviewed_results[cat]["pass"] += 1
                    reviewed_results[cat]["na"] -= 1
                    total_result["pass"] += 1
                    total_result["na"] -= 1
                elif status == "Error":
                    reviewed_results[cat]["pass"] += 1
                    reviewed_results[cat]["error"] -= 1
                    total_result["pass"] += 1
                    total_result["error"] -= 1
            elif not reviewed and reviewed != "Key Not Found":
                if status == "Error":
                    reviewed_results[cat]["fail"] += 1
                    reviewed_results[cat]["error"] -= 1
                    total_result["fail"] += 1
                    total_result["error"] -= 1

        denom = reviewed_results[cat]["total"] - reviewed_results[cat]["nt"]
        reviewed_results[cat]["pass_rate"] = (
            round(reviewed_results[cat]["pass"] / denom * 100, 2) if denom > 0 else 0
        )

    denom_total = total_result["total"] - total_result["nt"]
    total_result["pass_rate"] = (
        round(total_result["pass"] / denom_total * 100, 2) if denom_total > 0 else 0
    )


def finalize_report(
    reviewed_data, reviewed_results, plm_info, total_result, comment_info, device_info
):
    """HTML 리포트를 생성하고 (html_content, html_path)를 반환합니다."""
    html_path = f"{cv.base_log_path}/test_result.html"
    if os.path.exists(html_path):
        os.remove(html_path)

    html_content = generate_html_report(
        total_result=total_result,
        reviewed_data=reviewed_data,
        reviewed_results=reviewed_results,
        plm_info=plm_info,
        test_case_data=load_all_tc_data(),
        comment_info=comment_info,
        device_info=device_info,
    )
    return html_content, html_path
