import base64
import io
import json
from PIL import Image


Image.init()

def get_screenshot_info(screenshot_path):
    if screenshot_path == "":
        return ""
    with Image.open(screenshot_path) as screenshot:
        if screenshot.mode in ("RGBA", "P"):
            screenshot = screenshot.convert("RGBA")
        else:
            screenshot = screenshot.convert("RGB")
        max_width = 1000
        if screenshot.width > max_width:
            ratio = max_width / float(screenshot.width)
            new_height = int(float(screenshot.height) * ratio)
            screenshot = screenshot.resize((max_width, new_height), Image.Resampling.LANCZOS)
        buffer = io.BytesIO()
        screenshot.save(buffer, format="WEBP", quality=1)
        return base64.b64encode(buffer.getvalue()).decode('utf-8')



def generate_html_report(total_result: dict, reviewed_data: dict, reviewed_results: dict, plm_info: dict, test_case_data: dict, comment_info: dict, device_info: dict) -> str:
    html_template = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>자동화 테스트 결과 요약</title>
    <style>
        body {{
            font-family: 'Malgun Gothic', Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
            justify-content: center;
            align-items:center;
        }}
        .container {{
            max-width: 1800px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            text-align: center;
            margin-bottom: 30px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 30px;
            background-color: white;
        }}
        .result_table{{
            table-layout: fixed;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: center;
        }}
        th {{
            height: 21px;
            background-color: #4CAF50;
            color: white;
            font-weight: bold;
        }}
        .summary {{
            width: 4%;
        }}
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        .toggle-button{{
            font-size: 16px;
            font-weight: bold;
            padding: 12px 24px;
            cursor: pointer;
            border: none;
            background-color: #4CAF50;
            color: white;
            border-radius: 8px;
        }}
        .toggle-button:hover{{
            background-color: #006400;
        }}
        .toggle-button.active{{
            background-color: #006400;
        }}
        .section-title {{
            font-size: 18px;
            font-weight: bold;
            color: #333;
            margin: 30px 0 15px 0;
            border-bottom: 2px solid #4CAF50;
            padding-bottom: 5px;
        }}
        .fail-case {{
            text-align: left;
            white-space: nowrap;
            min-width: 300px;
        }}
        .toggle-tr {{
            display: none;
        }}
        .visible-tr {{
            display: table-row;
        }}
        .card{{
            display: flex;
            justify-content: center;
            align-items:center;
            overflow:hidden;
            cursor:pointer;
        }}
        .card img{{
            height: 50px;
            object-fit: cover;
            display: block;
        }}
        .card.expanded img{{
            width: auto;
        }}
        .modal{{
            display: none;
            position: fixed;
            z-index: 1000;
            padding-top: 50px;
            left: 0; top: 0;
            width: 100%; height: 100%;
            overflow: auto;
            background-color: rgba(0, 0, 0, 0.5);
        }}
        .modal-content {{
            margin: auto;
            display: block;
            height: 800px;
            border-radius: 5px;
            box-shadow: 0 0 20px rgba(255,255,255,0.2);
            animation-name: zoom;
            animation-duration: 0.3s;
            cursor: pointer;
        }}
        /* 닫기 버튼 (X) */
        .close {{
            position: absolute;
            top: 15px;
            right: 35px;
            color: #f1f1f1;
            font-size: 40px;
            font-weight: bold;
            transition: 0.3s;
            cursor: pointer;
        }}
        .close:hover, .close:focus {{
            color: #bbb;
            text-decoration: none;
            cursor: pointer;
        }}
        .divider-row td {{
            border-bottom: 0.5px solid #ddd;
            padding: 0px;
            height: 0px;
        }}
        .tcModal{{
            display: none;
            position: fixed;
            z-index: 1000;
            padding-top: 50px;
            left: 0; top: 0;
            width: 100%; height: 100%;
            overflow: auto;
            background-color: rgba(0, 0, 0, 0.5);
            justify-content: center;
            align-items:center;
        }}
        .tcModal-content {{
            margin: auto;
            display: flex;
            border-radius: 5px;
            box-shadow: 0 0 20px rgba(255,255,255,0.2);
            animation-name: zoom;
            animation-duration: 0.3s;
            cursor: pointer;
        }}
        pre {{
            font-family: 'Malgun Gothic', Arial, sans-serif;
            font-size: 13px;
            text-align: left;
            white-space: pre-wrap;
        }}
        .tcListModal{{
            display: none;
            position: fixed;
            z-index: 1000;
            padding-top: 100px;
            left: 0; top: 0;
            width: 100%; height: 100%;
            overflow: auto;
            background-color: rgba(0, 0, 0, 0.5);
            justify-content: center;
            flex-wrap: wrap;
        }}
        .tcListModal-content {{
            margin: auto;
            display: flex;
            border-radius: 5px;
            box-shadow: 0 0 20px rgba(255,255,255,0.2);
            animation-name: zoom;
            animation-duration: 0.3s;
            cursor: pointer;
        }}
    </style>
</head>
<body>
<div class="container">
    <h1>자동화 테스트 결과 요약 보고서</h1>
    <div class="section-title">테스트 수행 결과</div>
    <table class="result_table">
        <thead>
            <tr>
                <th class = "summary" style = "width: 100px">Android OS</th>
                <th class = "summary">Total</th>
                <th class = "summary">Pass</th>
                <th class = "summary">TC Fail</th>
                <th class = "summary">N/A</th>
                <th class = "summary">N/T</th>
                <th class = "summary" style="width: 100px;">Pass Rate</th>
                <th style="width: 250px;">Comment</th>
                <th>주요이슈</th>
            </tr>
        </thead>
        <tbody>
"""


    # 1. OS별 결과 요약표 렌더링
    for key, value in reviewed_results.items():
        os_name = key.replace("OS", " OS").replace("_", "")

        html_template += f"""
            <tr style="font-size:15px;">
                <td><button onclick="toggleVisibility(this, '{key}')" class="toggle-button">{os_name}</button>
                Model name : {device_info.get(key, "")}</td>
                <td>{value['total']}</td>
                <td>{value['pass']}</td>
                <td style="color: red">{value['fail']}</td>
                <td style="color: gray">{value['na']}</td>
                <td style="color: blue">{value['nt']}</td>
                <td>{value['pass_rate']}%</td>
                <td style="color: blue; font-size: 15px; text-align: left;">
"""
        if comment_info[key]["N/A"] != [] and comment_info.get(key):
            html_template += f"""
                    <div style="font-weight: bold;">#. N/A</div>
"""
            for comment in comment_info[key]["N/A"]:
                    html_template += f"<div>{comment}</div>"

        if comment_info[key]["N/A"] != [] and comment_info[key]["N/T"] != []:
            html_template += f"<br></br>"

        if comment_info[key]["N/T"] != [] and comment_info.get(key):
            html_template += f"""
                        <div style="font-weight: bold;">#. N/T</div>
"""
            for comment in comment_info[key]["N/T"]:
                html_template += f"<div>{comment}</div>"

        html_template += f"""
            </td>
"""
        if plm_info and plm_info.get(key):
            html_template += f"""
                <td style="color: red; font-size: 15px; text-align: left;">
                    <div style="font-weight: bold;">#. FAIL</div>
"""
            for issue_info in plm_info[key]:
                html_template += f"<div>{issue_info}</div>"
            html_template += "</td>"
        else:
            html_template += """
                    <td style="color: red; font-size: 15px; text-align: left;">
                        <div style="font-weight: bold;"></div>
                        <div></div>
                    </td>"""
        html_template += "</tr>"
    html_template += f"""
            <tr style = "font-weight: bold; background-color: antiquewhite; font-size:20px;">
                <td>Total</td>
                <td>{total_result['total']}</td>
                <td>{total_result['pass']}</td>
                <td style="color: red">{total_result['fail']}</td>
                <td style="color: gray">{total_result['na']}</td>
                <td style="color: blue">{total_result['nt']}</td>
                <td>{total_result['pass_rate']}%</td>
                <td> </td>
                <td> </td>
            </tr>
        </tbody>
    </table>
    <div class="section-title">Test Case 상세 정보</div>
        <div style="width: 100%; justify-content: center; display: flex;">
            <button class="toggle-button" onclick="opentcListModal()" style="width: 50%; margin-bottom: 15px;">Test cases</button>
        </div>
        <table>
            <thead>
                <tr>
                    <th style="width: 50px;">OS</th>
                    <th style="width: 250px;">Test case ID</th>
                    <th style="width: 100px;">수행 일시</th>
                    <th style="width: 100px;">Test Result</th>
                    <th>Actual Result</th>
                    <th style="width: 100px;">Screenshot</th>
                    <th style="width: 110px;">Re-test Result</th>
                    <th style="width: 200px;">PLM</th>
                </tr>
            </thead>
            <tbody id="fail_case">
    """

    for key, value in reviewed_data.items():
        tcid = ""
        os_name = key.replace("OS", " OS")
        os_name = os_name.replace("_", "")
        sorted_data = sorted(
            value,
            key=lambda x: (x['name'], 0 if x['status'] == 'FAIL' else 1)
        )
        for case in sorted_data:
            if case['status'] == 'Pass':
                html_template += f"""
                            <tr class="toggle-tr {key}" style="color: black; font-weight: bold;">
    """
            elif case['status'] == 'FAIL':
                if case["is_reviewed"]:
                    html_template += f"""
                                <tr class="toggle-tr {key}" style="color: black; font-weight: bold;">
    """
                else:
                    html_template += f"""
                                <tr class="toggle-tr {key}" style="color: red; font-weight: bold;">
    """
            elif case['status'] == 'Minor_Fail':
                if case["is_reviewed"]:
                    html_template += f"""
                                <tr class="toggle-tr {key}" style="color: black; font-weight: bold;">
    """
                else:
                    html_template += f"""
                                <tr class="toggle-tr {key}" style="color: coral; font-weight: bold;">
    """
            elif case['status'] == 'N/T':
                html_template += f"""
                            <tr class="toggle-tr {key}" style="color: blue; font-weight: bold;">
    """
            elif case['status'] == 'N/A':
                if case["is_reviewed"]:
                    html_template += f"""
                                <tr class="toggle-tr {key}" style="color: black; font-weight: bold;">
    """
                else:
                    html_template += f"""
                            <tr class="toggle-tr {key}" style="color: gray; font-weight: bold;">
    """
            elif case['status'] == 'Error':
                if case["is_reviewed"]:
                    html_template += f"""
                                <tr class="toggle-tr {key}" style="color: black; font-weight: bold;">
    """
                else:
                    html_template += f"""
                            <tr class="toggle-tr {key}" style="color: red; font-weight: bold;">
    """
            if tcid == "":
                tcid = case['name']
                html_template += f"""
                                <td>{os_name}</td>
                                <td>
                                    <div class= "card" onclick="openTcModal(this.innerHTML)">{case['name']}</div>
                                </td>
    """
            elif tcid == case['name']:
                html_template += f"""
                                <td></td>
                                <td></td>
    """
            else:
                tcid = case['name']
                html_template += f"""
                                <td>{os_name}</td>
                                <td>
                                    <div class= "card" onclick="openTcModal(this.innerHTML)">{case['name']}</div>
                                </td>
    """
            html_template += f"""
                                <td>{case['execution_time']}</td>
    """
            if case['status'] == "FAIL":
                html_template += f"""
                                    <td>TC Fail</td>
    """
            elif case['status'] == "Minor_Fail":
                html_template += f"""
                                    <td>추가시험 Fail</td>
    """
            elif case['status'] == "Error":
                html_template += f"""
                                    <td>Error</td>
    """
            else:
                html_template += f"""
                                    <td>{case['status']}</td>
    """
            html_template += f"""
                                <td>{case['content']}</td>
                                <td>
    """
            if case['screenshot_file'] != "":
                html_template += f"""
                                    <div class="card" onclick="openModal(this.querySelector('img').src)">
                                        <img src="data:image/webp;base64,{case['screenshot_file']}" alt="">
                                    </div>
    """
            html_template += f"""
                                </td>
    """
            if case['status'] == "FAIL" or case['status'] == "Minor_Fail" or case['status'] == "N/A" or case['status'] == "Error":
                if case["is_reviewed"]:
                    html_template += f"""
                                    <td style="color:black;">Pass</td>
    """
                else:
                    if case['status'] == "FAIL":
                        html_template += f"""
                                    <td>TC FAIL</td>
    """
                    if case['status'] == "Minor_Fail":
                        html_template += f"""
                                    <td>추가시험 Fail</td>
    """
                    if case['status'] == "N/A":
                        html_template += f"""
                                    <td>N/A</td>
    """
                    if case['status'] == "Error":
                        html_template += f"""
                                    <td>TC FAIL</td>
    """
            else:
                html_template += f"""
                                <td></td>
    """
            try:
                if case['plm_num'] == "":
                    html_template += f"""
                                    <td>{case['plm_title']}</td>
    """
                else:
                    html_template += f"""
                                    <td>[{case['plm_num']}] {case['plm_title']}</td>
    """
            except KeyError:
                html_template += f"""
                                <td></td>
    """
            html_template += f"""
                            </tr>
    """
    html_template += """
                </tbody>
            </table>
        </div>
        <div id="myModal" class="modal" onclick="closeModal()">
            <span class="close">&times;</span>
            <img class="modal-content" id="img01" alt="">
        </div>
        <div id="tcModal" class="tcModal" onclick="closeTcModal()">
            <span class="close">&times;</span>
            <table style="margin-bottom: 300px; width: 95%;">
                <thead>
                    <tr>
                        <th>Test Case ID</th>
                        <th>Middle Category</th>
                        <th>Small Category</th>
                        <th>Detail Function</th>
                        <th>Test Objectives</th>
                        <th>Input Specification</th>
                        <th>Pre-condition</th>
                        <th>Test Procedure</th>
                        <th>Expected Result</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td style="width: 200px;"><pre style="text-align: center;" id="tcid"></pre></td>
                        <td style="width: 60px;"><pre style="text-align: center;" id="middle_category"></pre></td>
                        <td style="width: 60px;"><pre style="text-align: center;" id="small_category"></pre></td>
                        <td style="width: 60px;"><pre style="text-align: center;" id="detail_function"></pre></td>
                        <td style="width: 60px;"><pre id="test_objectives"></pre></td>
                        <td style="width: 60px;"><pre id="input_specification"></pre></td>
                        <td style="width: 100px;"><pre id="pre_condition"></pre></td>
                        <td style="width: 200px;"><pre id="test_procedure"></pre></td>
                        <td style="width: 200px;"><pre id="expected_result"></pre></td>
                    </tr>
                </tbody>
            </table>
        </div>
        <div id="tcListModal" class="tcListModal">
            <span class="close" style="position: fixed; color: black;" onclick="closeTcListModal()">&times;</span>
            <table style="margin-bottom: 300px; width: 95%; height: 100%;">
                <thead>
                    <tr>
                        <th>Test Case ID</th>
                        <th>Middle Category</th>
                        <th>Small Category</th>
                        <th>Detail Function</th>
                        <th>Test Objectives</th>
                        <th>Input Specification</th>
                        <th>Pre-condition</th>
                        <th>Test Procedure</th>
                        <th>Expected Result</th>
                    </tr>
                </thead>
                <tbody>
    """
    for key, value in test_case_data.items():
        html_template += f"""
                    <tr>
                        <td style="width: 200px;"><pre style="text-align: center;">{key}</pre></td>
                        <td style="width: 60px;"><pre style="text-align: center;">{test_case_data[key]["middle_category"]}</pre></td>
                        <td style="width: 60px;"><pre style="text-align: center;">{test_case_data[key]["small_category"]}</pre></td>
                        <td style="width: 60px;"><pre style="text-align: center;">{test_case_data[key]["detail_function"]}</pre></td>
                        <td style="width: 60px;"><pre>{test_case_data[key]["test_objectives"]}</pre></td>
                        <td style="width: 60px;"><pre>{test_case_data[key]["input_specification"]}</pre></td>
                        <td style="width: 100px;"><pre>{test_case_data[key]["pre_condition"]}</pre></td>
                        <td style="width: 200px;"><pre>{test_case_data[key]["test_procedure"]}</pre></td>
                        <td style="width: 200px;"><pre>{test_case_data[key]["expected_result"]}</pre></td>
                    </tr>
    """
    html_template += """
                </tbody>
            </table>
        </div>
    <script>
        function toggleVisibility(btn, os_name) {
            const tbody = document.getElementById('fail_case');
            const os_list = tbody.querySelectorAll('.visible-tr');
            os_list.forEach(tr => {
                tr.classList.remove('visible-tr');
            });
    
            const selector = `.toggle-tr.${os_name}`;
            if (!tbody) return;
            const tdsToToggle = tbody.querySelectorAll(selector);
            tdsToToggle.forEach(tr => {
                tr.classList.toggle('visible-tr');
            });
            const button_element = btn;
            if (button_element.classList.contains('active')){
                button_element.classList.remove('active');
                tdsToToggle.forEach(tr => {
                    tr.classList.remove('visible-tr');
                });
            } else {
                const btn_list = document.querySelectorAll('.toggle-button');
                btn_list.forEach(button => {
                        button.classList.remove('active');
                    });
                button_element.classList.add('active');
            } 
    
        }
        function toggleImageSize(imageElement) {
            const card = imageElement.closest('.card');
            if (card.classList.contains('expanded')) {
                card.classList.remove('expanded')
            } else {
                card.classList.add('expanded')
            }
        }
        var modal = document.getElementById("myModal");
        var modalImg = document.getElementById("img01");
    
        function openModal(src) {
            modal.style.display = "block";
            modalImg.src = src; 
        }
    
        function closeModal() {
            modal.style.display = "none";
        }
    
        var tcModal = document.getElementById("tcModal");
        var tcid = document.getElementById("tcid");
        var middle_category = document.getElementById("middle_category");
        var small_category = document.getElementById("small_category");
        var detail_function = document.getElementById("detail_function");
        var test_objective = document.getElementById("test_objective");
        var input_specification = document.getElementById("input_specification");
        var pre_condition = document.getElementById("pre_condition");
        var test_procedure = document.getElementById("test_procedure");
        var expected_result = document.getElementById("expected_result");
    
    
        function openTcModal(test_case_id) {
    """
    tc_data = json.dumps(test_case_data)
    html_template += f"""
            const testcaseData = {tc_data}
            tcModal.style.display = "flex";
            tcid.innerHTML = test_case_id
            middle_category.innerHTML = testcaseData[test_case_id]["middle_category"]
            small_category.innerHTML = testcaseData[test_case_id]["small_category"]
            detail_function.innerHTML = testcaseData[test_case_id]["detail_function"]
            test_objectives.innerHTML = testcaseData[test_case_id]["test_objectives"]
            input_specification.innerHTML = testcaseData[test_case_id]["input_specification"]
            pre_condition.innerHTML = testcaseData[test_case_id]["pre_condition"]
            test_procedure.innerHTML = testcaseData[test_case_id]["test_procedure"]
            expected_result.innerHTML = testcaseData[test_case_id]["expected_result"]
        }}
    
        function closeTcModal() {{
            tcModal.style.display = "none";
        }}
        function opentcListModal() {{
            tcListModal.style.display = "flex";
        }}
        function closeTcListModal() {{
            tcListModal.style.display = "none";
        }}
    </script>
    
    
    </body>
    </html>
"""

    return html_template

