import os
import json
from typing import List, Any, Optional
import gspread
from google.auth import default
from google.oauth2.service_account import Credentials
from .config import (
    SCOPES,
    SPREADSHEET_ID,
    TEMPLATE_SHEET_NAME,
    REPORT_SHEET_NAME,
)


def get_gspread_client(credentials_path="service_account.json") -> gspread.Client:
    """
    Khởi tạo và xác thực kết nối với Google Sheets API linh hoạt từ nhiều nguồn:
      1. Biến môi trường GOOGLE_CREDENTIALS, GCP_SA_KEY, GCP_CREDENTIALS_JSON:
         - Hỗ trợ cả dạng đường dẫn file (vd: service_account.json)
         - Hỗ trợ cả dạng chuỗi JSON thô (khi chạy trên CI/CD)
      2. File credentials trên ổ đĩa (service_account.json, gcp-credentials.json, credentials.json)
      3. Google default application credentials
    """
    # 1. Đọc từ biến môi trường
    env_cred = (
        os.getenv("GOOGLE_CREDENTIALS")
        or os.getenv("GCP_SA_KEY")
        or os.getenv("GCP_CREDENTIALS_JSON")
    )
    if env_cred:
        clean_cred = env_cred.strip()
        # Trường hợp 1A: Biến môi trường là chuỗi JSON thô
        if clean_cred.startswith("{"):
            try:
                info = json.loads(clean_cred)
                creds = Credentials.from_service_account_info(info, scopes=SCOPES)
                print("✅ Đã nạp Google credentials từ chuỗi JSON trong biến môi trường.")
                return gspread.authorize(creds)
            except Exception as e:
                print(f"⚠️ Lỗi đọc credentials từ JSON trong biến môi trường: {e}")
        # Trường hợp 1B: Biến môi trường là đường dẫn file (vd: GOOGLE_CREDENTIALS=service_account.json)
        elif os.path.exists(clean_cred):
            try:
                creds = Credentials.from_service_account_file(clean_cred, scopes=SCOPES)
                print(f"✅ Đã nạp Google credentials từ file theo biến môi trường: {clean_cred}")
                return gspread.authorize(creds)
            except Exception as e:
                print(f"⚠️ Lỗi đọc file credentials từ biến môi trường '{clean_cred}': {e}")

    # 2. Đọc từ danh sách file JSON cục bộ
    possible_paths = [
        credentials_path,
        "service_account.json",
        "gcp-credentials.json",
        "credentials.json",
        os.path.join(os.path.dirname(__file__), "..", credentials_path),
        os.path.join(os.path.dirname(__file__), "..", "service_account.json"),
        os.path.join(os.path.dirname(__file__), "..", "gcp-credentials.json"),
    ]

    for path in possible_paths:
        if path and os.path.exists(path):
            try:
                creds = Credentials.from_service_account_file(path, scopes=SCOPES)
                print(f"✅ Đã nạp Google credentials từ file: {path}")
                return gspread.authorize(creds)
            except Exception as e:
                print(f"⚠️ Lỗi đọc file credentials '{path}': {e}")

    # 3. Default credentials
    try:
        creds, _ = default()
        return gspread.authorize(creds)
    except Exception as e:
        raise FileNotFoundError(
            "Không thể kết nối Google Sheets API. "
            "Vui lòng thiết lập biến môi trường GOOGLE_CREDENTIALS / GCP_SA_KEY hoặc cung cấp file 'service_account.json'."
        ) from e


def fetch_sheet_rows(
    spreadsheet: gspread.Spreadsheet, sheet_name: str
) -> List[List[Any]]:
    """Lấy toàn bộ dữ liệu bảng tính từ sheet được chỉ định."""
    try:
        # Tìm worksheet không phân biệt hoa thường
        worksheet = None
        for ws in spreadsheet.worksheets():
            if ws.title.strip().lower() == sheet_name.strip().lower():
                worksheet = ws
                break

        if not worksheet:
            # Nếu không tìm thấy sheet theo tên, thử lấy sheet đầu tiên hoặc báo lỗi
            raise ValueError(
                f"Không tìm thấy sheet '{sheet_name}'. Các sheet hiện có: {[w.title for w in spreadsheet.worksheets()]}"
            )

        rows = worksheet.get_all_values()
        print(f"✅ Đã tải thành công {len(rows)} dòng từ sheet '{worksheet.title}'")
        return rows
    except Exception as e:
        print(f"❌ Lỗi khi đọc sheet '{sheet_name}': {e}")
        raise e


def load_report_content(
    spreadsheet_id: Optional[str] = None,
) -> List[List[Any]]:
    """
    Kết nối Google Sheets và chỉ đọc duy nhất dữ liệu từ sheet 'report'.
    """
    sheet_id = spreadsheet_id or SPREADSHEET_ID
    client = get_gspread_client()
    spreadsheet = client.open_by_key(sheet_id)
    print(f"✅ Đã mở bảng tính: {spreadsheet.title} (ID: {sheet_id})")

    report_rows = fetch_sheet_rows(spreadsheet, REPORT_SHEET_NAME)
    return report_rows


def load_sheets_content(
    spreadsheet_id: Optional[str] = None,
) -> tuple[List[List[Any]], List[List[Any]]]:
    """
    Kết nối Google Sheets và tải cả 2 sheet: 'template' và 'report'
    để gửi 1 message template và 1 message report lên Teams.
    """
    sheet_id = spreadsheet_id or SPREADSHEET_ID
    client = get_gspread_client()
    spreadsheet = client.open_by_key(sheet_id)
    print(f"✅ Đã mở bảng tính: {spreadsheet.title} (ID: {sheet_id})")

    template_rows = fetch_sheet_rows(spreadsheet, TEMPLATE_SHEET_NAME)
    report_rows = fetch_sheet_rows(spreadsheet, REPORT_SHEET_NAME)
    return template_rows, report_rows
