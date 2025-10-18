from helper_functions import *
from botasaurus.browser import browser, Driver, Wait
import threading
import random
from time import sleep
from typing import List, Dict, Any

# ✅ أحداث التحكم العامة
start_event = threading.Event()
stop_event = threading.Event()
send_lock = threading.Lock()

json_data: Dict[str, Any] = read_json()

# 🟢 لتخزين حالة كل متصفح مفتوح
browsers_threads: List[threading.Thread] = []
browsers_opened: bool = False



@browser(profile=get_profile)
def open_browser(driver:Driver, data):
    sender_phone:list = data["phone_number"]
    driver.enable_human_mode()
    driver.google_get("https://web.whatsapp.com/")
    sleep(random.uniform(5, 10))
    driver.run_js(f'document.title = "📞 {sender_phone}";')
    print(f"[{sender_phone}] ✅ Browser ready.")
    browsers_threads.append(threading.current_thread)
    # انتظار start event
    start_event.wait()
    while True:
        assigned_number = None
        messages = []

        try:
            with send_lock:  # ✅ 🔒 القفل العام هنا
                # افتح المحادثة
                driver.get_element_containing_text("(You)", wait=Wait.VERY_LONG).click()
                driver.wait_for_element(selector=json_data['input_filed']).click()

                write_message(driver, f"https://web.whatsapp.com/send?phone={assigned_number}")
                sleep(random.uniform(1, 3))

                try:
                    driver.wait_for_element(selector=json_data['send_button_1']).click()
                except:
                    driver.wait_for_element(selector=json_data['send_button_2']).click()

                sleep(random.uniform(1, 3))
                driver.get_all_elements_containing_text("web.whatsapp.com")[-1].click()
                sleep(random.uniform(1, 3))

                if driver.is_element_present(json_data["ok_no_phone"]):
                    print(f"[{}] {assigned_number} is not on WhatsApp.")
                    continue

                msg_to_send = random.choice(messages)
                write_message(driver, msg_to_send)

                try:
                    driver.wait_for_element(selector=json_data['send_button_1']).click()
                except:
                    driver.wait_for_element(selector=json_data['send_button_2']).click()

                print(f"[{selected_category}] ✅ Message sent to {assigned_number} from [{sender_phone}]")
                sleep(random.uniform(2, 4))
        except AttributeError:
            stop_event.set()
            try:
                driver.close()
            except:
                pass
            
        except Exception as e:
            print(f"[] ❌ Error with : {e}")
            continue


def start_sending(receivers: List[str], messages: List[str]) -> None:
    """تفعيل إرسال الرسائل بعد فتح المتصفحات
    :param receivers: قائمة أرقام المستلمين
    :param messages: قائمة الرسائل
    """
    global browsers_threads, browsers_opened

    if not browsers_opened or not browsers_threads:
        print("⚠️ Please open browsers first before sending.")
        return

    stop_event.clear()
    start_event.set()  # تفعيل الـ event لكل المتصفحات

    print("🚀 Sending started...")

    # لكل thread مرتبط بالمتصفح نضيف إرسال الرسائل
    for t in browsers_threads:
        if not t.is_alive():
            t.start()  # شغّل الـ thread لو مش شغّال


# def open_browser_for_sender(
#     sender_data: Dict[str, str],
#     receivers: List[str],
#         messages: List[str]):
#     """
#     فتح متصفح واحد لكل sender والعمل على الإرسال داخله مباشرة
#     """
#     @browser(profile=get_profile)
#     def inner(driver: Driver):
#         sender_phone = sender_data["phone_number"]
#         driver.enable_human_mode()
#         driver.google_get("https://web.whatsapp.com/")
#         sleep(random.uniform(5, 10))
#         driver.run_js(f'document.title = "📞 {sender_phone}";')
#         print(f"[{sender_phone}] ✅ Browser ready.")

#         # انتظار start event
#         start_event.wait()

#         for receiver in receivers:
#             if stop_event.is_set():
#                 print(f"[{sender_phone}] 🛑 Sending stopped for this sender.")
#                 break

#             receiver = receiver.strip()
#             if not receiver:
#                 continue

#             try:
#                 with send_lock:
#                     # افتح مربع الكتابة
#                     driver.get_element_containing_text("(You)", wait=Wait.VERY_LONG).click()
#                     driver.wait_for_element(selector=json_data['input_filed']).click()

#                     # افتح شات الرقم
#                     write_message(driver, f"https://web.whatsapp.com/send?phone={receiver}")
#                     sleep(random.uniform(1, 3))

#                     try:
#                         driver.wait_for_element(selector=json_data['send_button_1']).click()
#                     except:
#                         driver.wait_for_element(selector=json_data['send_button_2']).click()

#                     sleep(random.uniform(1, 3))
#                     driver.get_all_elements_containing_text("web.whatsapp.com")[-1].click()
#                     sleep(random.uniform(1, 3))

#                     # تحقق من وجود الرقم
#                     if driver.is_element_present(json_data["ok_no_phone"]):
#                         print(f"[{sender_phone}] ⚠️ {receiver} is not on WhatsApp.")
#                         continue

#                     # أرسل الرسالة
#                     msg_to_send: str = random.choice(messages)
#                     write_message(driver, msg_to_send)

#                     try:
#                         driver.wait_for_element(selector=json_data['send_button_1']).click()
#                     except:
#                         driver.wait_for_element(selector=json_data['send_button_2']).click()

#                     print(f"[{sender_phone}] ✅ Message sent to {receiver}")
#                     sleep(random.uniform(2, 4))

#             except Exception as e:
#                 print(f"[{sender_phone}] ❌ Error sending to {receiver}: {e}")
#                 continue

#     inner()


# def open_all_browsers(senders: List[str]) -> None:
#     """
#     فتح كل المتصفحات فقط بدون مشاكل serialization
#     """
#     global browsers_threads, browsers_opened

#     browsers_threads.clear()
#     stop_event.clear()
#     start_event.clear()
#     browsers_opened = False

#     print(f"📌 Attempting to open {len(senders)} browsers...")

#     for sender in senders:
#         if isinstance(sender, str):
#             sender_data = {"phone_number": sender, "profile": sender}
#         elif isinstance(sender, dict):
#             sender_data = sender
#         else:
#             print(f"⚠️ Skipping unsupported sender type: {sender}")
#             continue

#         # t = threading.Thread(target=open_browser_for_sender, args=(sender_data, receivers, messages), daemon=True)
#         # t.start()
#         # browsers_threads.append(t)

#     browsers_opened = True
#     print(f"🟢 {len(browsers_threads)} browsers are now open and ready.")


# def start_sending() -> None:
#     """تفعيل إرسال الرسائل بعد فتح المتصفحات"""
#     if not browsers_opened or not browsers_threads:
#         print("⚠️ Please open browsers first before sending.")
#         return

#     stop_event.clear()
#     start_event.set()
#     print("🚀 Sending started...")


def stop_sending() -> None:
    """إيقاف عملية الإرسال فقط بدون إغلاق المتصفحات"""
    stop_event.set()
    print("🛑 Sending stopped (browsers remain open).")
