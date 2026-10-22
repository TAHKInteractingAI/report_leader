"""
Report Leader Bot package.
"""
def run_report_leader():
    from .reporter import run_report_leader as _run
    return _run()

__all__ = ["run_report_leader"]
