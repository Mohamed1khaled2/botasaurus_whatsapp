from helper_functions import *
from botasaurus.browser import browser, Driver, Wait
import threading
import random
from time import sleep

start_event = threading.Event()
send_lock = threading.Lock()  # 🔒 قفل عام لمنع الإرسال المتزامن
json_data = read_json()

# ✅ حفظ بيانات كل فئة
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
    },
    "Taghzia": {
        "numbers": get_numbers("taghzia"),
        "messages": get_message("taghzia"),
        "index": 0,
        "lock": threading.Lock()
    }
}

# ✅ الأرقام الخاصة بفئة التغذية فقط
nutrition_senders = [
    "201289427787", 
    "201208978327"
]



@browser(profile=get_profile)
def open_whatsapp(driver: Driver, data):
    sender_phone = data["phone_number"]

    driver.enable_human_mode()
    driver.google_get("https://web.whatsapp.com/")
    sleep(random.uniform(5, 10))
    driver.run_js(f'document.title = "📞 {sender_phone}";')

    print(f"[{sender_phone}] Waiting to start")
    start_event.wait()

    # ✅ لو الرقم من أرقام التغذية → يشتغل على "Taghzia" فقط
    is_nutrition_sender = sender_phone in nutrition_senders
    if is_nutrition_sender:
        categories_order = ["Taghzia"]
    else:
        categories_order = ["Nafs", "Tarbawy"]

    # لتحديد التبديل بين الفئات
    if not hasattr(threading.current_thread(), "last_category"):
        threading.current_thread().last_category = categories_order[0]

    while True:
        selected_category = None
        assigned_number = None
        messages = []

        # حدد الفئة التالية بالتناوب
        if len(categories_order) > 1:
            next_category = (
                categories_order[0]
                if threading.current_thread().last_category == categories_order[1]
                else categories_order[1]
            )
        else:
            next_category = categories_order[0]

        # ✅ جرب الفئة المطلوبة أولاً، وإذا فاضية جرب الأخرى
        for attempt in [next_category] + [c for c in categories_order if c != next_category]:
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
                driver.get_element_containing_text("Search or start a new chat", wait=Wait.VERY_LONG).click()
                write_message(driver, f"{assigned_number}", is_message=False)
                sleep(random.uniform(1, 3))
                first_chat = driver.is_element_present(selector=json_data['first_chat'])    
                
                if first_chat :
                    driver.wait_for_element(selector=json_data['first_chat']).click()
                else :
                    driver.wait_for_element(selector="#side > div._ak9t > div > div._ai04 > span > button", wait=Wait.VERY_LONG).click()
                    continue
                
                
                sleep(random.uniform(1, 3))
                driver.wait_for_element(selector=json_data['type_message_ele']).click()

                msg_to_send = random.choice(messages)
                write_message(driver, msg_to_send, is_message=True)
                sleep(random.uniform(1, 3))

                try:
                    driver.wait_for_element(selector=json_data['send_button_1']).click()
                except:
                    driver.wait_for_element(selector=json_data['send_button_2']).click()

                print(f"[{selected_category}] ✅ Message sent to {assigned_number} from [{sender_phone}]")
                sleep(random.uniform(2, 4))

        except AttributeError:
            # ✅ BAN detected → رجع الرقم مكانه وما يضيعش
            print(f"[{selected_category}] 🚫 BAN detected for {sender_phone}. Closing driver...")
            if assigned_number:
                cat_data = categories_data[selected_category]
                with cat_data["lock"]:
                    cat_data["index"] -= 1
                    if cat_data["index"] < 0:
                        cat_data["index"] = 0
            try:
                driver.close()
            except:
                pass
            break  # ❌ يخرج من اللوب لهذا المرسل فقط

        except Exception as e:
            print(f"[{selected_category}] ❌ Error with {assigned_number}: {e}")
            continue


def main():
    threads = []

    # * !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! بنحط هنا الارقام اللي هنشغلها
    all_senders = [
        {"phone_number": "201552436501", "profile": "201552436501"},
        {"phone_number": "201505377476", "profile": "201505377476"},
        {"phone_number": "201289427787", "profile": "201289427787"},  # تغذية
        {"phone_number": "201208978327", "profile": "201208978327"},  # تغذية
    ]
    # * !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

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
