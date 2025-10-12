import multiprocessing
import random
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
    """يتأكد إن المتصفح لسه شغال."""
    try:
        driver.get_page_source()
        return True
    except Exception:
        return False


def is_profile_running(profile_name: str) -> bool:
    """يتأكد إن بروفايل Chrome ده مفتوح بالفعل."""
    for proc in psutil.process_iter(['name', 'cmdline']):
        try:
            if proc.info['name'] and "chrome" in proc.info['name'].lower():
                if profile_name in " ".join(proc.info.get('cmdline', [])):
                    return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return False


# =========================================================
# ✅ فتح واتساب فقط (بدون إرسال)
# =========================================================
@browser(profile=get_profile)
def open_whatsapp_browser(driver: Driver, data, start_sending=True):
    """يفتح واتساب ويب، ولو start_sending=True يبدأ الإرسال."""
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

        # 🔹 لو start_sending=True — يبدأ المنطق بعد الإشارة
        print(Fore.YELLOW + f"[{sender_phone}] Waiting for start signal...")
        start_event.wait()
        run_sender_logic(driver, sender_phone, numbers, messages)

    finally:
        if is_browser_open(driver):
            try:
                driver.close()
            except:
                pass
        print(Fore.MAGENTA + f"[{sender_phone}] 🔚 Browser closed, process finished.")


# =========================================================
# ✅ منطق الإرسال فقط
# =========================================================
def run_sender_logic(driver: Driver, sender_phone, numbers, messages):
    """منطق إرسال الرسائل بعد فتح واتساب."""
    while True:
        if not is_browser_open(driver):
            print(Fore.RED + f"[{sender_phone}] ❌ Browser closed — stopping sender.")
            break

        assigned_number = numbers
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
                    driver.wait_for_element(
                        selector=json_data["clear_button"], wait=Wait.VERY_LONG
                    ).click()
                    raise NotFoundNumber()

                driver.wait_for_element(selector=json_data["type_message_ele"]).click()
                write_message(driver, msg_to_send, is_message=True)
                sleep(random.uniform(2, 4))

                try:
                    driver.wait_for_element(selector=json_data["send_button_1"]).click()
                except:
                    driver.wait_for_element(selector=json_data["send_button_2"]).click()

                print(Fore.GREEN + f"[{sender_phone}] ✅ Sent to {assigned_number}")

        except NotFoundNumber:
            print(Fore.YELLOW + f"[{sender_phone}] ⚠️ Number {assigned_number} not found")

        except Exception as e:
            if "10061" in str(e):
                print(Fore.RED + f"[{sender_phone}] 🔌 Lost Chrome connection — closing browser.")
                break
            else:
                print(Fore.RED + f"[{sender_phone}] ❌ Unexpected error: {e}")
                continue

        sleep(random.uniform(3, 8))


# =========================================================
# ✅ مدير العمليات (فتح + إرسال)
# =========================================================
def run(channels_numbers, messages, sender_numbers, open_only=False):
    """يفتح بروفايلات واتساب فقط أو يبدأ الإرسال."""
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
            args=(data, not open_only),  # لو open_only=True ⇒ start_sending=False
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
