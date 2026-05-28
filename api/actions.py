import importlib.util
import os
import shutil
import sys
import subprocess
from datetime import datetime
import time
from selenium.webdriver.common.actions import interaction
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.pointer_input import PointerInput
from config import common_variable
from config.common_variable import application_path
from core.webdriver import get_wd

_FAIL_LOG_WAIT = 5  # Fail 로그 수집 전 기기 상태 안정화 대기 시간(초)


# ── 로그 / TC 종료 ────────────────────────────────────────────────────────────

def saveLog(msg):
    # TC 실행 중 문제 발견 시 호출. 버그리포트·로그캣·스크린샷을 저장한 뒤 TC를 즉시 중단합니다.
    wdr = get_wd()
    time.sleep(_FAIL_LOG_WAIT)

    with open(f"{common_variable.log_path}/log.txt", "a", encoding='utf-8') as file:
        file.write(msg + "\n")

    output_dir = f'{common_variable.log_path}/{common_variable.tcid}'

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    report_path = f"{output_dir}/dumpstate_log.zip"
    try:
        udid = wdr.session.get('udid')
        subprocess.run(
            ["adb", '-s', udid, "bugreport", report_path],
            check=True,
            capture_output=True,
            text=True,
            encoding='utf-8',
            creationflags=subprocess.CREATE_NO_WINDOW
        )
    except subprocess.CalledProcessError as e:
        print(f"ADB 명령어 실행 오류: {e}")
        print(f"Stderr: {e.stderr}")
    except FileNotFoundError:
        print("ADB 실행 파일을 찾을 수 없습니다. PATH 환경 변수를 확인하세요.")

    log_path = f"{common_variable.log_path}/Logcat/logcat.txt"
    if not os.path.exists(f"{common_variable.log_path}/Logcat"):
        os.makedirs(f"{common_variable.log_path}/Logcat")
    with open(log_path, "a", encoding='utf-8') as logFile:
        logs = wdr.get_log('logcat')
        for log in logs:
            logFile.write(str(log['message']) + "\n")
        logFile.write(time.strftime('%Y.%m.%d - %H:%M:%S'))
    shutil.copy2(log_path, output_dir)
    wdr.save_screenshot(f"{output_dir}/screenshot.png")

    sys.exit()


def entry_saveLog(msg):
    output_dir = f'{common_variable.log_path}/Logcat'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    log_file_path = f"{common_variable.log_path}/log.txt"
    with open(log_file_path, "r", encoding='utf-8') as f:
        if any(msg in line for line in f):
            return

    wdr = get_wd()
    time.sleep(_FAIL_LOG_WAIT)
    errTime = datetime.now().strftime('%Y%m%d_%H%M%S')

    with open(log_file_path, "a", encoding='utf-8') as file:
        file.write(msg + "\n")
        file.write(datetime.now().strftime('%m/%d %H:%M') + "\n")
        file.write(errTime + "\n")

    output_dir = f'{common_variable.log_path}/{common_variable.tcid}/{errTime}'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    log_path = f"{common_variable.log_path}/Logcat/logcat.txt"
    with open(log_path, "a", encoding='utf-8') as logFile:
        logs = wdr.get_log('logcat')
        for log in logs:
            logFile.write(str(log['message']) + "\n")
    shutil.copy2(log_path, output_dir)
    wdr.save_screenshot(f"{output_dir}/screenshot.png")


def printl(msg):
    with open(f"{common_variable.log_path}/log.txt", "a", encoding='utf-8') as f:
        f.write(msg + "\n")
    print(msg)


# ── 앱 제어 ───────────────────────────────────────────────────────────────────

def restart():
    wdr = get_wd()
    wdr.terminate_app("com.samsung.android.oneconnect")
    wdr.terminate_app("com.android.chrome")
    wdr.activate_app("com.samsung.android.oneconnect")


# ── Element 탐색 ──────────────────────────────────────────────────────────────

def get_appiumby(pram):
    if "//" in pram:
        appiumby = "xpath"
    elif "UiSelector" in pram:
        appiumby = "-android uiautomator"
    elif ("com.samsung.android" in pram or "android:id/" in pram
          or "com.sec.android.app.launcher" in pram
          or "com.android.permissioncontroller" in pram
          or "com.google.android.gms" in pram):
        appiumby = "id"
    elif "android.widget" in pram or "android.webkit" in pram:
        appiumby = "class name"
    else:
        appiumby = "accessibility id"
    return appiumby


def find(pram, click=False, ex=False, parent=None):
    wdr = get_wd()

    if ex and parent is None:
        wdr.implicitly_wait(1)

    if parent is not None:
        wdr = parent

    appiumby = get_appiumby(pram)

    try:
        elem = wdr.find_element(appiumby, pram)
        t = elem.is_displayed()
    except Exception:
        elem, t = None, False
    if t:
        if click:
            elem.click()
        if ex and parent is None:
            wdr.implicitly_wait(10)
        return t

    try:
        elem = wdr.find_element(appiumby, pram)
        t = elem.is_enabled()
    except Exception:
        elem, t = None, False
    if t:
        if click:
            elem.click()
        if ex and parent is None:
            wdr.implicitly_wait(10)
        return t
    if parent is None:
        wdr.implicitly_wait(1)
    try:
        elem = wdr.find_element(pram)
        t = elem.is_displayed()
    except Exception:
        elem, t = None, False
    if t:
        if click:
            elem.click()
        if ex and parent is None:
            wdr.implicitly_wait(10)
        return t

    try:
        elem = wdr.find_element(pram)
        t = elem.is_enabled()
    except Exception:
        elem, t = None, False
    if t:
        if click:
            elem.click()
        if ex and parent is None:
            wdr.implicitly_wait(10)
        return t
    if parent is None:
        wdr.implicitly_wait(10)

    return False


def find_text(element, text, click=False, ex=False, parent=None):
    wdr = get_wd()
    if not find(element, ex=ex, parent=parent):
        return False

    appiumby = get_appiumby(element)
    if parent is not None:
        wdr = parent
    elem = wdr.find_element(appiumby, element)
    if elem.get_attribute("text") != text:
        return False

    if click:
        elem.click()

    return True


def find_enabled(element, click=False, ex=False, parent=None):
    wdr = get_wd()
    if not find(element, ex=ex, parent=parent):
        return False

    appiumby = get_appiumby(element)
    if parent is not None:
        wdr = parent
    elem = wdr.find_element(appiumby, element)
    if not elem.is_enabled():
        return False

    if click:
        elem.click()

    return True


def find_disabled(element, click=False, ex=False, parent=None):
    wdr = get_wd()
    if not find(element, ex=ex, parent=parent):
        return False

    if parent is not None:
        wdr = parent

    appiumby = get_appiumby(element)
    elem = wdr.find_element(appiumby, element)
    if elem.is_enabled():
        return False

    if click:
        elem.click()

    return True


def find_checked(element, checked, click=False, ex=False, parent=None):
    wdr = get_wd()
    if not find(element, ex=ex, parent=parent):
        return False

    appiumby = get_appiumby(element)
    if parent is not None:
        wdr = parent

    elem = wdr.find_element(appiumby, element)
    if elem.get_attribute("checked") != checked:
        return False

    if click:
        elem.click()

    return True


def find_selected(element, selected, click=False, ex=False, parent=None):
    wdr = get_wd()
    if not find(element, ex=ex, parent=parent):
        return False

    appiumby = get_appiumby(element)
    if parent is not None:
        wdr = parent

    elem = wdr.find_element(appiumby, element)
    if elem.get_attribute("selected") != selected:
        return False

    if click:
        elem.click()

    return True


def find_toast(text):
    wdr = get_wd()
    try:
        if wdr.find_element('//android.widget.Toast').get_attribute("text") == text:
            return True
    except (Exception,):
        return False
    return False


# ── 입력 ──────────────────────────────────────────────────────────────────────

def send_text(element, text, clear=False, parent=None):
    wdr = get_wd()
    if not find(element, True, parent=parent):
        return False

    appiumby = get_appiumby(element)
    if parent is not None:
        wdr = parent

    elem = wdr.find_element(appiumby, element)
    if clear:
        elem.clear()
    elem.send_keys(text)

    return True


# ── 스크롤 / 제스처 ───────────────────────────────────────────────────────────

def scrollDown(slightly=False):
    wdr = get_wd()
    deviceSize = wdr.get_window_size()
    screenWidth = deviceSize['width']
    screenHeight = deviceSize['height']
    if not slightly:
        wdr.swipe(start_x=int(screenWidth / 2), start_y=int(screenHeight * 0.7), end_x=int(screenWidth / 2), end_y=int(screenHeight * 0.2), duration=500)
    else:
        wdr.swipe(start_x=int(screenWidth / 2), start_y=int(screenHeight * 0.7), end_x=int(screenWidth / 2), end_y=int(screenHeight * 0.4), duration=500)
    time.sleep(1)


def scrollDown2(element):
    wdr = get_wd()
    deviceSize = wdr.get_window_size()
    screenHeight = deviceSize['height']
    if not find(element):
        saveLog("FAIL -> Scroll 을 하기 위한 element 가 보이지 않습니다.")
    appiumby = get_appiumby(element)
    rect = wdr.find_element(appiumby, element).rect

    center_x = rect['x'] + rect['width'] // 2
    center_y = rect['y'] + rect['height'] // 2

    wdr.swipe(start_x=int(center_x), start_y=int(center_y), end_x=int(center_x),  end_y=int(screenHeight * 0.1), duration=500)
    time.sleep(1)


def scrollUp():
    wdr = get_wd()
    deviceSize = wdr.get_window_size()
    screenWidth = deviceSize['width']
    screenHeight = deviceSize['height']
    wdr.swipe(start_x=int(screenWidth / 2), start_y=int(screenHeight * 0.2), end_x=int(screenWidth / 2), end_y=int(screenHeight * 0.7), duration=500)
    time.sleep(1)


def scrollUp2(element):
    wdr = get_wd()
    deviceSize = wdr.get_window_size()
    screenHeight = deviceSize['height']
    if not find(element):
        saveLog("FAIL -> Scroll 을 하기 위한 element 가 보이지 않습니다.")
    appiumby = get_appiumby(element)
    rect = wdr.find_element(appiumby, element).rect

    center_x = rect['x'] + rect['width'] // 2
    center_y = rect['y'] + rect['height'] // 2

    wdr.swipe(start_x=int(center_x), start_y=int(center_y), end_x=int(center_x),  end_y=int(screenHeight), duration=500)
    time.sleep(1)


def scrollLeft():
    wdr = get_wd()
    deviceSize = wdr.get_window_size()
    screenWidth = deviceSize['width']
    screenHeight = deviceSize['height']
    wdr.swipe(start_x=int(screenWidth * 0.2), start_y=int(screenHeight / 2), end_x=int(screenWidth * 0.7), end_y=int(screenHeight / 2), duration=500)
    time.sleep(1)


def scrollRight():
    wdr = get_wd()
    deviceSize = wdr.get_window_size()
    screenWidth = deviceSize['width']
    screenHeight = deviceSize['height']
    wdr.swipe(start_x=int(screenWidth * 0.7), start_y=int(screenHeight / 2), end_x=int(screenWidth * 0.2), end_y=int(screenHeight / 2), duration=500)
    time.sleep(1)


def scrollDown_LAND():
    # LANDSCAPE 모드 아래쪽 스크롤
    wdr = get_wd()
    deviceSize = wdr.get_window_size()
    screenWidth = deviceSize['width']
    screenHeight = deviceSize['height']
    wdr.swipe(start_y=int(screenWidth * 0.6), start_x=int(screenHeight / 2), end_y=int(screenWidth * 0.1), end_x=int(screenHeight / 2), duration=500)
    time.sleep(1)


def find_scroll_Down(a, b):
    # a: 찾고 싶은 element, b: 스크롤 할 layout
    for i in range(10):
        if find(a, ex=True):
            break
        scrollDown2(b)


def long_press(pram, one_sec=False):
    wdr = get_wd()
    if not find(pram):
        return False
    try:
        appiumby = get_appiumby(pram)
        rect = wdr.find_element(appiumby, pram).rect

        center_x = rect['x'] + rect['width'] // 2
        center_y = rect['y'] + rect['height'] // 2

        finger = PointerInput(interaction.POINTER_TOUCH, "finger")
        actions = ActionBuilder(wdr, mouse=finger)

        actions.pointer_action.move_to_location(center_x, center_y)
        actions.pointer_action.pointer_down()
        if one_sec:
            actions.pointer_action.pause(1)
        else:
            actions.pointer_action.pause(2)
        actions.pointer_action.pointer_up()

        actions.perform()
    except (Exception,):
        return False
    return True


def quickpanel():
    # 퀵패널 열기
    wdr = get_wd()
    deviceSize = wdr.get_window_size()
    screenWidth = deviceSize['width']
    wdr.swipe(start_x=int(screenWidth - 10), start_y=int(0), end_x=int(screenWidth - 10), end_y=int(400), duration=500)


def noti_bar():
    # 알림바 열기
    wdr = get_wd()
    wdr.swipe(start_x=int(10), start_y=int(0), end_x=int(10), end_y=int(400), duration=500)


def wait(pram):
    # 해당 값이 나올 때까지 최대 2분 30초 대기
    wdr = get_wd()
    appiumby = get_appiumby(pram)
    for k in range(15):
        time.sleep(3)
        try:
            t = wdr.find_element(appiumby, pram).is_displayed()
        except (Exception,):
            t = False
        if t:
            return t
    return False


# ── 페이지 / 모듈 ─────────────────────────────────────────────────────────────

def page_entry(page_name):
    check_file_path = "//10.254.245.50/sqe2_2/■ SmartThings/자동화 ST/00. TEST_LOG/page_entry_check.py"
    page_name = page_name.lower()
    page_name = page_name.replace(" ", "_")
    page_name = page_name.replace("'", "")
    wdr = get_wd()
    module_name = "page_entry"

    try:
        spec = importlib.util.spec_from_file_location(module_name, check_file_path)
        dynamic_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(dynamic_module)
    except ImportError:
        raise ImportError(f"{check_file_path} 파일을 찾을 수 없습니다")

    if not hasattr(dynamic_module, page_name):
        print(f"{page_name} 진입 확인 함수 추가 필요")
    else:
        getattr(dynamic_module, page_name)(wdr)


def module(module_name: str, args=()):
    base_dir = os.path.join(application_path, "moduler")

    module_path = f"{base_dir}\\{module_name}.py"
    spec = importlib.util.spec_from_file_location("dynamic_module", module_path)
    module1 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module1)
    wdr = get_wd()

    if not hasattr(module1, "run"):
        raise AttributeError(f"{module_path} 모듈에 run() 함수가 없습니다")

    return module1.run(wdr, *args)


def popup_entry(path):
    module("popup", args=(path,))


def is_mobile():
    wdr = get_wd()

    device = wdr.execute_script(
        'mobile: shell',
        {
            'command': 'getprop',
            'args': ['ro.build.characteristics']
        }
    )
    if 'tablet' in device.lower():
        return False

    return True
