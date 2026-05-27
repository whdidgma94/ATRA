import os
import importlib.util

from config.common_variable import application_path




def load_all_tc_data():
    test_case_data = {}
    """testcase 폴더를 순회하며 각 스크립트의 tc_info를 추출해 딕셔너리로 반환합니다."""
    base_dir = os.path.join(application_path, "testcase")

    if not os.path.exists(base_dir):
        print(f"경고: 테스트 케이스 폴더를 찾을 수 없습니다. 경로: {base_dir}")
        return test_case_data

    for root, _, files in os.walk(base_dir):
        sorted_files = sorted(files)

        for filename in sorted_files:
            # .pyc 파일이거나 __init__.py 같은 특수 파일, .py가 아닌 파일은 건너뜀
            if filename.endswith(".pyc") or filename.startswith("__") or not filename.endswith(".py"):
                continue

            file_path = os.path.join(root, filename)
            module_name = os.path.splitext(filename)[0]

            try:
                spec = importlib.util.spec_from_file_location(module_name, file_path)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    # 모듈 안에 'tc_info' 변수가 존재하면 딕셔너리에 저장
                    if hasattr(module, 'tc_info'):
                        test_case_data[module_name] = getattr(module, 'tc_info')

            except Exception as e:
                print(f"[TCParser] '{filename}' 로드 중 오류 발생: {e}")

    return test_case_data
