"""
Single full message composer merging template and report tables.
"""
import re
from typing import List, Any
from .template_builder import compose_template_message
from .report_builder import compose_table_leader_report


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
