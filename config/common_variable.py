import os
import sys
from datetime import datetime

username = os.getlogin()
_NAS_BASE = os.environ.get(
    "ATRA_LOG_BASE",
    "//10.254.245.50/sqe2_2/■ SmartThings/자동화 ST/00. TEST_LOG/BVT"
)
_date_suffix = datetime.now().strftime('%m%d')
log_path = f"{_NAS_BASE}/ATRA_{_date_suffix}"
base_log_path = f"{_NAS_BASE}/ATRA_{_date_suffix}"
os_version_dic = {"11" : "ROS", "12" : "SOS", "13" : "TOS", "14" : "UOS", "15" : "VOS", "16" : "BOS", "17" : "COS"}
tcid = ""
device_model_map = {}

if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
    if hasattr(sys, "_MEIPASS") and sys._MEIPASS not in sys.path:
        sys.path.append(sys._MEIPASS)
else:
    application_path = os.path.dirname(os.path.dirname(__file__))