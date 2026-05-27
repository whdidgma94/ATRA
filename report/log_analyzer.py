import re
from typing import Dict


def parse_result_file(file_path: str) -> Dict:
    """Android 테스트 결과 파일 파싱 (다중 결과 지원)"""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    test_cases = []

    # 카운터 초기화
    counts = {
        'pass': 0, 'fail': 0, 'minor_fail': 0,
        'error': 0, 'na': 0, 'nt': 0, 'no_run': 0
    }

    current_case = None  # 현재 처리 중인 TC ID를 기억하는 변수
    i = 0

    while i < len(lines):
        line = lines[i].strip()
        # 1. TC ID 발견 시: 현재 케이스 이름 갱신
        if re.match(r'TC ID : ', line) and not re.match(r'TC ID : reset_location', line):
            current_case = line.split(':')[1].strip()
            i += 1
            continue  # ID를 찾았으니 다음 줄로 이동해서 결과를 찾음

        # 2. 결과 라인 파싱 (현재 TC ID가 존재할 때만)
        if current_case:
            error_msg = ''

            # 상태값 판별
            if line == 'Pass':
                status = 'Pass'
                counts['pass'] += 1
            elif line.startswith('FAIL') or line.startswith('Fail'):
                status = 'Fail'
                counts['fail'] += 1
            elif line.startswith('entry_FAIL') or line.startswith('popup_FAIL'):
                status = 'Minor_Fail'
                counts['minor_fail'] += 1
            elif line.startswith('N/A'):
                status = 'N/A'
                counts['na'] += 1
            elif line.startswith('ERROR'):
                status = 'Error'
                counts['error'] += 1
            elif line.startswith('N/T'):
                status = 'N/T'
                counts['nt'] += 1
            else:
                status = 'No run'
                counts['no_run'] += 1

            # 3. 유효한 상태값이 발견된 경우 처리
            if status:
                # 에러 메시지 추출 (-> 구분자 처리)
                if '->' in line:
                    error_msg = line.split('->', 1)[1].strip()
                elif status != 'Pass':  # Pass가 아닌데 -> 가 없으면 라인 전체가 메시지일 수 있음
                    # FAIL 등의 접두사 제거 (필요 시)
                    error_msg = line.replace(status, '', 1).strip()

                # 실행 시간 확인 (다음 줄 미리보기)
                execution_time = ''
                screenshot_folder = ''
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    # 시간 형식인지 간단히 체크 (숫자와 콜론으로 구성된 경우)
                    if re.match(r'\d{2}/\d{2} \d{2}:\d{2}', next_line):
                        execution_time = next_line
                        i += 1  # 시간을 읽었으므로 인덱스 하나 더 증가
                        if status == "Minor_Fail":
                            next_line = lines[i+1].strip()
                            if re.match(r'\d{8}_\d{6}', next_line):
                                screenshot_folder = next_line

                                i += 1

                test_cases.append({
                    'name': current_case,
                    'status': status,
                    'error_msg': error_msg,
                    'execution_time': execution_time,
                    'screenshot_folder': screenshot_folder
                })


        # 다음 줄로 이동
        i += 1

    # 전체 개수는 발견된 결과들의 합으로 계산
    total_count = sum(counts.values()) - counts['minor_fail']
    return {
        'total': total_count,
        'pass': counts['pass'],
        'fail': counts['fail'],
        'minor_fail': counts['minor_fail'],
        'na': counts['na'],
        'nt': counts['nt'],
        'no_run': counts['no_run'],
        'error': counts['error'],
        'pass_rate': round((counts['pass'] / (total_count-counts['nt']) * 100), 2) if total_count > 0 and total_count-counts['nt'] > 0 else 0,
        'test_cases': test_cases
    }




