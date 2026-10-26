"""
Builder for composing the template portion (Table 0) of the report.
"""
import re
from typing import List, Any
from .constants import LINK_ATTRS
from .utils import clean_text


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
            line_str = re.sub(
                r'(https?://[^\s<]+)',
                f'<a aria-label="Link \\1" href="\\1" {LINK_ATTRS}>\\1</a>',
                line_str
            )
            if line_str:
                parts.append(f'<span style="font-size: inherit;">{line_str}</span>')
        inner = "<br>".join(parts)
        t0_trs.append(f"<tr><td>{inner}</td></tr>")

    html_template = f'<table data-is-focusable="true"><tbody>{"".join(t0_trs)}</tbody></table>'
    text_template = "\n".join(text_lines)

    return html_template, text_template
