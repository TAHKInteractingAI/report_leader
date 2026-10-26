"""
Helper utilities for text processing.
"""
import re
from typing import Any


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
