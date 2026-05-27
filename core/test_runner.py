import base64
import importlib.util
import os
import subprocess
import time

from api.actions import printl, restart, find
from config import common_variable
from config.common_variable import os_version_dic, application_path
from core.appium_manager import start_appium_server
from core.webdriver import get_wd
from datetime import datetime


def get_testcases():
    tc_list = []

    tc_dir = os.path.join(application_path, "testcase")
    for root1, _, testcase in os.walk(tc_dir):
        sorted_testcase = sorted(testcase)
        j = 0
        while j < len(sorted_testcase):
            tc = sorted_testcase[j]
            if tc.endswith("pyc"):
                j += 1
                continue
            if tc.endswith("py") and not tc.startswith("__"):
                tc_list.append(tc.split(".")[0])
            j += 1

    return tc_list


def run_device_process(udid1, port1, os_ver, log_direction, shared_dic):
    start_appium_server(port1)
    system_port = 8201 + (port1 - 4723) // 2
    wd = get_wd(udid1, port1, os_version_dic[os_ver], log_direction, system_port=system_port)
    try:
        run_test(wd, os_version_dic[os_ver], log_direction, shared_dic)
    finally:
        wd.quit()


def _save_recording(wd, os_ver, output_dir):
    time.sleep(2)
    video_raw_data = wd.stop_recording_screen()
    video_data = base64.b64decode(video_raw_data)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    video_path = os.path.join(output_dir, 'original_recording.mp4')
    compress_path = os.path.join(output_dir, 'recording.mp4')

    for path in (video_path, compress_path):
        if os.path.exists(path):
            os.remove(path)

    with open(video_path, 'wb') as video_file:
        video_file.write(video_data)

    time.sleep(1)
    try:
        creationflags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        subprocess.run(
            ['ffmpeg', '-i', video_path, '-r', '30', '-c:v', 'libx264', '-crf', '35', '-an', compress_path],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=creationflags
        )
        os.remove(video_path)
    except Exception:
        print(f"{os_ver} 동영상 압축 중 오류 발생")
        try:
            os.remove(compress_path)
        except Exception:
            pass


def run_test(wd, os_ver, log_direction, shared_dic):
    result = None
    tc_list = get_testcases()
    current_state = {script: 'Pending' for script in tc_list}
    shared_dic[os_ver] = current_state

    common_variable.base_log_path = log_direction
    common_variable.log_path = log_direction + f"/{os_ver}"
    common_variable.os_ver = os_ver
    if not os.path.exists(common_variable.log_path):
        os.makedirs(common_variable.log_path)

    testcases_path = os.path.join(application_path, "testcase")

    for script in tc_list:
        current_state[script] = 'Running'
        shared_dic[os_ver] = current_state
        file_path = ""
        for root1, _, dir1 in os.walk(testcases_path):
            for tcid in dir1:
                if tcid == script + ".py":
                    file_path = os.path.join(root1, tcid)

        common_variable.tcid = script
        print(f"{os_ver} 실행 중 : {common_variable.tcid}")
        printl(f"TC ID : {common_variable.tcid}")
        try:
            spec = importlib.util.spec_from_file_location("dynamic_module", file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            wd.start_recording_screen(videoSize='1280x720', bitRate='1000000')
            if hasattr(module, "run"):
                restart()
                sw = module.run(wd)
                if sw is None:
                    printl("Pass")
                    result = "Pass"
                else:
                    printl(sw)
                    result = sw.split("-")[0]
            else:
                print(f"{script} 에 run() 함수가 없습니다.")
        except SystemExit:
            result = "Fail"
        except Exception as e:
            print(f"{os_ver} {common_variable.tcid} 실행 중 오류 발생: {e}")
            printl(f"ERROR -> {common_variable.tcid} 실행 중 오류 발생")
            result = "Error"
        finally:
            try:
                printl(datetime.now().strftime('%m/%d %H:%M'))
                output_dir = f'{common_variable.log_path}/{common_variable.tcid}'
                _save_recording(wd, os_ver, output_dir)
                find("android:id/aerr_close", True, ex=True)
                if common_variable.tcid == "Basic_function_Checklist_1080":
                    wd.press_keycode(4)
                    wd.press_keycode(4)
                    wd.press_keycode(4)
                common_variable.defect = False
            except Exception:
                pass
        current_state[script] = result
        shared_dic[os_ver] = current_state
