from bs4 import BeautifulSoup


def transform_html_table(input_html):
    soup = BeautifulSoup(input_html, 'html.parser')
    # 1. 대상 HTML 테이블 기본 뼈대 및 CSS 스타일 설정
    target_html = [
        '<TABLE style="width:1330.98px;border-collapse:collapse;margin-bottom:30px;table-layout:fixed;color:rgb(0, 0, 0);font-family:\'Malgun Gothic\', Arial, sans-serif;font-weight:400;orphans:2;" class="result_table cui-real-table">',
        ' <COLGROUP><COL style="width:100px;"/><COL style="width:71.9531px;"/><COL style="width:71.9531px;"/><COL style="width:71.9531px;"/><COL style="width:71.9531px;"/><COL style="width:71.9531px;"/><COL style="width:100px;"/><COL style="width:250px;"/><COL style="width:520.312px;"/></COLGROUP>',
        ' <THEAD>',
        ' <TR>'
    ]
    # 2. 헤더(THEAD) 추출 및 변환
    headers = soup.find('thead').find_all('th')
    for i, th in enumerate(headers):
        text = th.text.strip()
        # 열(Column) 너비 동적 할당
        if text == "Android OS":
            width_style = "width:100px;"
        elif text in ["Total", "Pass", "TC Fail", "N/A", "N/T"]:
            width_style = "width:71.9531px;"
        elif text == "Pass Rate":
            width_style = "width:100px;"
        elif text == "Comment":
            width_style = "width:250px;"
        else:
            width_style = ""  # 주요이슈
        class_str = ' class="summary"' if i < 7 else ''
        font_size = "10pt" if i < 7 else "13.3333px"
        th_tag = f' <TH style="border:1px solid #dddddd;text-align:center;height:21px;background-color:#4caf50;color:white;font-weight:bold;{width_style}padding-left:12px;padding-bottom:12px;padding-right:12px;padding-top:12px;"{class_str}>'
        th_tag += f'\n <P><SPAN class="cui-origin-span" style="font-size:{font_size};">{text}</SPAN></P>\n </TH>'
        target_html.append(th_tag)
    target_html.extend([' </TR>', ' </THEAD>', ' <TBODY>'])
    # 3. 본문(TBODY) 추출 및 변환
    rows = soup.find('tbody').find_all('tr')
    for idx, tr in enumerate(rows):
        cells = tr.find_all('td')
        if not cells: continue
        is_total_row = "Total" in cells[0].text
        # 행 스타일(배경색) 설정
        if is_total_row:
            row_style = ' style="background-color:antiquewhite;font-weight:bold;font-size:15pt;"'
        elif idx % 2 != 0:
            row_style = ' style="background-color:#f9f9f9;font-size:11.25pt;"'
        else:
            row_style = ' style="font-size:11.25pt;"'
        target_html.append(f' <TR{row_style}>')
        for i, td in enumerate(cells):
            text_color = ""
            align = "center"
            # 셀 기본 색상 및 정렬 처리
            if i == 3:
                text_color = "color:red;"
            elif i == 4:
                text_color = "color:gray;"
            elif i == 5:
                text_color = "color:blue;"
            if not is_total_row:
                if i in [7, 8]: align = "left"
                if i == 7: text_color = "color:blue;"
                if i == 8: text_color = "color:red;"
                font_weight = "font-weight:bold;" if i == 0 else ""
                font_size = "11.25pt" if i >= 7 else "10pt"
            else:
                font_weight = ""
                font_size = "10pt"
            td_style = f'border:1px solid #dddddd;text-align:{align};{text_color}padding-left:12px;padding-bottom:12px;padding-right:12px;padding-top:12px;'
            td_open = f' <TD class="cui-real-td" style="{td_style}">'
            td_close = ' </TD>'
            # 4. 내부에 <div> 태그가 있는 복합 셀(Comment, 주요이슈) 동적 처리
            divs = td.find_all('div')
            if not is_total_row and divs:
                target_html.append(td_open)
                for div in divs:
                    div_text = div.get_text(strip=True)
                    div_style = div.get('style') or ''
                    # <div> 태그 내 font-weight bold 속성 추출
                    is_bold = 'font-weight: bold' in div_style or 'font-weight:bold' in div_style.replace(' ', '')
                    inner_td_style = "border:0px rgb(255, 0, 0);"
                    if is_bold:
                        inner_td_style = "font-weight:bold;" + inner_td_style
                    # 텍스트가 존재하면 P/SPAN 태그로 감싸고, 빈 줄이면 여백만 유지
                    if div_text:
                        content = f'\n <P><SPAN class="cui-origin-span" style="font-size:10pt;">{div_text}</SPAN></P>\n '
                    else:
                        content = "\n "
                    # 동적으로 서브 테이블 생성
                    nested_table = f''' <TABLE style="border-collapse:collapse;" class="cui-div">
                    <COLGROUP><COL/></COLGROUP>
                    <TBODY>
                        <TR>
                            <TD class="cui-div-cell" style="{inner_td_style}">{content}</TD>
                        </TR>
                    </TBODY>
                </TABLE>'''
                    target_html.append(nested_table)
                target_html.append(td_close)

            # 일반 텍스트 셀 처리
            else:
                cell_text = td.get_text(strip=True)
                if cell_text:
                    span_content = f'<P><SPAN class="cui-origin-span" style="{font_weight}font-size:{font_size};">{cell_text}</SPAN></P>'
                    target_html.append(f"{td_open}\n {span_content}\n{td_close}")
                else:
                    target_html.append(f"{td_open}\n{td_close}")
        target_html.append(' </TR>')
    target_html.extend([' </TBODY>', '</TABLE>'])
    return '\n'.join(target_html)

    #----- 실행 예시 -----
def generate_email_form(html_path):

    with open(html_path, "r", encoding="utf-8") as file:
        content = file.read()
    # 2. BeautifulSoup 객체 생성 (파싱)
    soup = BeautifulSoup(content, 'html.parser')


    # 3-3. 특정 클래스(class)를 가진 태그 찾기 (class는 예약어이므로 class_ 사용)
    table_tag = soup.find('table', class_='result_table')


    input_html = str(table_tag)
    result = transform_html_table(input_html)

    return result


