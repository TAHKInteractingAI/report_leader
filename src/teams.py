import time
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .config import TEAMS_EMAIL, TEAMS_PASSWORD
from .browser import get_driver, display_screenshot, save_screenshot


# ==============================================================================
# XỬ LÝ POPUP & ĐIỀU HƯỚNG TRÊN TEAMS
# ==============================================================================
def dismiss_teams_popups(driver):
    """Tự động đóng các banner, popup và xử lý chuyển tiếp sang web app trên Teams."""
    try:
        # 1. Bấm nút 'Open Teams on the web' hoặc 'Use the web app instead' nếu xuất hiện
        web_btns = driver.find_elements(
            By.XPATH,
            '//button[contains(., "Open Teams on the web") or contains(., "Mở Teams trên web")] | '
            '//a[contains(., "Open Teams on the web") or contains(., "Mở Teams trên web")] | '
            '//button[contains(text(), "Use the web app") or contains(text(), "Dùng ứng dụng web")] | '
            '//a[contains(text(), "Use the web app") or contains(text(), "Dùng ứng dụng web")]',
        )
        for btn in web_btns:
            try:
                if btn.is_displayed():
                    driver.execute_script("arguments[0].click();", btn)
                    print("👉 Đã bấm nút 'Open Teams on the web' / 'Use the web app'")
                    time.sleep(2)
            except Exception:
                pass
    except Exception:
        pass

    try:
        # 2. Đóng banner thông báo / What's new / Dismiss / Notifications
        close_banner_btns = driver.find_elements(
            By.XPATH,
            '//button[contains(@aria-label, "Dismiss") or contains(@aria-label, "Đóng") or contains(@aria-label, "Close") '
            'or contains(., "Dismiss") or contains(., "Not now") or contains(., "Got it") or contains(., "Không phải lúc này")] '
            '| //div[contains(., "desktop notifications")]//button[contains(@aria-label, "Close") or contains(@aria-label, "Dismiss") or text()="X"]',
        )
        for btn in close_banner_btns:
            try:
                if btn.is_displayed():
                    driver.execute_script("arguments[0].click();", btn)
                    time.sleep(0.5)
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
# HỖ TRỢ XÁC THỰC KHUNG CHAT & SOẠN THẢO
# ==============================================================================
def get_chat_editor(driver, timeout: int = 20):
    """
    Tìm phần tử soạn thảo tin nhắn (CKEditor / contenteditable) đang hiển thị trong khung chat.
    Loại trừ hoàn toàn ô tìm kiếm hoặc bộ lọc.
    """
    editor_xpaths = [
        '//div[@data-tid="ckeditor-replyConversation"]//div[@contenteditable="true"]',
        '//div[contains(@class, "ck-editor__editable")]',
        '//div[@data-tid="ckeditor-replyConversation"]',
        '//div[@data-tid="chat-pane-compose"]//div[@contenteditable="true"]',
        '//div[@role="main"]//div[@contenteditable="true"]',
        '//div[@contenteditable="true"]',
    ]
    start = time.time()
    while time.time() - start < timeout:
        for xpath in editor_xpaths:
            try:
                elements = driver.find_elements(By.XPATH, xpath)
                for el in elements:
                    if el.is_displayed():
                        aria = (el.get_attribute("aria-label") or "").lower()
                        placeholder = (el.get_attribute("placeholder") or "").lower()
                        data_tid = (el.get_attribute("data-tid") or "").lower()
                        # Bỏ qua ô search/filter
                        if any(
                            k in aria or k in placeholder or k in data_tid
                            for k in ["search", "filter", "tìm kiếm", "lọc", "sticky-filter"]
                        ):
                            continue
                        return el
            except Exception:
                pass
        time.sleep(1)
    return None


def _activate_chat_item(driver, item_el) -> bool:
    """Kích hoạt click và mở nhóm chat bằng nhiều phương thức kết hợp."""
    try:
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", item_el)
        time.sleep(0.5)
    except Exception:
        pass

    # 1. Tìm phần tử con (span text, button, a) có thể click được bên trong
    click_target = item_el
    try:
        sub_targets = item_el.find_elements(
            By.XPATH,
            './/span[string-length(normalize-space(text())) > 2] | .//button | .//a | .//*[@role="button"]'
        )
        if sub_targets:
            click_target = sub_targets[0]
    except Exception:
        pass

    # 2. Click phần cứng qua ActionChains (chuỗi sự kiện chuột thực)
    clicked = False
    try:
        actions = ActionChains(driver)
        actions.move_to_element(click_target).pause(0.2).click().perform()
        clicked = True
    except Exception:
        pass

    # 3. Native element click
    if not clicked:
        try:
            click_target.click()
            clicked = True
        except Exception:
            pass

    # 4. JavaScript click trực tiếp lên cả phần tử con và phần tử cha
    try:
        driver.execute_script("""
            const el = arguments[0];
            const parent = arguments[1];
            el.focus();
            el.click();
            if (parent && parent !== el) {
                parent.click();
            }
        """, click_target, item_el)
    except Exception:
        pass

    # 5. Gửi phím ENTER vào phần tử để kích hoạt (chuẩn WAI-ARIA Treeview)
    try:
        item_el.send_keys(Keys.ENTER)
    except Exception:
        try:
            click_target.send_keys(Keys.ENTER)
        except Exception:
            pass

    return True


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
        message_box = get_chat_editor(driver, timeout=20)
        if not message_box:
            raise RuntimeError("Không tìm thấy ô soạn thảo tin nhắn (CKEditor) trong khung chat!")

        try:
            driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'}); arguments[0].focus();", message_box
            )
            time.sleep(1)
            message_box.click()
        except Exception:
            pass

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
            send_btns = driver.find_elements(
                By.XPATH,
                '//button[@data-tid="chatPane-send-message-button"] '
                '| //button[contains(@aria-label, "Send") or contains(@aria-label, "Gửi")]',
            )
            for btn in send_btns:
                if btn.is_displayed():
                    try:
                        actions = ActionChains(driver)
                        actions.move_to_element(btn).pause(0.2).click().perform()
                        sent = True
                        break
                    except Exception:
                        driver.execute_script("arguments[0].click();", btn)
                        sent = True
                        break
        except Exception:
            pass

        if not sent:
            try:
                message_box.send_keys(Keys.ENTER)
                sent = True
            except Exception:
                try:
                    message_box.send_keys(Keys.CONTROL, Keys.ENTER)
                    sent = True
                except Exception:
                    pass

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

    # 1. Thử tìm trong danh sách chat đang hiển thị sẵn
    chat_item_xpath = (
        '//*[contains(@data-tid, "chat-list-item") '
        'or contains(@data-tid, "chat-item") '
        'or @data-item-type="chat" '
        'or @role="listitem" '
        'or @role="treeitem"]'
    )

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
            aria_label = g.get_attribute("aria-label") or ""
            title_attr = g.get_attribute("title") or ""
            target_str = (txt + " " + aria_label + " " + title_attr).lower()

            clean_chat_name = chat_name.lower().strip()
            prefix = clean_chat_name[:15]
            is_match = (
                clean_chat_name in target_str
                or txt.lower() in clean_chat_name
                or clean_chat_name.startswith(txt.replace("...", "").strip().lower())
                or prefix in target_str
            )

            if is_match:
                print(f"👉 Tìm thấy nhóm trong danh sách: '{txt}'. Đang kích hoạt...")
                _activate_chat_item(driver, g)

                # Chờ editor xuất hiện trong khung chat
                editor = get_chat_editor(driver, timeout=12)
                if not editor:
                    try:
                        g.send_keys(Keys.ENTER)
                    except Exception:
                        pass
                    editor = get_chat_editor(driver, timeout=8)

                if editor:
                    display_screenshot(driver, "after_opening_chat.png")
                    print(f"📂 Đã mở đúng nhóm: {chat_name}")
                    return True
                else:
                    print(f"⚠️ Đã click nhóm '{txt}' nhưng khung chat chưa nạp xong. Thử lại qua Filter...")
                    break
    except Exception as e:
        print(f"ℹ️ Quét danh sách ngoài ({e}). Đang chuyển sang tìm bằng Filter...")

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

        # Trích xuất từ khóa tìm kiếm tốt nhất (ưu tiên từ khóa đặc trưng như gbBOSS nếu có)
        tokens = [w for w in re.split(r'[\s*_\-]+', chat_name) if len(w) >= 3 and w.lower() not in ["ix000s", "issale"]]
        search_keyword = tokens[0] if tokens else (chat_name.split()[0] if " " in chat_name else chat_name[:15])

        print(f"🔍 Đang lọc danh sách với từ khóa: '{search_keyword}'...")
        search.send_keys(search_keyword)
        time.sleep(3)

        filtered_result_xpath = (
            f"//*[contains(@data-tid, 'chat-list-item') or contains(@data-tid, 'chat-item') or @role='listitem' or @role='treeitem'][.//*[contains(text(), '{search_keyword}')]] "
            f"| //span[contains(normalize-space(text()), '{search_keyword}')]"
        )
        filtered_result = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, filtered_result_xpath))
        )
        _activate_chat_item(driver, filtered_result)

        editor = get_chat_editor(driver, timeout=15)
        if not editor:
            try:
                filtered_result.send_keys(Keys.ENTER)
            except Exception:
                pass
            editor = get_chat_editor(driver, timeout=8)

        if editor:
            display_screenshot(driver, "after_opening_chat.png")
            print(f"📂 Đã mở nhóm qua thanh Filter: {chat_name}")
            return True

        raise RuntimeError(f"Khung chat chưa sẵn sàng sau khi chọn nhóm qua filter '{search_keyword}'")

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

            # Xử lý màn hình "Personal accounts aren't supported yet in Teams"
            try:
                body_text = driver.find_element(By.TAG_NAME, "body").text.lower()
                if "personal accounts aren't supported" in body_text or "personal accounts" in body_text:
                    open_btns = driver.find_elements(
                        By.XPATH,
                        '//button[contains(., "Open Teams on the web") or contains(., "Mở Teams trên web")] | '
                        '//a[contains(., "Open Teams on the web") or contains(., "Mở Teams trên web")]'
                    )
                    for b in open_btns:
                        if b.is_displayed():
                            driver.execute_script("arguments[0].click();", b)
                            print("👉 Đã bấm nút 'Open Teams on the web' trên màn hình Personal accounts")
                            time.sleep(3)
                            break
                    time.sleep(2)
                    continue
            except Exception:
                pass

            # Đóng các banner, popup, và chuyển hướng web app nếu có
            dismiss_teams_popups(driver)

            is_login_domain = any(
                d in current_url
                for d in (
                    "login.microsoftonline.com",
                    "login.live.com",
                    "account.live.com",
                )
            )

            # Kiểm tra xem giao diện chính Teams (App bar Chat hoặc Tablist / Chat-item) đã xuất hiện chưa
            chat_indicators = driver.find_elements(
                By.XPATH,
                '//button[contains(@data-tid, "app-bar-chat") or contains(@aria-label, "Chat") or contains(@aria-label, "Trò chuyện")] '
                '| //div[@role="tablist"] '
                '| //div[contains(@data-tid, "chat-list-item") or contains(@data-tid, "chat-item")] '
                '| //div[@data-tid="app-bar-chat"]'
            )
            if chat_indicators and not is_login_domain:
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
