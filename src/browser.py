import os
import sys
import types
import time
import shutil
import platform
import subprocess
import re
from selenium import webdriver

# Khắc phục thiếu distutils.version.LooseVersion trên Python 3.12+
try:
    from distutils.version import LooseVersion  # type: ignore
except ImportError:
    class LooseVersion:
        def __init__(self, vstring=None):
            self.vstring = vstring
            if vstring:
                self.version = [
                    int(x) if x.isdigit() else x
                    for x in re.split(r"(\d+)", str(vstring))
                    if x
                ]
            else:
                self.version = []

        def __repr__(self):
            return f"LooseVersion ('{self.vstring}')"

        def __lt__(self, other):
            return self.version < (
                other.version
                if isinstance(other, LooseVersion)
                else LooseVersion(other).version
            )

        def __le__(self, other):
            return self.version <= (
                other.version
                if isinstance(other, LooseVersion)
                else LooseVersion(other).version
            )

        def __eq__(self, other):
            return self.version == (
                other.version
                if isinstance(other, LooseVersion)
                else LooseVersion(other).version
            )

        def __ge__(self, other):
            return self.version >= (
                other.version
                if isinstance(other, LooseVersion)
                else LooseVersion(other).version
            )

        def __gt__(self, other):
            return self.version > (
                other.version
                if isinstance(other, LooseVersion)
                else LooseVersion(other).version
            )

    mod_distutils = types.ModuleType("distutils")
    mod_version = types.ModuleType("distutils.version")
    mod_version.LooseVersion = LooseVersion
    mod_distutils.version = mod_version
    sys.modules.setdefault("distutils", mod_distutils)
    sys.modules.setdefault("distutils.version", mod_version)

import undetected_chromedriver as uc


# Sửa lỗi OSError: [WinError 6] The handle is invalid khi Python dọn dẹp memory
def _patch_uc_del():
    def _safe_del(self):
        try:
            self.quit()
        except Exception:
            pass

    uc.Chrome.__del__ = _safe_del


_patch_uc_del()


def save_screenshot(driver: webdriver.Chrome, file_name: str = "screenshot.png"):
    """Lưu ảnh chụp màn hình để debug và kiểm tra trên CI/CD."""
    try:
        driver.save_screenshot(file_name)
        print(f"📸 Đã lưu ảnh màn hình '{file_name}'")
    except Exception as e:
        print(f"❌ Không thể lưu ảnh màn hình '{file_name}': {e}")
    time.sleep(1)


display_screenshot = save_screenshot


def detect_browser():
    """
    Tự động tìm kiếm đường dẫn thực thi của Brave Browser hoặc Chrome,
    kèm theo phiên bản chính (Major Version) của Chromium.
    Ưu tiên Brave Browser theo yêu cầu người dùng.
    """
    custom_path = (
        os.getenv("BROWSER_EXECUTABLE_PATH")
        or os.getenv("BRAVE_PATH")
        or os.getenv("CHROME_PATH")
    )
    candidates = []
    if custom_path:
        candidates.append(custom_path)

    system = platform.system()
    if system == "Darwin":  # macOS
        candidates.extend([
            "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
            os.path.expanduser("~/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"),
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            os.path.expanduser("~/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
        ])
    elif system == "Linux":
        candidates.extend([
            "brave-browser",
            "/usr/bin/brave-browser",
            "google-chrome",
            "/usr/bin/google-chrome",
            "google-chrome-stable",
            "/usr/bin/google-chrome-stable",
            "chromium-browser",
            "/usr/bin/chromium-browser",
            "chromium",
            "/usr/bin/chromium",
        ])
    elif system == "Windows":
        candidates.extend([
            r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
            r"C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\BraveSoftware\Brave-Browser\Application\brave.exe"),
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
        ])

    for path in candidates:
        if not path:
            continue
        # Chuyển đổi tên lệnh tương đối thành đường dẫn tuyệt đối qua PATH
        abs_path = shutil.which(path) if not os.path.isabs(path) else path
        if not abs_path or not os.path.exists(abs_path):
            continue
        try:
            real_path = os.path.realpath(abs_path)
            out = subprocess.check_output([real_path, "--version"], stderr=subprocess.DEVNULL).decode("utf-8")
            match = re.search(r"(\d+)\.", out)
            if match:
                version = int(match.group(1))
                browser_name = "Brave Browser" if ("brave" in real_path.lower() or "brave" in out.lower()) else "Chrome"
                print(f"✅ Đã tìm thấy {browser_name} tại: {real_path} (Major version: {version})")
                return real_path, version
        except Exception:
            continue

    # Thử tìm kiếm tự động qua cơ chế của undetected_chromedriver nếu chưa thấy
    try:
        uc_found = uc.find_chrome_executable()
        if uc_found and os.path.exists(uc_found):
            real_uc = os.path.realpath(uc_found)
            out = subprocess.check_output([real_uc, "--version"], stderr=subprocess.DEVNULL).decode("utf-8")
            match = re.search(r"(\d+)\.", out)
            version = int(match.group(1)) if match else None
            browser_name = "Brave Browser" if ("brave" in real_uc.lower() or "brave" in out.lower()) else "Chrome"
            print(f"✅ Đã tìm thấy {browser_name} qua uc tại: {real_uc} (Major version: {version})")
            return real_uc, version
    except Exception:
        pass

    return None, None


def get_driver():
    """Khởi tạo WebDriver với undetected_chromedriver tối ưu cho Teams Web trên Brave / Chrome."""
    options = uc.ChromeOptions()

    headless_env = os.getenv("HEADLESS", "true").strip().lower()
    if headless_env not in ("false", "0", "no"):
        options.add_argument("--headless=new")
    else:
        print("🖥️ Đang chạy trình duyệt có giao diện (HEADLESS=false)...")

    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-first-run")
    options.add_argument("--no-default-browser-check")
    options.add_argument("--disable-background-networking")
    options.add_argument("--window-size=1920,1080")
    options.page_load_strategy = "eager"
    options.add_argument("--lang=en-GB")

    prefs = {
        "profile.cookie_controls_mode": 0,
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
    }
    options.add_experimental_option("prefs", prefs)

    proxy_url = os.getenv("PROXY_URL")
    if proxy_url:
        options.add_argument(f"--proxy-server={proxy_url}")

    browser_path, browser_version = detect_browser()

    driver_kwargs = {"options": options}
    if browser_path and os.path.exists(browser_path):
        driver_kwargs["browser_executable_path"] = browser_path
        options.binary_location = browser_path
    if browser_version:
        driver_kwargs["version_main"] = browser_version

    try:
        driver = uc.Chrome(**driver_kwargs)
    except Exception as e:
        print(f"❌ Lỗi khi khởi động undetected_chromedriver: {e}")
        raise e

    try:
        driver.execute_cdp_cmd(
            "Emulation.setTimezoneOverride",
            {"timezoneId": "Asia/Ho_Chi_Minh"},
        )
    except Exception:
        pass

    try:
        driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {
                "source": """
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                window.navigator.chrome = { runtime: {} };
                Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
                Object.defineProperty(navigator, 'languages', { get: () => ['en-GB', 'en-US', 'en'] });
                Object.defineProperty(navigator, 'credentials', {
                    get: () => undefined
                });
                window.PublicKeyCredential = undefined;
            """
            },
        )
    except Exception as e:
        print(f"⚠️ Cảnh báo cấu hình CDP script (bỏ qua): {e}")

    return driver
