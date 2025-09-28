from helper_functions import *
from botasaurus.browser import browser, Driver, Wait
import threading
import random
from time import sleep

start_event = threading.Event()
stop_event = threading.Event()  # لإيقاف جميع الـ threads في حالة الخطأ
send_lock = threading.Lock()  # 🔒 قفل عام لمنع الإرسال المتزامن

json_data = read_json()

# حفظ بيانات كل فئة
categories_data = {
    "Nafs": {
        "numbers": get_numbers("nafs"),
        "messages": get_message("nafs"),
        "index": 0,
        "lock": threading.Lock()
    },
    "Tarbawy": {
        "numbers": get_numbers("tarbawy"),
        "messages": get_message("tarbawy"),
        "index": 0,
        "lock": threading.Lock()
    }
}


@browser(profile=get_profile)
def open_whatsapp(driver: Driver, data):
    sender_phone = data["phone_number"]

    driver.enable_human_mode()
    driver.google_get("https://web.whatsapp.com/")
    sleep(random.uniform(5, 10))
    driver.run_js(f'document.title = "📞 {sender_phone}";')

    print(f"[{sender_phone}] Waiting to start")
    start_event.wait()

    # # ✅ مراقبة التايتل في الخلفية
    # def monitor_title():
    #     while not stop_event.is_set():
    #         try:
    #             current_title = driver.run_js("return document.title;")
    #             if "واتساب" in current_title or "WhatsApp" in current_title:
    #                 driver.run_js(f'document.title = "📞 {sender_phone}";')
    #         except:
    #             break
    #         sleep(5)  # راجع كل 5 ثواني

    # threading.Thread(target=monitor_title, daemon=True).start()

    # لتحديد التبديل بين الفئات
    if not hasattr(threading.current_thread(), "last_category"):
        threading.current_thread().last_category = "Tarbawy"  # لكي تكون البداية مع Nafs

    while True:
        selected_category = None
        assigned_number = None
        messages = []

        # حدد الفئة التالية بالتناوب
        next_category = "Nafs" if threading.current_thread().last_category == "Tarbawy" else "Tarbawy"

        # جرّب الفئة المطلوبة أولاً، وإذا فاضية جرّب الأخرى
        for attempt in [next_category, "Tarbawy" if next_category == "Nafs" else "Nafs"]:
            cat_data = categories_data[attempt]
            with cat_data["lock"]:

                if cat_data["index"] < len(cat_data["numbers"]):
                    assigned_number = cat_data["numbers"][cat_data["index"]].strip()
                    cat_data["index"] += 1
                    selected_category = attempt
                    messages = cat_data["messages"]
                    threading.current_thread().last_category = selected_category
                    break

        if not selected_category:
            print(f"[{sender_phone}] ✅ No more numbers to process. Exiting...")
            break

        print(f"[{selected_category}] {sender_phone} preparing to send to {assigned_number}")

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
                    print(f"[{selected_category}] {assigned_number} is not on WhatsApp.")
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
            print(f"[{selected_category}] ❌ Error with {assigned_number}: {e}")
            continue


def main():
    threads = []

    all_senders = [
        {"phone_number": "201505377476", "profile": "201505377476"},
        {"phone_number": "201206226048", "profile": "201206226048"},
        {"phone_number": "201280578648", "profile": "201280578648"},
        {"phone_number": "201205217358", "profile": "201205217358"},
        {"phone_number": "201278846164", "profile": "201278846164"},
        # {"phone_number": "201206914284", "profile": "201206914284"},
        {"phone_number": "201289422415", "profile": "201289422415"},
        # {"phone_number": "201289427756", "profile": "201289427756"},
        # {"phone_number": "201221775260", "profile": "201221775260"},
        # {"phone_number": "201280576245", "profile": "201280576245"},
    ]

    for sender in all_senders:
        data = {
            "phone_number": sender["phone_number"],
            "profile": sender["profile"]
        }
        t = threading.Thread(target=open_whatsapp, args=(data,))
        t.start()
        threads.append(t)

    input("Start all browsers? (اضغط Enter للبدء)\n")
    start_event.set()

    for t in threads:
        t.join()


if __name__ == "__main__":
    main()
