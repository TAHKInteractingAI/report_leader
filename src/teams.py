import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .config import TEAMS_EMAIL, TEAMS_PASSWORD
from .browser import get_driver, display_screenshot, save_screenshot


# ==============================================================================
# XỬ LÝ POPUP & ĐIỀU HƯỚNG TRÊN TEAMS
# ==============================================================================
def dismiss_teams_popups(driver):
    """Tự động đóng các banner và popup làm phiền sau đăng nhập trên Teams."""
    try:
        # 1. Bấm nút 'Use the web app instead' nếu xuất hiện
        use_web_btn = driver.find_elements(
            By.XPATH,
            '//a[contains(text(), "Use the web app") or contains(text(), "Dùng ứng dụng web")] | '
            '//button[contains(text(), "Use the web app") or contains(text(), "Dùng ứng dụng web")]',
        )
        for btn in use_web_btn:
            try:
                if btn.is_displayed():
                    driver.execute_script("arguments[0].click();", btn)
                    print("👉 Đã bấm nút 'Use the web app instead'")
                    time.sleep(1)
            except Exception:
                pass
    except Exception:
        pass

    try:
        # 2. Đóng banner thông báo / What's new / Dismiss
        close_banner_btns = driver.find_elements(
            By.XPATH,
            '//button[contains(@aria-label, "Dismiss") or contains(@aria-label, "Đóng") or contains(@aria-label, "Close") '
            'or contains(., "Dismiss") or contains(., "Not now") or contains(., "Got it") or contains(., "Không phải lúc này")]',
        )
        for btn in close_banner_btns:
            try:
                if btn.is_displayed():
                    driver.execute_script("arguments[0].click();", btn)
                    time.sleep(1)
            except Exception:
                pass
    except Exception:
        pass


def ensure_chat_tab(driver):
    """Đảm bảo đang ở tab Chat (Trò chuyện) trên thanh điều hướng Teams."""
    dismiss_teams_popups(driver)
    try:
        chat_btn = WebDriverWait(driver, 8).until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    '//button[contains(@data-tid, "app-bar-chat") '
                    'or contains(@aria-label, "Chat") '
                    'or contains(@aria-label, "Trò chuyện")] '
                    '| //div[@role="tab"][contains(@data-tid, "app-bar-chat") or contains(@aria-label, "Chat") or contains(@aria-label, "Trò chuyện")] '
                    '| //a[@role="tab"][contains(@data-tid, "app-bar-chat") or contains(@aria-label, "Chat") or contains(@aria-label, "Trò chuyện")]',
                )
            )
        )
        driver.execute_script("arguments[0].click();", chat_btn)
        time.sleep(2)
        print("📂 Đã bấm chuyển sang tab Chat.")
    except Exception as e:
        print(f"ℹ️ Tab Chat có thể đã được chọn sẵn hoặc không tìm thấy nút: {e}")


# ==============================================================================
# GỬI TIN NHẮN
# ==============================================================================
def send_message(driver, message: str, html_content: str = None) -> bool:
    """
    Gửi nội dung báo cáo vào khung chat đang mở.
    Hỗ trợ chèn trực tiếp nội dung HTML (Table Grid) thông qua Clipboard/insertHTML,
    giúp giữ nguyên cấu trúc bảng và hoàn tất gửi 1 tin nhắn duy nhất tức thì.
    """
    try:
        input_xpath = (
            '//div[@contenteditable="true"] '
            '| //div[@role="textbox"] '
            '| //div[@data-tid="ckeditor-replyConversation"]'
        )
        message_box = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, input_xpath))
        )
        driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", message_box
        )
        time.sleep(1)
        try:
            message_box.click()
        except Exception:
            driver.execute_script("arguments[0].focus();", message_box)

        inserted_html_successfully = False

        # Ưu tiên chèn HTML bảng trực tiếp nếu có html_content
        if html_content:
            try:
                js_insert_html = '''
                const editor = arguments[0];
                const html = arguments[1];
                const plainText = arguments[2] || '';

                editor.focus();

                // Xóa / bôi đen nội dung cũ nếu có
                const range = document.createRange();
                range.selectNodeContents(editor);
                const sel = window.getSelection();
                sel.removeAllRanges();
                sel.addRange(range);

                // Thử cách 1: ClipboardEvent với DataTransfer (text/html)
                try {
                    const dt = new DataTransfer();
                    dt.setData('text/html', html);
                    dt.setData('text/plain', plainText);
                    const pasteEvt = new ClipboardEvent('paste', {
                        bubbles: true,
                        cancelable: true,
                        clipboardData: dt
                    });
                    editor.dispatchEvent(pasteEvt);
                } catch (e) {}

                // Thử cách 2: execCommand insertHTML nếu editor chưa có bảng
                if (!editor.querySelector('table')) {
                    try {
                        document.execCommand('insertHTML', false, html);
                    } catch (e) {}
                }

                // Phát sinh sự kiện input để CKEditor cập nhật state
                editor.dispatchEvent(new Event('input', { bubbles: true }));
                return (editor.querySelector('table') !== null || (editor.innerHTML && editor.innerHTML.length > 50));
                '''
                res = driver.execute_script(
                    js_insert_html, message_box, html_content, message
                )
                inserted_html_successfully = bool(res)
                if inserted_html_successfully:
                    print("📊 Đã chèn thành công bố cục bảng HTML vào khung chat Teams!")
            except Exception as e_html:
                print(f"⚠️ Không thể chèn HTML trực tiếp, chuyển sang gõ văn bản: {e_html}")

        # Dự phòng gõ phím nếu không có html_content hoặc chèn HTML không thành công
        if not inserted_html_successfully:
            lines = message.split("\n")
            total_lines = len(lines)
            for i, line in enumerate(lines):
                try:
                    message_box.send_keys(line)
                except Exception:
                    safe_line = "".join(c for c in line if ord(c) <= 0xFFFF)
                    message_box.send_keys(safe_line)

                if i < total_lines - 1:
                    message_box.send_keys(Keys.SHIFT, Keys.ENTER)

        display_screenshot(driver, "after_typing_message.png")
        time.sleep(2)

        # Bấm nút gửi tin nhắn
        sent = False
        try:
            send_btn = driver.find_elements(
                By.XPATH,
                '//button[@data-tid="chatPane-send-message-button"] '
                '| //button[contains(@aria-label, "Send") or contains(@aria-label, "Gửi")]',
            )
            for btn in send_btn:
                if btn.is_displayed():
                    driver.execute_script("arguments[0].click();", btn)
                    sent = True
                    break
        except Exception:
            pass

        if not sent:
            message_box.send_keys(Keys.ENTER)

        time.sleep(3)
        display_screenshot(driver, "after_sending_message.png")
        print("✅ Đã gửi thành công tin nhắn báo cáo lên nhóm Teams!")
        return True

    except Exception as e:
        print(f"❌ Lỗi khi gửi tin nhắn: {e}")
        display_screenshot(driver, "send_message_error.png")
        return False


# ==============================================================================
# MỞ NHÓM CHAT TEAMS
# ==============================================================================
def open_chat(driver, chat_name: str) -> bool:
    """Mở nhóm chat an toàn: tìm trong danh sách và dùng bộ lọc tìm kiếm (Filter)."""
    ensure_chat_tab(driver)
    dismiss_teams_popups(driver)

    chat_item_xpath = (
        '//*[contains(@data-tid, "chat-list-item") '
        'or contains(@data-tid, "chat-item") '
        'or @data-item-type="chat" '
        'or @role="listitem" '
        'or @role="treeitem"]'
    )

    # 1. Thử tìm trong danh sách chat đang hiển thị sẵn
    try:
        WebDriverWait(driver, 8).until(
            EC.presence_of_element_located((By.XPATH, chat_item_xpath))
        )
        groups = driver.find_elements(By.XPATH, chat_item_xpath)

        for g in groups:
            lines = [x.strip() for x in g.text.splitlines() if x.strip()]
            if not lines:
                continue
            if lines[0] in ["Unread", "Chưa đọc"]:
                lines.pop(0)
            if not lines:
                continue

            txt = lines[0]
            if not txt:
                txt = g.get_attribute("aria-label") or ""

            if (
                txt == chat_name
                or chat_name.lower() in txt.lower()
                or txt.lower() in chat_name.lower()
                or chat_name.startswith(txt.replace("...", "").strip())
            ):
                driver.execute_script(
                    "arguments[0].scrollIntoView({block: 'center'});", g
                )
                time.sleep(1)
                driver.execute_script("arguments[0].click();", g)
                time.sleep(3)
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located(
                        (
                            By.XPATH,
                            '//div[@contenteditable="true"] | //div[@role="textbox"] | //div[@data-tid="ckeditor-replyConversation"]',
                        )
                    )
                )
                display_screenshot(driver, "after_opening_chat.png")
                print(f"📂 Đã mở đúng nhóm: {chat_name}")
                return True
    except Exception as e:
        print(
            f"ℹ️ Không thấy '{chat_name}' ở danh sách ngoài ({e}). Đang chuyển sang tìm bằng Filter..."
        )

    # 2. Mở nhóm bằng thanh Filter / Search
    try:
        try:
            filter_icon_xpath = (
                '//button[@data-testid="simple-collab-left-rail-header-sticky-filter-v2-button"]'
                ' | //button[contains(@aria-keyshortcuts, "Ctrl+Shift+F")]'
                ' | //button[contains(@aria-label, "Filter") or contains(@aria-label, "Lọc")]'
            )
            filter_icon = driver.find_element(By.XPATH, filter_icon_xpath)
            driver.execute_script("arguments[0].click();", filter_icon)
            time.sleep(1)
        except Exception:
            pass

        left_search_xpath = (
            '//input[@data-testid="simple-collab-left-rail-sticky-filter-input"]'
            ' | //input[@id="simple-collab-left-rail-sticky-filter-input-id"]'
            ' | //input[contains(@placeholder, "Filter") or contains(@placeholder, "Lọc")]'
        )
        search = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, left_search_xpath))
        )
        search.click()
        search.send_keys(Keys.CONTROL + "a")
        search.send_keys(Keys.BACKSPACE)
        # Sử dụng một phần từ khóa tên nhóm để tìm kiếm chính xác
        search_keyword = chat_name.split()[0] if " " in chat_name else chat_name[:15]
        search.send_keys(search_keyword)
        time.sleep(4)

        filtered_result_xpath = (
            f"//*[contains(@data-tid, 'chat-list-item') or contains(@data-tid, 'chat-item') or @role='listitem' or @role='treeitem'][.//*[contains(text(), '{search_keyword}')]] "
            f"| //span[contains(normalize-space(text()), '{search_keyword}')]"
        )
        filtered_result = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, filtered_result_xpath))
        )
        driver.execute_script("arguments[0].click();", filtered_result)
        time.sleep(3)
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    '//div[@contenteditable="true"] | //div[@role="textbox"] | //div[@data-tid="ckeditor-replyConversation"]',
                )
            )
        )
        display_screenshot(driver, "after_opening_chat.png")
        print(f"📂 Đã mở nhóm qua thanh Filter: {chat_name}")
        return True

    except Exception as e:
        display_screenshot(driver, "open_chat_error.png")
        print(
            f"❌ Lỗi khi mở chat '{chat_name}' (URL: {driver.current_url}): {e}"
        )
        return False


# ==============================================================================
# ĐĂNG NHẬP TEAMS
# ==============================================================================
def login(email: str = TEAMS_EMAIL, password: str = TEAMS_PASSWORD):
    """Đăng nhập tài khoản Microsoft Teams qua giao diện web."""
    if not email or not password:
        print("❌ Lỗi: TEAMS_EMAIL hoặc TEAMS_PASSWORD chưa được thiết lập!")
        return None

    driver = None
    try:
        driver = get_driver()
        driver.get("https://teams.microsoft.com/")
        wait = WebDriverWait(driver, 30)

        print(f"⏳ Đang thực hiện đăng nhập tài khoản: {email}...")

        # 1. Xử lý nút Sign in ban đầu
        try:
            sign_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        '//button[contains(., "Sign in")] | //a[contains(., "Sign in")] | //button[contains(., "Đăng nhập")]',
                    )
                )
            )
            sign_btn.click()
        except Exception:
            pass

        # 2. Ô nhập Email
        email_box = wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'input[type="email"], input[name="loginfmt"]')
            )
        )
        email_box.send_keys(email)
        email_box.send_keys(Keys.RETURN)
        time.sleep(3)

        # Xử lý trường hợp Microsoft đòi gửi mã xác thực -> ép chuyển về Password
        try:
            use_pass_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        '//*[contains(text(), "Use your password") or contains(text(), "Sử dụng mật khẩu")]',
                    )
                )
            )
            use_pass_btn.click()
            time.sleep(2)
        except Exception:
            pass

        # Xử lý màn hình "Sign in another way" -> Chọn Use your password
        try:
            try:
                other_ways_btn = WebDriverWait(driver, 4).until(
                    EC.presence_of_element_located(
                        (
                            By.XPATH,
                            '//*[contains(text(), "Other ways to sign in") or contains(text(), "Cách đăng nhập khác")]',
                        )
                    )
                )
                driver.execute_script("arguments[0].click();", other_ways_btn)
                print("👉 Đã chọn: Other ways to sign in")
                time.sleep(2)
            except Exception:
                pass

            use_pass_btn = WebDriverWait(driver, 6).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        '//*[contains(text(), "Use your password") or contains(text(), "Sử dụng mật khẩu")]/ancestor::div[@role="button"] '
                        '| //*[contains(text(), "Use your password") or contains(text(), "Sử dụng mật khẩu")]',
                    )
                )
            )
            driver.execute_script("arguments[0].click();", use_pass_btn)
            print("👉 Đã kích hoạt: Use your password")
            time.sleep(3)
        except Exception as e:
            print(f"ℹ️ Bước chuyển phương thức đăng nhập: {e}")

        # 3. Ô nhập Password
        pass_box = wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'input[type="password"], input[name="passwd"]')
            )
        )
        pass_box.send_keys(password)
        pass_box.send_keys(Keys.RETURN)

        # 4. Xử lý màn hình "Stay signed in?" -> Chọn No / Decline
        try:
            print("⏳ Đang xử lý màn hình Stay signed in...")
            no_btn = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        '//*[@id="declineButton"] | //*[@id="idBtn_Back"] | //*[@value="No"] | //button[contains(., "No")]',
                    )
                )
            )
            no_btn.click()
            time.sleep(3)
        except Exception:
            print("⚠️ Không thấy màn hình Stay signed in, tiếp tục...")

        print("✅ Đăng nhập tài khoản Microsoft thành công!")

        # 5. Chờ giao diện chính Teams nạp xong
        print("⏳ Đang chờ giao diện Teams nạp xong (tối đa 75s)...")
        start_wait = time.time()
        max_wait = 75
        while time.time() - start_wait < max_wait:
            current_url = (driver.current_url or "").lower()

            # Kiểm tra xem có bị tạm khóa phiên (Try again later) không
            try:
                body_text = driver.find_element(By.TAG_NAME, "body").text.lower()
                if (
                    "try again later" in body_text
                    or "can't sign you in right now" in body_text
                ):
                    save_screenshot(driver, "try_again_later_blocked.png")
                    print(
                        f"❌ Microsoft tạm khóa phiên đăng nhập (Try again later) tại: {driver.current_url}"
                    )
                    try:
                        driver.quit()
                    except Exception:
                        pass
                    return None
            except Exception:
                pass

            # Bấm nút 'Use the web app instead' nếu xuất hiện
            try:
                use_web_btn = driver.find_elements(
                    By.XPATH,
                    '//a[contains(text(), "Use the web app") or contains(text(), "Dùng ứng dụng web")] | '
                    '//button[contains(text(), "Use the web app") or contains(text(), "Dùng ứng dụng web")]',
                )
                for btn in use_web_btn:
                    if btn.is_displayed():
                        driver.execute_script("arguments[0].click();", btn)
                        print("👉 Đã bấm nút 'Use the web app instead'")
                        time.sleep(2)
            except Exception:
                pass

            is_login_domain = any(
                d in current_url
                for d in (
                    "login.microsoftonline.com",
                    "login.live.com",
                    "account.live.com",
                )
            )
            nav_items = driver.find_elements(
                By.XPATH,
                '//button | //div[@role="button"] | //div[@role="tab"] | //div[@role="listitem"] | //*[@role="treeitem"]',
            )
            if len(nav_items) > 5 and not is_login_domain:
                print(
                    f"✅ Giao diện chính Teams đã sẵn sàng sau {int(time.time() - start_wait)} giây!"
                )
                dismiss_teams_popups(driver)
                return driver
            time.sleep(3)

        print(f"⚠️ Hết thời gian chờ {max_wait}s. URL hiện tại: {driver.current_url}")
        dismiss_teams_popups(driver)
        return driver

    except Exception as e:
        print(f"❌ Đăng nhập thất bại: {e}")
        if driver:
            try:
                save_screenshot(driver, "login_error.png")
            except Exception:
                pass
            try:
                driver.quit()
            except Exception:
                pass
        return None
