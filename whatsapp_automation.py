import multiprocessing
import random
import csv
from datetime import datetime
from time import sleep
from colorama import Fore, init
import psutil
from helper_functions import *
from botasaurus.browser import browser, Driver, Wait

# ✅ تهيئة الألوان في الكونسول
init(autoreset=True)

start_event = multiprocessing.Event()
send_lock = multiprocessing.Lock()
json_data = read_json()


class NotFoundNumber(Exception):
    pass


# =========================================================
# ✅ دوال مساعدة
# =========================================================
def is_browser_open(driver: Driver):
    try:
        driver.get_page_source()
        return True
    except Exception:
        return False


def is_profile_running(profile_name: str) -> bool:
    for proc in psutil.process_iter(['name', 'cmdline']):
        try:
            if proc.info['name'] and "chrome" in proc.info['name'].lower():
                if profile_name in " ".join(proc.info.get('cmdline', [])):
                    return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return False


# =========================================================
# ✅ كتابة الرسائل بطريقة آمنة
# =========================================================
def write_message(driver: Driver, message: str, is_message: bool):
    safe_message = message.replace("`", "\\`").replace("\n", "\\n")
    driver.run_js(f'''
        const input = document.querySelector('div[contenteditable="true"][role="textbox"][data-tab="{'10' if is_message else '3'}"]');
        const dataTransfer = new DataTransfer();
        dataTransfer.setData('text', `{safe_message}`);

        const event = new ClipboardEvent('paste', {{
            clipboardData: dataTransfer,
            bubbles: true
        }});

        input.focus();
        input.dispatchEvent(event);
    ''')


# =========================================================
# ✅ تسجيل كل إرسال في ملف CSV
# =========================================================
def log_sent_message(profile_number, recipient_number, message):
    filename = f"logs_{profile_number}.csv"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(filename, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, profile_number, recipient_number, message])


# =========================================================
# ✅ فتح واتساب لكل بروفايل
# =========================================================
@browser(profile=get_profile)
def open_whatsapp_browser(driver: Driver, data, start_sending=True, update_gui_callback=None):
    sender_phone = data["phone_number"]
    messages = data["messages"]
    numbers = data["numbers"]

    try:
        driver.enable_human_mode()
        driver.google_get("https://web.whatsapp.com/", timeout=180)
        driver.wait_for_element("body", wait=Wait.VERY_LONG)
        sleep(random.uniform(5, 10))
        driver.run_js(f'document.title = "📞 {sender_phone}";')
        print(Fore.CYAN + f"[{sender_phone}] ✅ WhatsApp loaded successfully.")

        if not start_sending:
            print(Fore.GREEN + f"[{sender_phone}] 🟢 Browser opened only (no sending).")
            while is_browser_open(driver):
                sleep(2)
            return

        print(Fore.YELLOW + f"[{sender_phone}] Waiting for start signal...")
        start_event.wait()
        run_sender_logic(driver, sender_phone, numbers, messages, update_gui_callback)

    finally:
        if is_browser_open(driver):
            try:
                driver.close()
            except:
                pass
        print(Fore.MAGENTA + f"[{sender_phone}] 🔚 Browser closed, process finished.")


# =========================================================
# ✅ منطق الإرسال لكل رقم مع تحديث GUI
# =========================================================
def run_sender_logic(driver: Driver, sender_phone, numbers, messages, update_gui_callback=None):
    numbers_to_send = numbers.copy()
    random.shuffle(numbers_to_send)

    for assigned_number in numbers_to_send:
        if not is_browser_open(driver):
            print(Fore.RED + f"[{sender_phone}] ❌ Browser closed — stopping sender.")
            break

        msg_to_send = random.choice(messages)

        try:
            with send_lock:
                search_box = driver.get_element_containing_text(
                    "Search or start a new chat", wait=Wait.VERY_LONG
                )
                search_box.click()
                write_message(driver, assigned_number, is_message=False)
                sleep(random.uniform(1, 3))

                first_chat = driver.is_element_present(selector=json_data["first_chat"])
                if first_chat:
                    driver.wait_for_element(selector=json_data["first_chat"]).click()
                else:
                    driver.wait_for_element(selector=json_data["clear_button"], wait=Wait.VERY_LONG).click()
                    print(Fore.YELLOW + f"[{sender_phone}] ⚠️ Number {assigned_number} not found")
                    continue

                driver.wait_for_element(selector=json_data["type_message_ele"]).click()
                write_message(driver, msg_to_send, is_message=True)
                sleep(random.uniform(2, 4))

                try:
                    driver.wait_for_element(selector=json_data["send_button_1"]).click()
                except:
                    driver.wait_for_element(selector=json_data["send_button_2"]).click()

                print(Fore.GREEN + f"[{sender_phone}] ✅ Sent to {assigned_number}")
                log_sent_message(sender_phone, assigned_number, msg_to_send)

                # 🔹 تحديث GUI إذا موجود
                if update_gui_callback:
                    update_gui_callback(assigned_number, sender_phone)

        except Exception as e:
            if "10061" in str(e):
                print(Fore.RED + f"[{sender_phone}] 🔌 Lost Chrome connection — stopping browser.")
                break
            else:
                print(Fore.RED + f"[{sender_phone}] ❌ Unexpected error: {e}")
                continue

        sleep(random.uniform(5, 12))


# =========================================================
# ✅ إدارة العمليات لجميع البروفايلات
# =========================================================
def run(channels_numbers, messages, sender_numbers, open_only=False, update_gui_callback=None):
    processes = []

    for channel in channels_numbers:
        if is_profile_running(channel):
            print(Fore.YELLOW + f"⚠️ Profile '{channel}' is already running. Skipping...")
            continue

        data = {
            "phone_number": channel,
            "profile": channel,
            "messages": messages,
            "numbers": sender_numbers,
        }

        p = multiprocessing.Process(
            target=open_whatsapp_browser,
            args=(data, not open_only, update_gui_callback),
        )
        p.start()
        processes.append(p)

    if not processes:
        print(Fore.RED + "\n❌ No browsers launched. All profiles already running.")
        return

    if open_only:
        print(Fore.CYAN + "\n🟢 All browsers opened (no sending).")
    else:
        print(Fore.CYAN + "\n✅ All browsers launched.")
        input(Fore.YELLOW + "👉 Press Enter to start sending...\n")
        start_event.set()

    for p in processes:
        p.join()

    print(Fore.GREEN + "\n🎯 All processes finished.")
