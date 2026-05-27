from datetime import datetime

def generate_html(sender_name: str, sender_rank: str, release_ver: str, application_ver: str, table_form: str) -> str:
    """사용자 입력을 바탕으로 HTML 이메일 템플릿을 생성합니다."""
    main_form = f"""<P><SPAN style="font-size:10pt;">▣ 수신 : 수신처 제위</SPAN></P>
<P><SPAN style="font-size:10pt;">▣ 참조 : 참조처 제위</SPAN></P>
<P><SPAN style="font-size:10pt;">▣ 발신 : {sender_name} {sender_rank} / 어니컴 주식회사</SPAN></P>
<P><SPAN style="font-size:10pt;"><BR/></SPAN></P>
<P><SPAN style="font-size:10pt;">안녕하세요.</SPAN></P>
<P><SPAN style="font-size:10pt;">어니컴 {sender_name}입니다.</SPAN></P>
<P><SPAN style="font-size:10pt;"><BR/></SPAN></P>
<P><SPAN style="font-size:10pt;">요청하신 [{release_ver}][{application_ver}] Android Build Verification Test 중 Build Verification Checklist 진행 결과 송부해드립니다.</SPAN></P>
<P><SPAN style="font-size:10pt;"><BR/></SPAN></P>"""
    sub_form = ""
    sub_form += f"""<P><SPAN style="font-size:10pt;font-weight:bold;">1. 진행결과</SPAN></P>
<P><SPAN style="font-size:10pt;"> - 자동화 테스트 요약 프로그램(ATRA)을 활용하여 자동화 효율화 진행하였으니 참고 부탁 드립니다(자동으로 테스트 수행 및 결과 취합)<BR/></SPAN></P>\n"""

    final_form = """<P><SPAN style="font-size:10pt;">자세한 사항은 첨부파일 확인 부탁드립니다.</SPAN></P>
    <P><SPAN style="font-size:10pt;">감사합니다.</SPAN></P>"""
    # 최종 결과물 합치기
    return main_form + "\n" + sub_form + "\n" + table_form + "\n" + final_form

def generate_title(release_ver: str, application_ver: str):

    return f"[진행결과][SVT][{release_ver}][{application_ver}] Android Build Verification Test 진행 결과 ({datetime.now().strftime('%m/%d')})"

print(generate_title("2026 R1.2", "1.8.45.17 RC2"))