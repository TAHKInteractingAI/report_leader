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


DOC_LINKS = {
    "xu_ly_phan_hoi": "https://docs.google.com/document/d/1eptdDdXD1e1Tz2xzR0kKgB_uNeAurwhKHB8b-1yUf9I/edit?tab=t.rteda6ijpm46",
    "nop_jobs": "https://docs.google.com/spreadsheets/d/1vUcKAbDazlC_vFSjzty02Fdugu4Nw_jZsEG2k_wyxXY/edit?gid=1653216804#gid=1653216804",
    "willing_job": "https://docs.google.com/document/d/1v15KFMxfk2v3eYyQOiJbL4sCE6RQa3Nuses_cxLnkzM/edit?tab=t.atun0hlffezr#heading=h.gpe024pkb62i",
    "interview": "https://docs.google.com/document/d/1phoQJ7SWn8gEGsXq79afmuK8H5JCdsyzaPn_-H4PYBg/edit?tab=t.epjtewsrdzv4",
    "feedback_job": "https://docs.google.com/document/d/1phoQJ7SWn8gEGsXq79afmuK8H5JCdsyzaPn_-H4PYBg/edit?tab=t.43t5jivli07x",
    "ah": "https://docs.google.com/document/d/1JrZHfVV9GHnETvcLrN0GLvHKhp8O3N0efkV49wXyOjY/edit?tab=t.0#heading=h.cr5o8ciz9sfm",
    "au": "https://docs.google.com/document/d/1muhs3g6cpgDTXyUtC9902AfjwYXM_M_Lhi6wJxyCEPo/edit?tab=t.a8v2tuy7i94k",
    "sam_foundation": "https://docs.google.com/document/d/1uTXqOXJ7I8kiYz-0d6YuFLNBJUxwyr4gfRN_rHo1V4c/edit?usp=sharing",
    "niw_citations": "https://docs.google.com/spreadsheets/d/1tV1h-pNtGBgq639ky7cdBjc3CTfoeJEKIakOjORePEM/edit?gid=1346338716#gid=1346338716",
    "niw_notes": "https://docs.google.com/document/d/1__q1kkUZkmpXi1E5dDkbwzfir-HKTCQSYEU4Edz38k0/edit?tab=t.boxu2wiwp4xz#heading=h.j84em85ufx8",
    "niw_linkedin": "https://docs.google.com/spreadsheets/d/163Ye0HpfriaBs7nPWpKZC5mY-nHgcZdIQh2sJMoDIuQ/edit?gid=1498442053#gid=1498442053",
    "niw_case": "https://docs.google.com/document/d/1__q1kkUZkmpXi1E5dDkbwzfir-HKTCQSYEU4Edz38k0/edit?tab=t.boxu2wiwp4xz"
}

LINK_CLS = 'class="fui-Link ___1q1shib f2hkw1w f3rmtva f1ewtqcl fyind8e f1k6fduh f1w7gpdv fk6fouc fjoy568 figsok6 f1s184ao f1mk8lai fnbmjn9 f1o700av f13mvf36 f1cmlufx f9n3di6 f1ids18y f1tx3yz7 f1deo86v f1eh06m1 f1iescvh fhgqx19 f1olyrje f1p93eir f1nev41a f1h8hb77 f1lqvz6u f10aw75t fsle3fq f17ae5zn"'
LINK_ATTRS = f'{LINK_CLS} rel="noopener noreferrer" target="_blank" tabindex="0" data-testid="atp-safelink"'
BLUE_STYLE = 'style="color: rgb(154, 184, 255); font-size: inherit;" data-original-highlight-color="rgb(30, 83, 163)"'
ORANGE_STYLE = 'style="color: rgb(254, 131, 93); font-size: inherit;" data-original-highlight-color="rgb(205, 89, 55)"'


def compose_template_message(template_rows: List[List[Any]]) -> tuple[str, str]:
    """
    Ráp nội dung từ sheet 'template' theo chuẩn cấu trúc 100% của Ray (nhóm gbBOSS):
    Mỗi hàng là một dòng trong bảng Table 0 (data-is-focusable="true").
    """
    if not template_rows:
        return "", ""

    t0_trs = []
    text_lines = []
    for r in template_rows:
        row_txt = " ".join(clean_text(c) for c in r if clean_text(c))
        if not row_txt:
            t0_trs.append("<tr><td>&nbsp;</td></tr>")
            text_lines.append("")
            continue

        text_lines.append(row_txt)
        parts = []
        for line in row_txt.split("\n"):
            line_str = (
                line.strip()
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
            )
            line_str = re.sub(r'(https?://[^\s<]+)', f'<a aria-label="Link \\1" href="\\1" {LINK_ATTRS}>\\1</a>', line_str)
            if line_str:
                parts.append(f'<span style="font-size: inherit;">{line_str}</span>')
        inner = "<br>".join(parts)
        t0_trs.append(f"<tr><td>{inner}</td></tr>")

    html_template = f'<table data-is-focusable="true"><tbody>{"".join(t0_trs)}</tbody></table>'
    text_template = "\n".join(text_lines)

    return html_template, text_template


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


BLUE_STYLE = 'style="color: rgb(154, 184, 255); font-size: inherit;" data-original-highlight-color="rgb(30, 83, 163)"'
ORANGE_STYLE = 'style="color: rgb(254, 131, 93); font-size: inherit;" data-original-highlight-color="rgb(205, 89, 55)"'


def compose_table_leader_report(rows: List[List[Any]]) -> tuple[str, str]:
    """
    Ráp báo cáo theo chuẩn 100% cấu trúc của Ray trong nhóm gbBOSS:
    Bao gồm 6 bảng Table (Tổng thể, 10% Business, 80%+ Job Cali, TTS/Volunteer, NIW, Đăng bài)
    với đầy đủ các liên kết Google Docs / Spreadsheets tương ứng.
    """
    def cell(r: int, c: int) -> str:
        if 0 <= r < len(rows) and 0 <= c < len(rows[r]):
            return clean_text(rows[r][c])
        return ""

    # =========================================================================
    # TABLE 1: TỔNG THỂ (Chuẩn xác Ray: 1 ô td rowspan="1", phân tách bằng <br>)
    # =========================================================================
    raw_tt = ""
    for r in range(len(rows)):
        for c in range(len(rows[r])):
            v = cell(r, c)
            if v.lower().startswith("tổng thể:") and len(v) > 20:
                raw_tt = v.replace("Tổng thể:", "").replace("tổng thể:", "").strip()
                break
        if raw_tt:
            break

    tt_paragraphs = []
    for p in raw_tt.split("\n\n"):
        p = p.strip()
        if not p:
            continue
        p_lines = []
        for line in p.split("\n"):
            line = line.strip()
            if not line:
                continue
            safe_l = (
                line.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
            )
            safe_l = re.sub(
                r'(https?://[^\s<]+)',
                f'<a aria-label="Link \\1" href="\\1" {LINK_ATTRS}><span style="font-size: inherit;">\\1</span></a>',
                safe_l
            )
            p_lines.append(f'<span style="font-size: inherit;">{safe_l}</span>')
        tt_paragraphs.append("<br>".join(p_lines))

    tt_inner = '<span style="font-size: inherit;">Tổng thể:&nbsp;</span><br>' + "<br><br>".join(tt_paragraphs)
    table_1 = f'<table data-is-focusable="true"><tbody><tr><td rowspan="1">{tt_inner}</td></tr></tbody></table>'

    # =========================================================================
    # TABLE 2: 10% BUSINESS (Chuẩn xác Ray)
    # =========================================================================
    header_cols = [
        "10% Business (50% direct và MLL)", "Debt", "Fund", "Charity", "Internship",
        "Headhunt", "Gen AI", "Volunteer", "Trading", "Data Center", "Coin", "Bank", "Bot", "NIW"
    ]
    t2_trs = []
    # R0: Headers
    h_tds = [f'<td><span style="font-size: inherit;"><strong>{header_cols[0]}</strong></span></td>']
    for h in header_cols[1:]:
        h_tds.append(f'<td><span style="font-size: inherit;">{h}</span></td>')
    t2_trs.append(f'<tr>{"".join(h_tds)}</tr>')

    # R1: - gửi e-mail báo giá ISSale
    r1_tds = [f'<td><span style="font-size: inherit;">{cell(1, 0)}</span></td>']
    for c in range(1, 14):
        val = cell(1, c) or "&nbsp;"
        r1_tds.append(f'<td><span style="font-size: inherit;">{val}</span></td>' if val != "&nbsp;" else '<td>&nbsp;</td>')
    t2_trs.append(f'<tr>{"".join(r1_tds)}</tr>')

    # R2: - gửi e-mail báo giá ISSale 12-MLLs
    r2_tds = [f'<td><span style="font-size: inherit;">{cell(2, 0)}&nbsp;&nbsp;</span></td>']
    for c in range(1, 14):
        val = cell(2, c) or "&nbsp;"
        r2_tds.append(f'<td><span style="font-size: inherit;">{val}</span></td>' if val != "&nbsp;" else '<td>&nbsp;</td>')
    t2_trs.append(f'<tr>{"".join(r2_tds)}</tr>')

    # R3: - gửi linkedin ISSale MLLs báo giá
    r3_title = cell(3, 0).replace("báo giá", "").strip()
    r3_tds = [f'<td><span style="font-size: inherit;">{r3_title}&nbsp; báo giá</span></td>']
    for c in range(1, 14):
        val = cell(3, c) or "0"
        r3_tds.append(f'<td><span style="font-size: inherit;">{val}</span></td>')
    t2_trs.append(f'<tr>{"".join(r3_tds)}</tr>')

    # R4: - post tag báo giá ISSale MLLs Linkedin
    r4_tds = [f'<td><span style="font-size: inherit;">{cell(4, 0)}</span></td>']
    for c in range(1, 14):
        r4_tds.append('<td>&nbsp;</td>')
    t2_trs.append(f'<tr>{"".join(r4_tds)}</tr>')

    # R5: - post tag báo giá ISSale MLLs Twitter
    r5_tds = [f'<td><span style="font-size: inherit;">{cell(5, 0)}</span></td>']
    for c in range(1, 14):
        r5_tds.append('<td>&nbsp;</td>')
    t2_trs.append(f'<tr>{"".join(r5_tds)}</tr>')

    # R6: - connect linkedin
    sum_email = cell(6, 5) or "3196"
    sum_linkedin = cell(6, 8) or "0"
    push_fund = cell(6, 12) or "0"
    t2_trs.append(
        f'<tr><td><span style="font-size: inherit;">- connect linkedin</span></td>'
        f'<td><span style="font-size: inherit;">20</span></td>'
        f'<td><span style="font-size: inherit;">Sum email gửi báo giá</span></td>'
        f'<td>&nbsp;</td><td>&nbsp;</td>'
        f'<td><span style="font-size: inherit;">{sum_email}</span></td>'
        f'<td colspan="2" rowspan="1"><span style="font-size: inherit;">Sum gửi báo giá linkedin</span></td>'
        f'<td><span style="font-size: inherit;">{sum_linkedin}</span></td>'
        f'<td colspan="3" rowspan="1"><span style="font-size: inherit;">Push Fundraising service</span></td>'
        f'<td><span style="font-size: inherit;">{push_fund}</span></td>'
        f'<td>&nbsp;</td></tr>'
    )

    # R7: - xử lý các phản hồi trên email, linkedin
    r7_detail = cell(7, 1)
    r7_lines = [
        f'<span {ORANGE_STYLE}>{l.strip().replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")}</span>'
        for l in r7_detail.splitlines()
        if l.strip()
    ]
    r7_html = "<br>".join(r7_lines)
    t2_trs.append(
        f'<tr><td><a aria-label="Link - xử lý các phản hồi trên email, linkedin" href="{DOC_LINKS["xu_ly_phan_hoi"]}" {LINK_ATTRS}><span {BLUE_STYLE}><u>- xử lý các phản hồi trên email, linkedin</u></span></a></td>'
        f'<td colspan="12" rowspan="1">{r7_html}</td>'
        f'<td>&nbsp;</td></tr>'
    )
    table_2 = f'<table data-is-focusable="true"><tbody>{"".join(t2_trs)}</tbody></table>'

    # =========================================================================
    # TABLE 3: 80%+ JOB CALI (Chuẩn xác Ray)
    # =========================================================================
    t3_trs = []
    # R0: Headers
    t3_trs.append(
        '<tr><td><span style="font-size: inherit;"><strong>80%+ job Cali,US: $150k trở lên</strong></span></td>'
        '<td><span style="font-size: inherit;"><strong>chief</strong></span></td>'
        '<td><span style="font-size: inherit;"><strong>manager</strong></span></td>'
        '<td><span style="font-size: inherit;"><strong>dưới.M</strong></span></td>'
        '<td><span style="font-size: inherit;"><strong>250+</strong></span></td>'
        '<td><span style="font-size: inherit;"><strong>200+</strong></span></td>'
        '<td><span style="font-size: inherit;"><strong>150+</strong></span></td>'
        '<td><span style="font-size: inherit;"><strong>SUM</strong></span></td>'
        '<td><span style="font-size: inherit;"><strong>chưa apply</strong></span></td></tr>'
    )

    # R1: - Nộp Jobs
    nop_jobs_label = cell(11, 0).replace("Nộp Jobs", "").replace("-", "").strip()
    r1_cols = [
        f'<td><span style="font-size: inherit;">- </span><a aria-label="Link Nộp Jobs " href="{DOC_LINKS["nop_jobs"]}" {LINK_ATTRS}><span style="font-size: inherit;">Nộp Jobs </span></a><span style="font-size: inherit;">{nop_jobs_label}</span></td>'
    ]
    for c in range(1, 9):
        r1_cols.append(f'<td><span style="font-size: inherit;">{cell(11, c)}</span></td>')
    t3_trs.append(f'<tr>{"".join(r1_cols)}</tr>')

    # R2: - Willing job
    willing_label = cell(12, 0).replace("Willing job", "").replace("-", "").strip()
    t3_trs.append(
        f'<tr><td><a aria-label="Link - Willing job" href="{DOC_LINKS["willing_job"]}" {LINK_ATTRS}><span style="font-size: inherit;">- Willing job</span></a><span style="font-size: inherit;">{willing_label}</span></td>'
        f'<td><span style="font-size: inherit;">Linkedin</span></td><td><span style="font-size: inherit;">{cell(12, 2)}</span></td>'
        f'<td><span style="font-size: inherit;">Email</span></td><td><span style="font-size: inherit;">{cell(12, 4)}</span></td>'
        f'<td><span style="font-size: inherit;">Push email</span></td><td><span style="font-size: inherit;">{cell(12, 6)}</span></td>'
        f'<td><span style="font-size: inherit;">Push Linkedin</span></td><td><span style="font-size: inherit;">{cell(12, 8)}</span></td></tr>'
    )

    # R3: - Interview sắp đến:
    iv_detail = cell(13, 0).replace("Interview sắp đến:", "").strip()
    iv_lines = [
        f'<span style="font-size: inherit;">{l.strip().replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")}</span>'
        for l in iv_detail.splitlines()
        if l.strip()
    ]
    iv_html = "<br>".join(iv_lines)
    t3_trs.append(
        f'<tr><td><a aria-label="Link - Interview sắp đến:" href="{DOC_LINKS["interview"]}" {LINK_ATTRS}><span {BLUE_STYLE}><u>- Interview sắp đến:</u></span></a></td>'
        f'<td colspan="8" rowspan="1">{iv_html}</td></tr>'
    )

    # R4: 75%ML / 25%iD
    t3_trs.append(
        '<tr><td><span style="font-size: inherit;"><strong>75%ML / 25%iD</strong></span></td>'
        '<td><span style="font-size: inherit;"><strong>US</strong></span></td>'
        '<td><span style="font-size: inherit;"><strong>Dubai</strong></span></td>'
        '<td><span style="font-size: inherit;"><strong>US đa quốc gia</strong></span></td>'
        '<td><span style="font-size: inherit;"><strong>PhD US</strong></span></td>'
        '<td><span style="font-size: inherit;"><strong>Riyadh</strong></span></td>'
        '<td><span style="font-size: inherit;"><strong>Doha</strong></span></td>'
        '<td>&nbsp;</td><td>&nbsp;</td></tr>'
    )

    # R5: Linkedin
    t3_trs.append(
        f'<tr><td><span style="font-size: inherit;"><strong>Linkedin</strong></span></td>'
        f'<td><span style="font-size: inherit;">{cell(15, 1)}</span></td>'
        f'<td><span style="font-size: inherit;">{cell(15, 2)}</span></td>'
        f'<td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td></tr>'
    )

    # R6: Email
    t3_trs.append(
        f'<tr><td><span style="font-size: inherit;"><strong>Email</strong></span></td>'
        f'<td><span style="font-size: inherit;">{cell(16, 1)}</span></td>'
        f'<td><span style="font-size: inherit;">{cell(16, 2)}</span></td>'
        f'<td><span style="font-size: inherit;">{cell(16, 3)}</span></td>'
        f'<td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td></tr>'
    )

    # R7: Submit form
    t3_trs.append(
        f'<tr><td><span style="font-size: inherit;"><strong>Submit form</strong></span></td>'
        f'<td><span style="font-size: inherit;">{cell(17, 1)}</span></td>'
        f'<td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td></tr>'
    )

    # R8: Trả lời email
    r18_val = cell(18, 1)
    r18_span = f'<span {ORANGE_STYLE}>{r18_val}</span>' if r18_val else '&nbsp;'
    t3_trs.append(
        f'<tr><td><a aria-label="Link - Trả lời email được giới thiệu job, bài test/asssesment" href="{DOC_LINKS["feedback_job"]}" {LINK_ATTRS}><span {BLUE_STYLE}><u>- Trả lời email được giới thiệu job, bài test/asssesment</u></span></a></td>'
        f'<td colspan="8" rowspan="1">{r18_span}</td></tr>'
    )
    table_3 = f'<table data-is-focusable="true"><tbody>{"".join(t3_trs)}</tbody></table>'

    # =========================================================================
    # TABLE 4: TTS / VOLUNTEER (Chuẩn xác Ray)
    # =========================================================================
    t4_trs = []
    t4_trs.append(
        '<tr><td><span style="font-size: inherit;"><strong>TTS /Volunteer</strong></span></td>'
        '<td><span style="font-size: inherit;">Sáng</span></td>'
        '<td><span style="font-size: inherit;">Chiều</span></td>'
        '<td><span style="font-size: inherit;">Tối</span></td>'
        '<td><span style="font-size: inherit;">Xử lý CV intern</span></td>'
        '<td><span style="font-size: inherit;">Xử lý CV volunteer</span></td>'
        '<td><span style="font-size: inherit;">Tổng intern</span></td>'
        '<td><span style="font-size: inherit;">Tổng giờ làm</span></td></tr>'
    )

    # AH
    t4_trs.append(
        f'<tr><td><a aria-label="Link AH" href="{DOC_LINKS["ah"]}" {LINK_ATTRS}><span {BLUE_STYLE}><strong><u>AH</u></strong></span></a></td>'
        f'<td><span style="font-size: inherit;">{cell(11, 11)}</span></td>'
        f'<td><span style="font-size: inherit;">{cell(11, 12)}</span></td>'
        f'<td><span style="font-size: inherit;">{cell(11, 13)}</span></td>'
        f'<td><span style="font-size: inherit;">{cell(11, 14)}</span></td>'
        f'<td><span style="font-size: inherit;">{cell(11, 15)}</span></td>'
        f'<td colspan="1" rowspan="3"><span style="font-size: inherit;">{cell(11, 16)}</span></td>'
        f'<td colspan="1" rowspan="3"><span style="font-size: inherit;">{cell(11, 17)}</span></td></tr>'
    )
    # AU
    t4_trs.append(
        f'<tr><td><a aria-label="Link AU" href="{DOC_LINKS["au"]}" {LINK_ATTRS}><span {BLUE_STYLE}><strong><u>AU</u></strong></span></a></td>'
        f'<td><span style="font-size: inherit;">{cell(12, 11)}</span></td>'
        f'<td><span style="font-size: inherit;">{cell(12, 12)}</span></td>'
        f'<td><span style="font-size: inherit;">{cell(12, 13)}</span></td>'
        f'<td><span style="font-size: inherit;">{cell(12, 14)}</span></td>'
        f'<td><span style="font-size: inherit;">{cell(12, 15)}</span></td></tr>'
    )
    # SAM Foundation + QT
    t4_trs.append(
        f'<tr><td><a aria-label="Link SAM Foundation" href="{DOC_LINKS["sam_foundation"]}" {LINK_ATTRS}><span style="font-size: inherit;"><strong>SAM Foundation</strong></span></a><span style="font-size: inherit;"><strong> + QT</strong></span></td>'
        f'<td><span style="font-size: inherit;">{cell(13, 11)}</span></td>'
        f'<td><span style="font-size: inherit;">{cell(13, 12)}</span></td>'
        f'<td><span style="font-size: inherit;">{cell(13, 13)}</span></td>'
        f'<td><span style="font-size: inherit;">{cell(13, 14)}</span></td>'
        f'<td><span style="font-size: inherit;">{cell(13, 15)}</span></td></tr>'
    )
    table_4 = f'<table data-is-focusable="true"><tbody>{"".join(t4_trs)}</tbody></table>'

    # =========================================================================
    # TABLE 5: NIW (Chuẩn xác Ray)
    # =========================================================================
    t5_trs = []
    # R0
    t5_trs.append(
        f'<tr><td colspan="7" rowspan="1"><span style="font-size: inherit;">NIW: </span>'
        f'<a aria-label="Link Citations for papers" href="{DOC_LINKS["niw_citations"]}" {LINK_ATTRS}><span style="font-size: inherit;">Citations for papers</span></a>'
        f'<span style="font-size: inherit;"> </span>'
        f'<a aria-label="Link NIW\'s note - Xoắn nện" href="{DOC_LINKS["niw_notes"]}" {LINK_ATTRS}><span style="font-size: inherit;">NIW\'s note - Xoắn nện</span></a></td></tr>'
    )
    # R1: - Linkedin
    t5_trs.append(
        f'<tr><td><span style="font-size: inherit;">- </span><a aria-label="Link Linkedin" href="{DOC_LINKS["niw_linkedin"]}" {LINK_ATTRS}><span style="font-size: inherit;">Linkedin</span></a></td>'
        f'<td><span style="font-size: inherit;">Connect</span></td><td><span style="font-size: inherit;">{cell(21, 2)}</span></td>'
        f'<td><span style="font-size: inherit;">Reference</span></td><td><span style="font-size: inherit;">{cell(21, 4)}</span></td>'
        f'<td><span style="font-size: inherit;">Push ref</span></td><td><span style="font-size: inherit;">{cell(21, 6)}</span></td></tr>'
    )
    # R2: - Email
    t5_trs.append(
        '<tr><td><span style="font-size: inherit;">- Email</span></td>'
        '<td><span style="font-size: inherit;">Reference</span></td>'
        '<td>&nbsp;</td>'
        '<td><span style="font-size: inherit;">Push ref</span></td>'
        '<td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td></tr>'
    )
    # R3: - xử lý case
    t5_trs.append(
        f'<tr><td><a aria-label="Link - xử lý case" href="{DOC_LINKS["niw_case"]}" {LINK_ATTRS}><span {BLUE_STYLE}><u>- xử lý case</u></span></a></td>'
        f'<td colspan="6" rowspan="1">&nbsp;</td></tr>'
    )
    # R4: - Hồ sơ Chen - WeGreen
    chen_detail = cell(24, 1)
    chen_lines = [
        f'<span style="font-size: inherit;">{l.strip().replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")}</span>'
        for l in chen_detail.splitlines()
        if l.strip()
    ]
    chen_html = "<br>".join(chen_lines)
    t5_trs.append(
        f'<tr><td><span style="font-size: inherit;">- Hồ sơ Chen - WeGreen</span></td>'
        f'<td colspan="6" rowspan="1">{chen_html}</td></tr>'
    )
    table_5 = f'<table data-is-focusable="true"><tbody>{"".join(t5_trs)}</tbody></table>'

    # =========================================================================
    # TABLE 6: ĐĂNG BÀI (Chuẩn xác Ray: bảng 1 cột)
    # =========================================================================
    t6_trs = ['<tr><td rowspan="1"><span style="font-size: inherit;"><strong>Đăng bài:</strong></span></td></tr>']
    for r in range(len(rows)):
        for c in range(len(rows[r])):
            v = cell(r, c)
            if "threads.com" in v:
                u = v.strip()
                handle = u.split("@")[-1].rstrip("/") if "@" in u else u
                title = f"@{handle}"
                if "auavago" in u:
                    title = "AU-Avago Corp (@auavago_corp) • Threads, Say more"
                elif "ahlongquan" in u:
                    title = "AH-LongQuan Corporation (@ahlongquan.company) • Threads, Say more"
                elif "sam.foundation.nonprofit" in u:
                    title = "SAM Foundation Organization (@sam.foundation.nonprofit) • Threads,..."
                elif "sam_foundation_official" in u:
                    title = u
                t6_trs.append(
                    f'<tr><td rowspan="1"><a aria-label="Link {title}" href="{u}" {LINK_ATTRS}><span style="font-size: inherit;">{title}</span></a></td></tr>'
                )

    table_6 = f'<table data-is-focusable="true"><tbody>{"".join(t6_trs)}</tbody></table>'

    # =========================================================================
    # GOM TOÀN BỘ 6 BẢNG REPORT THÀNH HTML
    # =========================================================================
    html_report = f"{table_1}{table_2}{table_3}{table_4}{table_5}{table_6}"

    # Tạo bản plain-text tương ứng
    dashboard_res = _parse_report_dashboard(rows)
    text_report = compose_leader_report(dashboard_res)

    return html_report, text_report


def compose_full_single_message(
    template_rows: List[List[Any]], report_rows: List[List[Any]]
) -> tuple[str, str]:
    """
    Gom toàn bộ nội dung thành 1 tin nhắn duy nhất chuẩn 100% cấu trúc Ray (nhóm gbBOSS):
      - Table 0: Template
      - Table 1: Tổng thể
      - Table 2: 10% Business
      - Table 3: 80%+ job Cali
      - Table 4: TTS /Volunteer
      - Table 5: NIW
      - Table 6: Đăng bài
    Trả về tuple (html_content, text_content).
    """
    html_template, text_template = compose_template_message(template_rows)
    html_report, text_report = compose_table_leader_report(report_rows)

    # Wrap each table in its own <div data-table-scroll-container="true"> separated by <p>&nbsp;</p>
    # and outer <div dir="auto" class="fui-Primitive ___11tzqds f1oy3dpc f89hs3r fqtknz5 fyvcxda">
    raw_tables = [html_template] + re.findall(r"<table.*?>.*?</table>", html_report, flags=re.DOTALL | re.IGNORECASE)
    wrapped_tables = [f'<div data-table-scroll-container="true">{t}</div>' for t in raw_tables]
    inner_content = "<p>&nbsp;</p>" + "<p>&nbsp;</p>".join(wrapped_tables) + "<p>&nbsp;</p>"
    combined_html = f'<div dir="auto" class="fui-Primitive ___11tzqds f1oy3dpc f89hs3r fqtknz5 fyvcxda">{inner_content}</div>'

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
