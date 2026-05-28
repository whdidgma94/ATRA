import os

from appium import webdriver

_wd = None


def get_wd(udid=None, port=None, os_ver="", logdir="", system_port=None, desired_cap=None):
    global _wd
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

    if _wd is None:
        _wd = webdriver.Remote(f"http://127.0.0.1:{port}", desired_cap)
        _wd.implicitly_wait(10)

        if not os.path.exists(logdir):
            os.makedirs(logdir)
        if not os.path.exists(f"{logdir}/{os_ver}"):
            os.makedirs(f"{logdir}/{os_ver}")

    return _wd
