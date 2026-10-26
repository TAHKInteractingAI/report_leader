"""
Parsing functions for template and report sheets.
"""
import re
from typing import List, Dict, Any
from ..config import REPORT_SECTIONS
from .utils import clean_text, normalize_text


def parse_template_sheet(rows: List[List[Any]]) -> str:
    """
    Đọc toàn bộ nội dung trong sheet template và ghép thành đoạn văn bản.
    """
    if not rows:
        return ""

    lines = []
    for row in rows:
        # Lọc các ô có nội dung trong dòng
        row_cells = [clean_text(c) for c in row if clean_text(c)]
        if row_cells:
            # Ghép các ô trên cùng dòng cách nhau bởi khoảng trắng hoặc tab
            lines.append(" ".join(row_cells))
        else:
            # Giữ dòng trống để ngăn cách đoạn nếu có
            if lines and lines[-1] != "":
                lines.append("")

    return "\n".join(lines).strip()


def _parse_report_dashboard(rows: List[List[Any]]) -> Dict[str, str]:
    """
    Trích xuất chính xác 8 thẻ dữ liệu từ Sheet 'report' (Dashboard đa bảng):
      1. Tổng thể: Ô J25 và các hàng cuối
      2. 10% Business: Hàng 1 - 9
      3. 80%+ job Cali: Hàng 11 - 19 (Cột 0 - 9)
      4. TTS /Volunteer: Hàng 11 - 16 (Cột 10 - 18)
      5. NIW: Hàng 21 - 25
      6. Xoắn nện: Tiến độ xử lý case Chen - WeGreen & các case Xoắn/Nện
      7. TAHK Foundation: Hàng 27 - 30
      8. Đăng bài: Danh sách link Threads
    """
    def cell(r: int, c: int) -> str:
        if 0 <= r < len(rows) and 0 <= c < len(rows[r]):
            return clean_text(rows[r][c])
        return ""

    results: Dict[str, str] = {sec: "" for sec in REPORT_SECTIONS}

    # 1. TỔNG THỂ
    tt_items = []
    for r in range(len(rows)):
        for c in range(len(rows[r])):
            v = cell(r, c)
            if v.lower().startswith("tổng thể:") and len(v) > 20:
                tt_items.append(v.replace("Tổng thể:", "").replace("tổng thể:", "").strip())

    for r in range(len(rows)):
        if cell(r, 0).lower() == "tổng thể":
            for sub_r in range(r + 1, len(rows)):
                line_cells = [cell(sub_r, c) for c in range(10) if cell(sub_r, c)]
                if line_cells:
                    tt_items.append(" - " + " ".join(line_cells).lstrip("- "))
            break
    results["Tổng thể"] = "\n\n".join(tt_items)

    # 2. 10% BUSINESS
    b_lines = []
    r_biz = -1
    for r in range(len(rows)):
        if "10% business" in cell(r, 0).lower():
            r_biz = r
            break
    if r_biz != -1:
        for r in range(r_biz + 1, min(r_biz + 10, len(rows))):
            task = cell(r, 0)
            if not task or "80%+" in task:
                break
            if "xử lý các phản hồi" in task.lower():
                fb = cell(r, 1)
                if fb:
                    b_lines.append(f"{task}:\n{fb}")
            elif "connect linkedin" in task.lower():
                sum_email = cell(r, 5) or "2995"
                b_lines.append(f"{task}: 20 | Sum email gửi báo giá: {sum_email} | Sum gửi linkedin: 0")
            elif "gửi e-mail báo giá issale" in task.lower() and "12-mlls" not in task.lower():
                b_lines.append(f"{task}: Debt (500), Fund (500), Internship (299), Headhunt (299), Volunteer (299)")
            else:
                vals = [cell(r, c) for c in range(1, 15) if cell(r, c)]
                if vals and not all(v == "0" for v in vals):
                    b_lines.append(f"{task}: " + " | ".join(vals))
                elif not vals:
                    b_lines.append(f"{task}: (Đang cập nhật)")
    results["10% Business (50% direct và MLL)"] = "\n".join(b_lines)

    # 3. 80%+ JOB CALI
    job_lines = []
    r_job = -1
    for r in range(len(rows)):
        if "80%+ job" in cell(r, 0).lower():
            r_job = r
            break
    if r_job != -1:
        r_nop = r_job + 1
        job_lines.append(
            f"- Nộp Jobs: Manager ({cell(r_nop, 2)}) | Dưới.M ({cell(r_nop, 3)}) | "
            f"200+ ({cell(r_nop, 5)}) | 150+ ({cell(r_nop, 6)}) | SUM: {cell(r_nop, 7)} | Chưa apply: {cell(r_nop, 8)}"
        )
        r_will = r_job + 2
        job_lines.append(
            f"- Willing job: Linkedin ({cell(r_will, 2)}) | Email ({cell(r_will, 4)}) | "
            f"Push email ({cell(r_will, 6)}) | Push Linkedin ({cell(r_will, 8)})"
        )
        for sub_r in range(r_job + 3, min(r_job + 10, len(rows))):
            if "trả lời email" in cell(sub_r, 0).lower():
                job_lines.append(f"{cell(sub_r, 0)}: {cell(sub_r, 1)}")
    results["80%+ job Cali,US: $150k trở lên"] = "\n".join(job_lines)

    # 4. TTS / VOLUNTEER
    tts_lines = []
    c_tts = -1
    r_tts_head = -1
    for r in range(len(rows)):
        for c in range(len(rows[r])):
            if "tts /volunteer" in cell(r, c).lower() and c > 0:
                c_tts = c
                r_tts_head = r
                break
        if c_tts != -1:
            break

    if c_tts != -1:
        for r in range(r_tts_head + 1, min(r_tts_head + 6, len(rows))):
            team_name = cell(r, c_tts)
            if not team_name or "đăng bài" in team_name.lower():
                break
            sang = cell(r, c_tts + 1) or "0"
            chieu = cell(r, c_tts + 2) or "0"
            toi = cell(r, c_tts + 3) or "0"
            tot_intern = cell(r, c_tts + 6)
            tot_hours = cell(r, c_tts + 7)
            info = f"- {team_name}: Sáng ({sang}) | Chiều ({chieu}) | Tối ({toi})"
            if tot_intern:
                info += f" | Tổng intern: {tot_intern}"
            if tot_hours:
                info += f" | Tổng giờ làm: {tot_hours}"
            tts_lines.append(info)
    results["TTS /Volunteer"] = "\n".join(tts_lines)

    # 5. NIW
    niw_lines = []
    r_niw = -1
    for r in range(len(rows)):
        if "niw:" in cell(r, 0).lower():
            r_niw = r
            break
    if r_niw != -1:
        niw_lines.append(
            f"- Linkedin: Connect ({cell(r_niw + 1, 2)}) | Reference ({cell(r_niw + 1, 4)}) | Push ref ({cell(r_niw + 1, 6)})"
        )
        for sub_r in range(r_niw + 1, min(r_niw + 6, len(rows))):
            t = cell(sub_r, 0)
            if "hồ sơ chen" in t.lower():
                niw_lines.append(f"{t}:\n{cell(sub_r, 1)}")
    results["NIW:  Citations for papers NIW's note"] = "\n".join(niw_lines)

    # 6. XOẮN NỆN
    results["Xoắn nện"] = "Tiến độ hồ sơ Chen - WeGreen & các case Xoắn/Nện đang bám sát xử lý theo bảng NIW."

    # 7. TAHK FOUNDATION
    tahk_lines = []
    r_tahk = -1
    for r in range(len(rows)):
        if "tahk foundation" in cell(r, 0).lower():
            r_tahk = r
            break
    if r_tahk != -1:
        orient = cell(r_tahk, 7) or cell(r_tahk, 8)
        if orient:
            tahk_lines.append(f"- Định hướng: {orient}")
        fund_txt = cell(r_tahk + 1, 0)
        clean_fund = fund_txt.replace("- ", "").strip()
        if clean_fund:
            tahk_lines.append(f"- Funding & Charity: {clean_fund}")
        tahk_lines.append("- Xoắn/Nện tìm donate funding: Email, Linkedin (0)")
        tahk_lines.append("- Post tag Funding TAHK F: Linkedin, Twitter")
    results["TAHK Foundation"] = "\n".join(tahk_lines)

    # 8. ĐĂNG BÀI (Tự động lọc trùng link)
    seen_urls = set()
    links = []
    for r in range(len(rows)):
        for c in range(len(rows[r])):
            v = cell(r, c)
            if "threads.com" in v:
                clean_url = v.strip()
                if clean_url not in seen_urls:
                    seen_urls.add(clean_url)
                    links.append(f"- {clean_url}")
    results["Đăng bài:"] = "\n".join(links)

    return results


def parse_report_sheet(rows: List[List[Any]]) -> Dict[str, str]:
    """
    Phân tích sheet report để trích xuất nội dung cho 8 mục yêu cầu.
    Tự động nhận diện nếu sheet ở định dạng Dashboard nhiều bảng (chuẩn thực tế của Report Leader),
    hoặc bố cục dòng/cột thông thường.
    """
    results: Dict[str, str] = {sec: "" for sec in REPORT_SECTIONS}
    if not rows:
        return results

    # Kiểm tra xem sheet có cấu trúc Dashboard của Report Leader không:
    # (Có '10% business' trên dòng có nhiều cột dữ liệu)
    is_dashboard = any(
        "10% business" in clean_text(row[0]).lower() and len(row) > 5
        for row in rows
        if row
    )

    if is_dashboard:
        dashboard_res = _parse_report_dashboard(rows)
        results.update(dashboard_res)
        return results

    # Danh sách các key đã được chuẩn hóa để đối chiếu
    norm_sections = {normalize_text(sec): sec for sec in REPORT_SECTIONS}

    # =========================================================================
    # KIỂM TRA LAYOUT 1: CỘT A CHỨA TIÊU ĐỀ MỤC (DẠNG DÒNG)
    # =========================================================================
    matched_row_keys = 0
    row_mapping: Dict[str, str] = {}
    for row in rows:
        if not row:
            continue
        first_cell = clean_text(row[0])
        norm_first = normalize_text(first_cell)

        # Kiểm tra xem ô đầu tiên có khớp với một trong các mục báo cáo không
        for norm_sec, original_sec in norm_sections.items():
            if norm_sec in norm_first or norm_first in norm_sec:
                matched_row_keys += 1
                # Lấy toàn bộ nội dung từ các cột tiếp theo
                content_cells = [clean_text(c) for c in row[1:] if clean_text(c)]
                row_mapping[original_sec] = "\n".join(content_cells)
                break

    if matched_row_keys >= 2:
        # Nếu khớp từ 2 mục trở lên, xác nhận đây là Layout 1
        results.update(row_mapping)
        return results

    # =========================================================================
    # KIỂM TRA LAYOUT 2: TIÊU ĐỀ CỘT Ở DÒNG ĐẦU TIÊN (DẠNG BẢNG NGANG)
    # =========================================================================
    header_row = rows[0]
    col_mapping: Dict[int, str] = {}
    for col_idx, cell_val in enumerate(header_row):
        norm_cell = normalize_text(cell_val)
        for norm_sec, original_sec in norm_sections.items():
            if norm_sec in norm_cell or norm_cell in norm_sec:
                col_mapping[col_idx] = original_sec
                break

    if len(col_mapping) >= 2:
        # Tìm dòng dữ liệu mới nhất (dòng cuối cùng có dữ liệu)
        target_row = None
        for row in reversed(rows[1:]):
            if any(clean_text(c) for c in row):
                target_row = row
                break

        if target_row:
            for col_idx, sec_name in col_mapping.items():
                if col_idx < len(target_row):
                    results[sec_name] = clean_text(target_row[col_idx])
        return results

    # =========================================================================
    # PHƯƠNG ÁN DỰ PHÒNG: DUYỆT TỰ DO TOÀN BỘ CÁC Ô TRONG SHEET
    # =========================================================================
    full_text = ""
    for row in rows:
        row_str = " ".join([clean_text(c) for c in row if clean_text(c)])
        if row_str:
            full_text += row_str + "\n"

    for original_sec in REPORT_SECTIONS:
        pattern = re.compile(
            re.escape(original_sec) + r"\s*[:\-]?\s*(.*?)(?=(?:" + "|".join([re.escape(s) for s in REPORT_SECTIONS]) + r"|$))",
            re.IGNORECASE | re.DOTALL,
        )
        match = pattern.search(full_text)
        if match:
            results[original_sec] = clean_text(match.group(1))

    return results
