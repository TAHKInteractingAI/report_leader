import re
from typing import List, Dict, Any, Optional
from .config import REPORT_SECTIONS


def clean_text(val: Any) -> str:
    """Loại bỏ ký tự khoảng trắng thừa và ký tự non-breaking space."""
    if val is None:
        return ""
    text = str(val).replace("\xa0", " ").strip()
    return text


def normalize_text(text: str) -> str:
    """
    Chuẩn hóa chuỗi văn bản để so khớp tiêu đề không phân biệt hoa thường,
    dấu cách và dấu hai chấm.
    """
    text = clean_text(text).lower()
    text = re.sub(r"[\s_:\-\.,]+", " ", text).strip()
    return text


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


def compose_template_message(template_rows: List[List[Any]]) -> tuple[str, str]:
    """
    Ráp nội dung từ sheet 'template' theo định dạng văn bản (Text / Paragraphs)
    được căn chỉnh đẹp mắt, thụt lề rõ ràng, tách đoạn mạch lạc, có đường dẫn click được.
    Trả về tuple (html_template, text_template).
    """
    if not template_rows:
        return "", ""

    raw_lines = []
    for r in template_rows:
        for c in r:
            c_str = clean_text(c)
            if not c_str:
                continue
            # Tách các dòng bên trong mỗi ô nếu có xuống dòng
            for line in c_str.split("\n"):
                line_str = line.strip()
                if line_str:
                    raw_lines.append(line_str)

    html_lines = []
    text_lines = []

    for l in raw_lines:
        if l.startswith("---") or l.startswith("==="):
            html_lines.append('<hr style="border: 0; border-top: 1px dashed #cbd5e1; margin: 10px 0;" />')
            text_lines.append("----------------------------------------")
            continue

        # An toàn ký tự HTML
        safe_l = (
            l.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )
        url_pattern = re.compile(r'(https?://[^\s<]+)')
        safe_l = url_pattern.sub(r'<a href="\1" style="color: #2563eb; text-decoration: underline;">\1</a>', safe_l)

        if l.startswith("+ vd") or l.startswith("vd:"):
            html_lines.append(f'<div style="margin: 2px 0 2px 28px; color: #475569; font-style: italic; line-height: 1.55;">{safe_l}</div>')
            text_lines.append(l)
        elif l.startswith("+ "):
            html_lines.append(f'<div style="margin: 2px 0 2px 24px; color: #334155; line-height: 1.55;">{safe_l}</div>')
            text_lines.append(l)
        elif l.startswith("- "):
            html_lines.append(f'<div style="margin: 3px 0 3px 12px; color: #1e293b; line-height: 1.55;">{safe_l}</div>')
            text_lines.append(l)
        elif re.match(r"^\d+%\s+", l):
            html_lines.append(f'<div style="margin: 2px 0 2px 24px; color: #334155; line-height: 1.55;">{safe_l}</div>')
            text_lines.append(l)
        elif re.match(r"^\d+\.\s*WIN", l):
            html_lines.append(f'<div style="margin: 8px 0 3px 0; font-weight: normal; color: #1e293b; line-height: 1.55;">{safe_l}</div>')
            text_lines.append(l)
        elif "iHugeFreeEcosystemMoneyEvent" in l:
            html_lines.append(f'<div style="background-color: #f8fafc; border-left: 3px solid #6366f1; padding: 6px 10px; margin: 8px 0; font-size: 13px; color: #1e293b; line-height: 1.5;">{safe_l}</div>')
            text_lines.append(l)
        elif l.startswith("*") and l.endswith("*"):
            html_lines.append(f'<div style="margin: 10px 0 4px 0; color: #0f172a; line-height: 1.55;">{safe_l}</div>')
            text_lines.append(l)
        else:
            html_lines.append(f'<div style="margin: 4px 0; line-height: 1.55;">{safe_l}</div>')
            text_lines.append(l)

    full_tmpl_html = (
        '<div style="font-family: -apple-system, BlinkMacSystemFont, \'Segoe UI\', Roboto, Helvetica, Arial, sans-serif; '
        'font-size: 13px; color: #1f2937; margin-bottom: 16px;">\n'
        + "\n".join(html_lines)
        + "\n</div>"
    )
    full_tmpl_text = "\n".join(text_lines)

    return full_tmpl_html, full_tmpl_text


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
    for col_idx, cell in enumerate(header_row):
        norm_cell = normalize_text(cell)
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
        norm_sec = normalize_text(original_sec)
        pattern = re.compile(
            re.escape(original_sec) + r"\s*[:\-]?\s*(.*?)(?=(?:" + "|".join([re.escape(s) for s in REPORT_SECTIONS]) + r"|$))",
            re.IGNORECASE | re.DOTALL,
        )
        match = pattern.search(full_text)
        if match:
            results[original_sec] = clean_text(match.group(1))

    return results


def compose_table_leader_report(rows: List[List[Any]]) -> tuple[str, str]:
    """
    Ráp báo cáo theo bố cục bảng (Table Grid) và gom toàn bộ vào 1 tin nhắn duy nhất.
    Trả về tuple: (html_content, text_content)
    
    Đặc điểm:
      - Bố cục table HTML với border mảnh (#d1d5db) theo chuẩn giao diện Microsoft Teams.
      - Giữ nguyên các phần: Tổng thể, 10% Business, 80%+ job Cali, TTS /Volunteer,
        NIW: Citations for papers NIW's note - Xoắn nện, TAHK Foundation, Đăng bài.
      - Lọc trùng link Threads.
      - Tiêu đề gọn gàng, không dùng in đậm markdown (**) hay emoji rườm rà.
    """
    def cell(r: int, c: int) -> str:
        if 0 <= r < len(rows) and 0 <= c < len(rows[r]):
            return clean_text(rows[r][c])
        return ""

    td = "border: 1px solid #d1d5db; padding: 4px 8px; vertical-align: top;"
    th = "border: 1px solid #d1d5db; padding: 4px 8px; background-color: #f3f4f6; text-align: left; font-weight: normal; vertical-align: top;"
    tbl = "border-collapse: collapse; width: 100%; border: 1px solid #d1d5db; margin-bottom: 12px; font-size: 13px;"

    # 1. TỔNG THỂ (DẠNG TABLE)
    raw_tt = ""
    for r in range(len(rows)):
        for c in range(len(rows[r])):
            v = cell(r, c)
            if v.lower().startswith("tổng thể:") and len(v) > 20:
                raw_tt += v.replace("Tổng thể:", "").replace("tổng thể:", "").strip() + "\n"

    for r in range(len(rows)):
        if cell(r, 0).lower() == "tổng thể":
            for sub_r in range(r + 1, len(rows)):
                line = [cell(sub_r, c) for c in range(10) if cell(sub_r, c)]
                if line:
                    raw_tt += " - " + " | ".join(line).lstrip("- ") + "\n"
            break

    tt_rows = []
    for line in raw_tt.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("- ") or line.startswith("+ "):
            bullet_text = line.lstrip("-+ ").strip()
            if ":" in bullet_text and len(bullet_text.split(":", 1)[0]) < 30:
                topic, detail = bullet_text.split(":", 1)
                tt_rows.append((topic.strip(), detail.strip()))
            else:
                tt_rows.append(("-", bullet_text))
        else:
            if tt_rows:
                last_top, last_det = tt_rows[-1]
                tt_rows[-1] = (last_top, last_det + "\n" + line)
            else:
                tt_rows.append(("-", line))

    tt_html = f'<table border="1" style="{tbl}">'
    tt_html += f'<tr><th style="{th}; width: 25%;">Tổng thể</th><th style="{th}">Chi tiết / Tiến độ</th></tr>'
    for top, det in tt_rows:
        tt_html += f'<tr><td style="{td}">{top}</td><td style="{td}; white-space: pre-wrap;">{det}</td></tr>'
    tt_html += "</table>"

    # 2. 10% BUSINESS
    b_html = f'<p style="margin: 0 0 4px 0;">10% Business (50% direct và MLL)</p><table border="1" style="{tbl}">'
    header_cols = [cell(0, c) for c in range(14) if cell(0, c)]
    if not header_cols:
        header_cols = ["10% Business (50% direct và MLL)"]
    b_html += "<tr>" + "".join(f'<th style="{th}">{h}</th>' for h in header_cols) + "</tr>"
    for r in range(1, 9):
        task = cell(r, 0)
        if not task:
            continue
        if r == 7:
            b_html += f'<tr><td style="{td}">{task}</td><td colspan="{max(1, len(header_cols)-1)}" style="{td}; white-space: pre-wrap;">{cell(r, 1)}</td></tr>'
        elif r == 6:
            b_html += (
                f'<tr><td style="{td}">{task}</td>'
                f'<td style="{td}">20</td>'
                f'<td colspan="3" style="{td}">Sum email gửi báo giá: {cell(r, 5)}</td>'
                f'<td colspan="4" style="{td}">Sum gửi báo giá linkedin: {cell(r, 8)}</td>'
                f'<td colspan="4" style="{td}">Push Fundraising service: {cell(r, 12)}</td></tr>'
            )
        else:
            vals = [cell(r, c) for c in range(1, len(header_cols))]
            if not any(vals):
                b_html += f'<tr><td colspan="{len(header_cols)}" style="{td}">{task}</td></tr>'
            else:
                b_html += f'<tr><td style="{td}">{task}</td>' + "".join(f'<td style="{td}">{v}</td>' for v in vals) + "</tr>"
    b_html += "</table>"

    # 3. 80%+ JOB CALI
    j_html = f'<p style="margin: 0 0 4px 0;">80%+ job Cali,US: $150k trở lên</p><table border="1" style="{tbl}">'
    j_header = [cell(10, c) for c in range(9) if cell(10, c)]
    if not j_header:
        j_header = ["80%+ job Cali,US: $150k trở lên"]
    j_html += "<tr>" + "".join(f'<th style="{th}">{h}</th>' for h in j_header) + "</tr>"
    j_html += '<tr><td style="' + td + '">' + cell(11, 0) + '</td>' + "".join(f'<td style="{td}">{cell(11, c)}</td>' for c in range(1, 9)) + "</tr>"
    j_html += '<tr><td style="' + td + '">' + cell(12, 0) + '</td>' + "".join(f'<td style="{td}">{cell(12, c)}</td>' for c in range(1, 9)) + "</tr>"
    j_html += f'<tr><td colspan="9" style="{td}">{cell(13, 0)}</td></tr>'
    j_html += "<tr>" + "".join(f'<th style="{th}">{cell(14, c)}</th>' for c in range(7)) + f'<td colspan="2" style="{td}"></td></tr>'
    j_html += f'<tr><td style="{td}">{cell(15, 0)}</td><td style="{td}">{cell(15, 1)}</td><td style="{td}">{cell(15, 2)}</td><td colspan="6" style="{td}"></td></tr>'
    j_html += f'<tr><td style="{td}">{cell(16, 0)}</td><td style="{td}">{cell(16, 1)}</td><td style="{td}">{cell(16, 2)}</td><td style="{td}">{cell(16, 3)}</td><td colspan="5" style="{td}"></td></tr>'
    j_html += f'<tr><td style="{td}">{cell(17, 0)}</td><td style="{td}">{cell(17, 1)}</td><td colspan="7" style="{td}"></td></tr>'
    j_html += f'<tr><td style="{td}">{cell(18, 0)}</td><td colspan="8" style="{td}">{cell(18, 1)}</td></tr>'
    j_html += "</table>"

    # 4. TTS / VOLUNTEER
    tts_html = f'<p style="margin: 0 0 4px 0;">TTS /Volunteer</p><table border="1" style="{tbl}">'
    tts_header = [cell(10, c) for c in range(10, 18) if cell(10, c)]
    if not tts_header:
        tts_header = ["TTS /Volunteer", "Sáng", "Chiều", "Tối", "Tổng intern", "Tổng giờ làm"]
    tts_html += "<tr>" + "".join(f'<th style="{th}">{h}</th>' for h in tts_header) + "</tr>"
    for r in [11, 12, 13]:
        row_vals = [cell(r, c) for c in range(10, 10 + len(tts_header))]
        tts_html += "<tr>" + "".join(f'<td style="{td}">{v}</td>' for v in row_vals) + "</tr>"
    tts_html += "</table>"

    # 5. NIW & XOẮN NỆN
    niw_html = f'<p style="margin: 0 0 4px 0;">NIW: Citations for papers NIW\'s note - Xoắn nện</p><table border="1" style="{tbl}">'
    niw_html += f'<tr><td style="{td}">{cell(21, 0)}</td><td style="{td}">{cell(21, 1)}</td><td style="{td}">{cell(21, 2)}</td><td style="{td}">{cell(21, 3)}</td><td style="{td}">{cell(21, 4)}</td><td style="{td}">{cell(21, 5)}</td><td style="{td}">{cell(21, 6)}</td></tr>'
    niw_html += f'<tr><td style="{td}">{cell(22, 0)}</td><td style="{td}">{cell(22, 1)}</td><td colspan="5" style="{td}">{cell(22, 3)}</td></tr>'
    niw_html += f'<tr><td colspan="7" style="{td}">{cell(23, 0)}</td></tr>'
    niw_html += f'<tr><td style="{td}">{cell(24, 0)}</td><td colspan="6" style="{td}; white-space: pre-wrap;">{cell(24, 1)}</td></tr>'
    niw_html += "</table>"

    # 6. TAHK FOUNDATION
    tahk_html = f'<p style="margin: 0 0 4px 0;">TAHK Foundation</p><table border="1" style="{tbl}">'
    tahk_html += f'<tr><td style="{td}">{cell(26, 0)}</td><td colspan="5" style="{td}"></td><td style="{td}">{cell(26, 7)}</td></tr>'
    tahk_html += f'<tr><td colspan="7" style="{td}">{cell(27, 0)}</td></tr>'
    tahk_html += f'<tr><td style="{td}">{cell(28, 0)}</td><td style="{td}">{cell(28, 1)}</td><td style="{td}"></td><td style="{td}">{cell(28, 3)}</td><td style="{td}">{cell(28, 4)}</td><td colspan="2" style="{td}"></td></tr>'
    tahk_html += f'<tr><td style="{td}">{cell(29, 0)}</td><td style="{td}">{cell(29, 1)}</td><td style="{td}"></td><td style="{td}">{cell(29, 3)}</td><td colspan="3" style="{td}"></td></tr>'
    tahk_html += "</table>"

    # 7. ĐĂNG BÀI (DẠNG TABLE & TỰ ĐỘNG LỌC TRÙNG LINK THREADS)
    seen_urls = set()
    post_items = []
    for r in range(len(rows)):
        for c in range(len(rows[r])):
            v = cell(r, c)
            if "threads.com" in v:
                u = v.strip()
                if u not in seen_urls:
                    seen_urls.add(u)
                    handle = u.split("@")[-1].rstrip("/") if "@" in u else u
                    post_items.append((handle, u))

    post_html = f'<table border="1" style="{tbl}">'
    post_html += f'<tr><th style="{th}; width: 35%;">Đăng bài:</th><th style="{th}">Link bài đăng Threads</th></tr>'
    for h, u in post_items:
        post_html += f'<tr><td style="{td}">@{h}</td><td style="{td}"><a href="{u}">{u}</a></td></tr>'
    post_html += "</table>"

    # GOM TOÀN BỘ BÁO CÁO VÀO 1 TIN NHẮN DUY NHẤT (100% CẤU TRÚC TABLE)
    html_report = f"""<div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; font-size: 13px; color: #242424; line-height: 1.5;">
  {tt_html}
  {b_html}
  {j_html}
  {tts_html}
  {niw_html}
  {tahk_html}
  {post_html}
</div>""".strip()

    # Tạo bản plain-text tương ứng
    dashboard_res = _parse_report_dashboard(rows)
    text_report = compose_leader_report(dashboard_res)

    return html_report, text_report


def compose_full_single_message(
    template_rows: List[List[Any]], report_rows: List[List[Any]]
) -> tuple[str, str]:
    """
    Gom toàn bộ nội dung thành 1 tin nhắn duy nhất:
      - Phần trên: Template (sheet 'template')
      - Phần dưới: Report Leader (sheet 'report' - 100% bố cục Table)
    Trả về tuple (html_content, text_content).
    """
    html_template, text_template = compose_template_message(template_rows)
    html_report, text_report = compose_table_leader_report(report_rows)

    combined_html = f"""<div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; font-size: 13px; color: #242424; line-height: 1.5;">
  {html_template}
  <hr style="border: none; border-top: 2px solid #e1dfdd; margin: 20px 0;" />
  {html_report}
</div>""".strip()

    combined_text = f"{text_template}\n\n" + ("=" * 60) + f"\n\n{text_report}".strip()

    return combined_html, combined_text


def compose_leader_report(
    report_sections: Any,
    template_content: Optional[Any] = None,
) -> str:
    """
    Ráp nội dung báo cáo hoàn chỉnh chỉ lấy từ Sheet 'report' theo đúng thứ tự 8 mục:
      1. Tổng thể
      2. 10% Business (50% direct và MLL)
      3. 80%+ job Cali,US: $150k trở lên
      4. TTS /Volunteer
      5. NIW:  Citations for papers NIW's note
      6. Xoắn nện
      7. TAHK Foundation
      8. Đăng bài:
    (Đã loại bỏ logic lấy từ template)
    """
    # Hỗ trợ cả trường hợp gọi theo định dạng cũ: compose_leader_report(template, report_sections)
    if isinstance(report_sections, str) and isinstance(template_content, dict):
        report_sections = template_content

    if not isinstance(report_sections, dict):
        report_sections = {}

    report_parts = []
    for section in REPORT_SECTIONS:
        content = (report_sections.get(section) or "").strip()
        header = section
        if content:
            # Nếu dòng đầu của content đã chứa tên section, loại bỏ để tránh lặp
            lines = content.splitlines()
            first_line_norm = normalize_text(lines[0])
            sec_norm = normalize_text(section)
            if sec_norm in first_line_norm or first_line_norm in sec_norm:
                clean_body = "\n".join(lines[1:]).strip()
            else:
                clean_body = content

            if clean_body:
                report_parts.append(f"{header}\n{clean_body}")
            else:
                report_parts.append(header)
        else:
            report_parts.append(f"{header}\n(Chưa có cập nhật)")

    return "\n\n".join(report_parts).strip()


def split_report_into_messages(text: str, max_chars: int = 2500) -> List[str]:
    """
    Chia nhỏ văn bản báo cáo thành nhiều tin nhắn riêng biệt để gửi lên Teams:
      - Ưu tiên tách theo các đường kẻ phân cách (---, ===, ___)
      - Nén các dòng trống liên tiếp
      - Nếu một phân đoạn vẫn dài hơn max_chars (mặc định 2500 ký tự), tự động chia nhỏ theo từng đoạn (\n\n)
    """
    text = (text or "").strip()
    if not text:
        return []

    # 1. Tách theo đường phân cách (---, ===, ___)
    raw_blocks = [b.strip() for b in re.split(r'\n\s*[-=_]{3,}\s*\n', text) if b.strip()]
    if not raw_blocks:
        raw_blocks = [text]

    final_messages = []
    for block in raw_blocks:
        # Nén nhiều dòng trống liên tiếp
        cleaned_block = re.sub(r'\n{3,}', '\n\n', block).strip()
        if not cleaned_block:
            continue

        if len(cleaned_block) <= max_chars:
            final_messages.append(cleaned_block)
        else:
            # Nếu phân đoạn quá dài, chia nhỏ theo đoạn (\n\n)
            paragraphs = cleaned_block.split('\n\n')
            current_chunk = []
            current_len = 0
            for p in paragraphs:
                p_str = p.strip()
                if not p_str:
                    continue
                if current_len + len(p_str) + 2 > max_chars and current_chunk:
                    final_messages.append('\n\n'.join(current_chunk))
                    current_chunk = [p_str]
                    current_len = len(p_str)
                else:
                    current_chunk.append(p_str)
                    current_len += len(p_str) + 2
            if current_chunk:
                final_messages.append('\n\n'.join(current_chunk))

    return final_messages
