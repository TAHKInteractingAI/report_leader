"""
Composer package for preparing, parsing, and rendering Microsoft Teams messages.
"""

from .constants import (
    DOC_LINKS,
    LINK_CLS,
    LINK_ATTRS,
    BLUE_STYLE,
    RED_STYLE,
    ORANGE_STYLE,
)
from .utils import (
    clean_text,
    normalize_text,
)
from .parsers import (
    parse_template_sheet,
    parse_report_sheet,
    _parse_report_dashboard,
)
from .template_builder import (
    compose_template_message,
)
from .report_builder import (
    compose_table_leader_report,
    compose_leader_report,
    split_report_into_messages,
)
from .message_builder import (
    compose_full_single_message,
)

__all__ = [
    "clean_text",
    "normalize_text",
    "DOC_LINKS",
    "LINK_CLS",
    "LINK_ATTRS",
    "BLUE_STYLE",
    "RED_STYLE",
    "ORANGE_STYLE",
    "parse_template_sheet",
    "parse_report_sheet",
    "_parse_report_dashboard",
    "compose_template_message",
    "compose_table_leader_report",
    "compose_leader_report",
    "split_report_into_messages",
    "compose_full_single_message",
]
