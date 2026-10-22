# Report Leader MS Teams Bot

Hệ thống tự động hóa thu thập dữ liệu báo cáo từ Google Sheets, định dạng theo template chuẩn và gửi tin nhắn báo cáo định kỳ lên nhóm Microsoft Teams vào lúc **22:00 mỗi ngày (giờ Việt Nam - Asia/Ho_Chi_Minh)**.

---

## Luồng hoạt động

1. **Đọc dữ liệu từ Google Sheets:**
   * Bảng tính: `Report Leader` (ID: `1ix1D8qMD6DYTsCWtxevoUfBde8FP2vx_UF_bmKzFBng`)
   * Sheet `template`: Lấy toàn bộ nội dung template chuẩn đặt ở đầu báo cáo.
   * Sheet `report`: Trích xuất dữ liệu của 8 mục theo đúng thứ tự quy định.

2. **Quy tắc ráp nội dung tin nhắn (`src/composer.py`):**
   * **Phần 1:** Toàn bộ nội dung của sheet `template`.
   * **Phần 2:** Lần lượt 8 mục từ sheet `report`:
     1. `Tổng thể`
     2. `10% Business (50% direct và MLL)`
     3. `80%+ job Cali,US: $150k trở lên`
     4. `TTS /Volunteer`
     5. `NIW:  Citations for papers NIW's note`
     6. `Xoắn nện`
     7. `TAHK Foundation`
     8. `Đăng bài:`

3. **Gửi tin nhắn lên Microsoft Teams (`src/teams.py` & `src/browser.py`):**
   * Tự động đăng nhập tài khoản Microsoft Teams.
   * Điều hướng vào đúng nhóm chat: `iX000s iSSale gbBOSS AH*AU*cOL*YeuCauTop-iUp*KTra`.
   * Nhập nội dung, xuống dòng (`Shift + Enter`), gửi tin và chụp ảnh màn hình xác nhận.

---

## Triển khai tự động trên GitHub Actions

File workflow `.github/workflows/main.yml` đã được cài đặt sẵn:
- **Lịch chạy tự động:** 22:00 mỗi ngày giờ Việt Nam.
- **Chạy thủ công:** Vào tab **Actions** -> Chọn workflow **Report Leader Bot** -> Nhấn **Run workflow**.
- **Cấu hình Secrets trên GitHub:**
  * `GOOGLE_CREDENTIALS`: Nội dung file `gcp-credentials.json`
  * `TEAMS_EMAIL`: (tùy chọn, mặc định đã cài sẵn trong code)
  * `TEAMS_PASSWORD`: (tùy chọn, mặc định đã cài sẵn trong code)
  * `TEAMS_CHAT`: (tùy chọn)
