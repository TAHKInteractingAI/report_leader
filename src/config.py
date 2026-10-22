import os
import gc
import time
import datetime
try:
    import pytz
    LOCAL_TZ = pytz.timezone("Asia/Ho_Chi_Minh")
except ImportError:
    LOCAL_TZ = datetime.timezone(datetime.timedelta(hours=7))

try:
    from dotenv import load_dotenv, find_dotenv
    load_dotenv(find_dotenv())
except ImportError:
    pass

def get_hcm_now() -> datetime.datetime:
    """Trả về thời gian hiện tại theo múi giờ Hồ Chí Minh (UTC+7)."""
    return datetime.datetime.now(datetime.timezone.utc).astimezone(LOCAL_TZ)

# ==============================================================================
# MS TEAMS CONFIG
# ==============================================================================
TEAMS_EMAIL = os.getenv("TEAMS_EMAIL")
TEAMS_PASSWORD = os.getenv("TEAMS_PASSWORD")
TEAMS_CHAT = (
    os.getenv("TEAMS_CHAT")
    or "iX000s iSSale gbBOSS AH*AU*cOL*YeuCauTop-iUp*KTra"
)

# ==============================================================================
# GOOGLE SHEETS CONFIG
# ==============================================================================
SPREADSHEET_ID = (
    os.getenv("SPREADSHEET_ID")
    or "1ix1D8qMD6DYTsCWtxevoUfBde8FP2vx_UF_bmKzFBng"
)
TEMPLATE_SHEET_NAME = os.getenv("TEMPLATE_SHEET_NAME", "template")
REPORT_SHEET_NAME = os.getenv("REPORT_SHEET_NAME", "report")

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# ==============================================================================
# REPORT SECTIONS (THEO THỨ TỰ QUY ĐỊNH TẠI DESCRIPTION.MD)
# ==============================================================================
# Thứ tự:
# 1. Tổng thể
# 2. 10% Business (50% direct và MLL)
# 3. 80%+ job Cali,US: $150k trở lên
# 4. TTS /Volunteer
# 5. NIW: Citations for papers NIW's note
# 6. Xoắn nện
# 7. TAHK Foundation
# 8. Đăng bài:
REPORT_SECTIONS = [
    "Tổng thể",
    "10% Business (50% direct và MLL)",
    "80%+ job Cali,US: $150k trở lên",
    "TTS /Volunteer",
    "NIW:  Citations for papers NIW's note",
    "Xoắn nện",
    "TAHK Foundation",
    "Đăng bài:",
]
