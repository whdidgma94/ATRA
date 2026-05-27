import os

from appium import webdriver

wd = None
file = None


def get_wd(udid=None, port=None, os_ver=0, logdir="",system_port=None, desired_cap=None):
    global wd
    global file
    if desired_cap is None:
        desired_cap = {
            "appium:deviceName": udid,
            "platformName": "Android",
            "appium:automationName": "UiAutomator2",
            "udid": udid,
            "newCommandTimeout": 600
        }

    if system_port:
        desired_cap["systemPort"] = system_port

    if wd is None:
        wd = webdriver.Remote(f"http://127.0.0.1:{port}", desired_cap)
        wd.implicitly_wait(10)

        if not os.path.exists(logdir):
            os.makedirs(logdir)
        if not os.path.exists(f"{logdir}/{os_ver}"):
            os.makedirs(f"{logdir}/{os_ver}")
        file = open(f"{logdir}/{os_ver}/log.txt", "a", encoding='utf-8')

    return wd