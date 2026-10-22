import os
import sys
import time
import datetime
from pathlib import Path

# Thêm thư mục gốc vào PYTHONPATH nếu chạy trực tiếp file
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.config import (
    get_hcm_now,
    TEAMS_CHAT,
    SPREADSHEET_ID,
)
from src.sheets import load_sheets_content, load_report_content
from src.composer import (
    parse_report_sheet,
    compose_leader_report,
    compose_table_leader_report,
    compose_template_message,
    compose_full_single_message,
    split_report_into_messages,
)
from src.teams import login, open_chat, send_message


def run_report_leader():
    """Quy trình tổng thể lấy dữ liệu và gửi 1 tin nhắn duy nhất (trên Template, dưới Report Table) lên Teams."""
    now_hcm = get_hcm_now()
    now_utc = datetime.timezone.utc

    print("=" * 70)
    print("🚀 BẮT ĐẦU CHẠY BOT TỰ ĐỘNG GỬI REPORT LEADER LÊN MS TEAMS")
    print(f" - Giờ Việt Nam (HCM)       : {now_hcm.strftime('%Y-%m-%d %H:%M:%S %Z%z')}")
    print(f" - Bảng tính Google Sheets  : {SPREADSHEET_ID}")
    print(f" - Nhóm Teams đích          : {TEAMS_CHAT}")
    print("=" * 70)

    # 1. TẢI VÀ RÁP NỘI DUNG TỪ GOOGLE SHEETS (GOM THÀNH 1 MESSAGE: TRÊN TEMPLATE, DƯỚI REPORT TABLE)
    print("\n[Bước 1/3] Đang tải dữ liệu từ Google Sheets (sheet 'template' & sheet 'report')...")
    try:
        template_rows, report_rows = load_sheets_content()
        html_msg, text_msg = compose_full_single_message(template_rows, report_rows)

        print("\n" + "-" * 50)
        print("📦 BÁO CÁO GOM TOÀN BỘ VÀO 1 TIN NHẮN DUY NHẤT:")
        print(" - Phần trên : Template (sheet 'template')")
        print(" - Phần dưới : Report Leader (sheet 'report' - 100% bố cục Table Grid)")
        print(f" - Tổng kích thước HTML : {len(html_msg)} ký tự")
        print(f" - Tổng kích thước Text : {len(text_msg)} ký tự ({len(text_msg.splitlines())} dòng)")
        print("-" * 50 + "\n")

    except Exception as e:
        print(f"❌ Lỗi nghiêm trọng khi đọc hoặc ráp dữ liệu Google Sheets: {e}")
        raise e

    # 2. ĐĂNG NHẬP MICROSOFT TEAMS
    print("\n[Bước 2/3] Đang đăng nhập tài khoản Microsoft Teams...")
    driver = None
    max_login_attempts = 3
    for attempt in range(1, max_login_attempts + 1):
        print(f"👉 Thử đăng nhập lần {attempt}/{max_login_attempts}...")
        driver = login()
        if driver:
            break
        time.sleep(3)

    if not driver:
        print("❌ Đăng nhập Teams thất bại sau tất cả các lần thử!")
        sys.exit(1)

    # 3. MỞ NHÓM CHAT VÀ GỬI 1 TIN NHẮN DUY NHẤT
    print("\n[Bước 3/3] Đang điều hướng đến nhóm chat và gửi tin nhắn...")
    try:
        chat_opened = False
        max_open_attempts = 3
        for attempt in range(1, max_open_attempts + 1):
            print(f"👉 Thử mở nhóm '{TEAMS_CHAT}' lần {attempt}/{max_open_attempts}...")
            if open_chat(driver, TEAMS_CHAT):
                chat_opened = True
                break
            time.sleep(3)

        if not chat_opened:
            raise RuntimeError(
                f"Không thể mở nhóm chat '{TEAMS_CHAT}' sau {max_open_attempts} lần thử!"
            )

        # Gửi 1 tin nhắn duy nhất gồm cả Template (trên) và Report Table (dưới)
        print(f"📨 Đang gửi tin nhắn duy nhất (trên Template, dưới Report Table) vào nhóm '{TEAMS_CHAT}'...")
        success = send_message(driver, text_msg, html_content=html_msg)

        if success:
            print("🎉 BÁO CÁO LEADER (TRÊN TEMPLATE, DƯỚI REPORT TABLE) ĐÃ ĐƯỢC GỬI THÀNH CÔNG TRONG 1 TIN NHẮN DUY NHẤT!")
        else:
            raise RuntimeError("Gửi tin nhắn vào nhóm Teams thất bại!")

    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass
                print("🔒 Đã đóng trình duyệt Chrome.")
            except Exception:
                pass


if __name__ == "__main__":
    run_report_leader()
