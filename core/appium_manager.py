import subprocess
import time
import urllib.request
import urllib.error


def _wait_for_appium(port_num, timeout=30):
    url = f"http://127.0.0.1:{port_num}/status"
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            urllib.request.urlopen(url, timeout=1)
            return
        except (urllib.error.URLError, OSError):
            time.sleep(0.5)
    raise TimeoutError(f"Appium 서버가 {timeout}초 내에 기동되지 않았습니다 (port: {port_num})")


def start_appium_server(port_num):
    cmd = f"appium -p {port_num} --session-override --log-level debug --relaxed-security"
    proc = subprocess.Popen(cmd, shell=True)
    _wait_for_appium(port_num)
    return proc