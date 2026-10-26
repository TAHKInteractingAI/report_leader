"""
Builder for composing the structured report tables and text formats.
"""
import re
from typing import List, Dict, Any, Optional
from ..config import REPORT_SECTIONS
from .constants import (
    DOC_LINKS,
    LINK_ATTRS,
    BLUE_STYLE,
    RED_STYLE,
    ORANGE_STYLE,
)
from .utils import clean_text, normalize_text
from .parsers import _parse_report_dashboard


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

    # R7: - xử lý các phản hồi trên email, linkedin (Màu đỏ chuẩn Ray: RED_STYLE)
    r7_idx = 7
    for r_check in range(1, min(15, len(rows))):
        if "xử lý các phản hồi" in cell(r_check, 0).lower():
            r7_idx = r_check
            break
    r7_detail = cell(r7_idx, 1)
    r7_lines = [
        f'<span {RED_STYLE}>{l.strip().replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")}</span>'
        for l in r7_detail.splitlines()
        if l.strip()
    ]
    r7_html = "<br>".join(r7_lines) if r7_lines else "&nbsp;"
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

    # R8: Trả lời email (Màu đỏ chuẩn Ray: RED_STYLE)
    r18_idx = 18
    for r_check in range(11, min(25, len(rows))):
        col0 = cell(r_check, 0).lower()
        if "trả lời email" in col0 or "asssesment" in col0:
            r18_idx = r_check
            break
    r18_val = cell(r18_idx, 1)
    r18_lines = [
        f'<span {RED_STYLE}>{l.strip().replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")}</span>'
        for l in r18_val.splitlines()
        if l.strip()
    ]
    r18_html = "<br>".join(r18_lines) if r18_lines else "&nbsp;"
    t3_trs.append(
        f'<tr><td><a aria-label="Link - Trả lời email được giới thiệu job, bài test/asssesment" href="{DOC_LINKS["feedback_job"]}" {LINK_ATTRS}><span {BLUE_STYLE}><u>- Trả lời email được giới thiệu job, bài test/asssesment</u></span></a></td>'
        f'<td colspan="8" rowspan="1">{r18_html}</td></tr>'
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
