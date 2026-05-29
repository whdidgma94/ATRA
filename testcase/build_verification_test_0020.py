from main import find, saveLog

def run(wd):
    if not find("Map view"):
        saveLog("FAIL -> 맵뷰 확인 실패")
    