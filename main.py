"""
Entrypoint chạy Report Leader Bot gửi tin nhắn tự động lên Microsoft Teams.
"""
import gc
from src.reporter import run_report_leader

# Vô hiệu hóa garbage collection tự động để tránh conflict với undetected_chromedriver
gc.disable()

if __name__ == "__main__":
    run_report_leader()
