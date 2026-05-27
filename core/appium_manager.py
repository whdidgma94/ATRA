import subprocess
import time


def start_appium_server(port_num):
    cmd = f"appium -p {port_num} --session-override --log-level debug --relaxed-security"
    CREATE_NEW_CONSOLE = 0x00000010
    proc = subprocess.Popen(cmd, shell=True, creationflags=CREATE_NEW_CONSOLE)
    time.sleep(5)
    return proc