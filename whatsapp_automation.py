import threading
import random
from time import sleep
from typing import List, Dict, Any, Optional
from botasaurus.browser import Driver, Wait, browser
from helper_functions import get_profile, make_data_item, write_message, read_json


class WhatsAppSender:
    def __init__(self):
        self.start_event = threading.Event()
        self.stop_event = threading.Event()  # للتحكم في التوقيف المؤقت
        self.send_lock = threading.Lock()
        self.browsers_threads: List[threading.Thread] = []
        self.drivers: Dict[str, Driver] = {}
        self.drivers_lock = threading.Lock()
        self.browsers_opened: bool = False
        self.json_data = read_json()
        self.all_drivers_ready = threading.Event()

        # للحفاظ على حالة الإرسال عند pause/resume
        self._sending_state = {
            "recipients": [],
            "senders": [],
            "messages": [],
            "min_delay": 1.0,
            "max_delay": 3.0,
            "on_message_sent": None,
            "current_index": 0,
            "thread": None,
            "settings":{}
        }

    # ------------------------ إدارة المتصفحات ------------------------
    
    
    def _start_driver_for(self, data_item: Dict[str, Any]):
        @browser(close_on_crash=True, profile=get_profile) # to not retrying open browsers again of crash
        def run_browser(driver: Driver, data):
            phone = str(data.get("phone_number", "unknown"))
            try:
                profile_path = get_profile(data)
                print(profile_path)
                with self.drivers_lock:
                    self.drivers[phone] = driver

                driver.enable_human_mode()
                driver.google_get("https://web.whatsapp.com/")
                sleep(random.uniform(4, 8))
                driver.run_js(f'document.title = "📞 {phone}";')
                print(f"[{phone}] ✅ WhatsApp browser ready.")
                self.all_drivers_ready.set()

                while not self.stop_event.is_set():
                    sleep(1)

            except Exception as e:
                print(f"[{phone}] exception in driver thread: {e}")

        run_browser(data_item)


    def open_browser_only(self, numbers_open: List[str]):

        for k, v in self.drivers.items():
            if k in numbers_open:
                try:
                    index_ = numbers_open.index(k)
                    try:
                        self.drivers.get(k).current_url
                        numbers_open.pop(index_)
                    except Exception as e:
                        pass
                except Exception as e:
                    print(e)

        try:
            if len(numbers_open) == 0:
                return
            data_items = [make_data_item(p) for p in numbers_open]
            for item in data_items:
                t = threading.Thread(
                    target=self._start_driver_for, args=(item,), daemon=True
                )
                t.start()
                self.browsers_threads.append(t)
            self.browsers_opened = True
        except Exception as e:
            print(f">> {e}")

        print(
            f"Started {len(self.browsers_threads)} browser thread(s). Log in to each if needed."
        )

    # add this because i need if sender whatsapp tap close every whatsapp close
    def close_drivers(self):
        # إشارة لإيقاف الحلقات داخل Threads
        self.stop_event.set()

        # إغلاق جميع الـ Drivers المفتوحين
        with self.drivers_lock:
            for phone, drv in self.drivers.items():
                try:
                    print(f"[{phone}] 🔻 Closing driver...")
                    drv.close()
                except Exception as e:
                    print(f"[{phone}] ⚠️ Error closing driver: {e}")
            self.drivers.clear()

        # انتظار انتهاء جميع الـ Threads
        for t in self.browsers_threads:
            try:
                t.join(timeout=3)
            except Exception:
                pass

        self.browsers_threads.clear()
        self.browsers_opened = False
        print("✅ All drivers closed and threads cleaned.")

    def _collect_drivers(self, timeout: float = 30.0) -> Dict[str, Driver]:
        from time import time

        end = time() + timeout
        while time() < end:
            with self.drivers_lock:
                if len(self.drivers) >= 1:
                    return dict(self.drivers)
            sleep(0.5)
        with self.drivers_lock:
            return dict(self.drivers)

    # ------------------------ إرسال الرسائل ------------------------
    def logic_to_send(
        self, driver: Driver, assigned_number: str, receiver: str, message: str, way_to_send: str
    ):
        
        
        def __send_message():
            "because if any cases we send message with the same way"
            driver.wait_for_element(selector=self.json_data["general"]["type_message_ele"]).click()
            
            driver.long_random_sleep()
            
            write_message(driver, message, is_message=True)
            sleep(random.uniform(1.5, 5))
            try:
                driver.wait_for_element(
                    selector=self.json_data["general"]["send_button_1"]
                ).click()
            except Exception:
                driver.wait_for_element(
                    selector=self.json_data["general"]["send_button_2"]
                ).click()

        
        try:
            match way_to_send:
                case 'google_contacts':
                    random_way = random.randint(1,2)
                    
                    match random_way:
                        case 1 :
                            #* here way_to_send = google_contacts
                            search_box = driver.get_element_containing_text(
                                "Search or start a new chat", wait=Wait.VERY_LONG
                            )
                            search_box.click()
                            write_message(driver, assigned_number, is_message=False)
                            sleep(random.uniform(1, 2.5))
                            driver.short_random_sleep()

                            first_chat = driver.is_element_present(
                                selector=self.json_data[way_to_send]["first_chat"]
                            )
                            
                            if first_chat:
                                driver.wait_for_element(selector=self.json_data[way_to_send]["first_chat"]).click()
                            else:
                                driver.wait_for_element(
                                    selector=self.json_data[way_to_send]["clear_button"], wait=Wait.VERY_LONG
                                ).click()
                                print(f"[{receiver}] ⚠️ Number {assigned_number} not found")
                                return "Number Not Found or Not Have Whatsapp"

                            driver.wait_for_element(selector=self.json_data[way_to_send]["type_message_ele"]).click()
                            driver.long_random_sleep()
                            write_message(driver, message, is_message=True)
                            sleep(random.uniform(1.5, 5))
                            
                            __send_message()

                            print(f"[{receiver}] ✅ Sent to {assigned_number}")
                        case 2:
                            click_new_chat = driver.wait_for_element(selector=self.json_data[way_to_send]['button_new_chat'])
                            click_new_chat.click()
                            
                            write_message(driver, assigned_number, is_message=False)
                            
                            driver.short_random_sleep()
                            
                            if first_chat:
                                driver.wait_for_element(selector=self.json_data[way_to_send]["first_chat2"]).click()
                            else:
                                driver.wait_for_element(
                                    selector=self.json_data[way_to_send]["clear_button2"], wait=Wait.VERY_LONG
                                ).click()
                                print(f"[{receiver}] ⚠️ Number {assigned_number} not found")
                                return "Number Not Found or Not Have Whatsapp"
                        
                            __send_message()

                        
        except Exception as e:
            print(f">>>> send error {e}")

    def _send_loop(self):
        state = self._sending_state
        senders = state["senders"]
        recipients = state["recipients"]
        messages = state["messages"]
        n_senders = len(senders)
        on_message_sent = state["on_message_sent"]
        min_delay = state["min_delay"]
        max_delay = state["max_delay"]
        settings = state["settings"]

        drivers = self._collect_drivers(timeout=30.0)
        sender_drivers: Dict[str, Driver] = {}
        for s in senders:
            key = str(s)
            if key in drivers:
                sender_drivers[key] = drivers[key]
            else:
                raise ValueError(
                    f"Sender {s} not found among opened browsers: {list(drivers.keys())}"
                )

        idx = state["current_index"]
        while idx < len(recipients):
            if self.stop_event.is_set():
                print("Pause signal received. Sending paused.")
                break

            recipient = recipients[idx]
            sender_index = idx % n_senders
            sender_phone = str(senders[sender_index])
            driver = sender_drivers[sender_phone]
            message = random.choice(messages)
            way_to_send = settings['ways_to_send']
            print(way_to_send)


                
            
            # ways_approve = random.choice([{way:status  for way, status in settings.items() if status == True}])
            try:
                with self.send_lock:
                    results = self.logic_to_send(
                        driver,
                        assigned_number=recipient[0],
                        receiver=sender_phone,
                        message=message,
                        way_to_send=""
                    )
                    if on_message_sent:
                        if results == ("Number Not Found or Not Have Whatsapp"):
                            on_message_sent(recipient, None)
                        else:
                            on_message_sent(recipient, sender_phone)
            except Exception as e:
                print(f"Error sending from {sender_phone} to {recipient}: {e}")

            state["current_index"] = idx + 1
            idx += 1
            sleep(random.uniform(min_delay, max_delay))

        if idx >= len(recipients):
            print("Finished sending all messages.")

    def start_sending(
        self,
        senders: List[str],
        recipients: List[str],
        messages: List[str],
        settings: dict[str, bool], 
        min_delay: float = 1.0,
        max_delay: float = 3.0,
        background: bool = False,
        on_message_sent=None,
    ):
        if not self.browsers_opened:
            raise RuntimeError(
                "Browsers are not open. Call open_browser_only(...) first."
            )

        # حفظ حالة الإرسال للـ pause/resume
        self._sending_state.update(
            {
                "recipients": recipients,
                "senders": senders,
                "messages": messages,
                "min_delay": min_delay,
                "max_delay": max_delay,
                "on_message_sent": on_message_sent,
                "current_index": 0,
                "settings":settings
            }
        )

        if background:
            t = threading.Thread(target=self._send_loop, daemon=True)
            t.start()
            self._sending_state["thread"] = t
            return t
        else:
            self._send_loop()

    def stop_sending(self):
        """Pause sending (thread stays alive)."""
        print("Pausing sending...")
        self.stop_event.set()

    def resume_sending(self):
        """Resume sending from last paused index."""
        if not self._sending_state["recipients"]:
            print("No sending state found. Cannot resume.")
            return
        if (
            self._sending_state.get("thread")
            and self._sending_state["thread"].is_alive()
        ):
            print("Already running. Clearing pause flag...")
            self.stop_event.clear()
            return

        print("Resuming sending...")
        self.stop_event.clear()
        t = threading.Thread(target=self._send_loop, daemon=True)
        t.start()
        self._sending_state["thread"] = t


if __name__ == "__main__":
    sender = WhatsAppSender()
    senders = ["201505177473"]
    sender.open_browser_only(senders)

    input("بعد تسجيل الدخول في كل نافذة اضغط Enter لبدء الإرسال...")

    recipients = ["201002097448", "201013416458", "201093998000"]
    messages = ["أهلاً 🌟", "رسالة تجريبية", "مرحباً، هذا اختبار"]

    sender.start_sending(
        senders, recipients, messages, min_delay=1.5, max_delay=3.5, background=True
    )

    print("العملية شغالة في الخلفية... اضغط Ctrl + C للإيقاف.")

    # 🔴 هـــــــــــــام: منع غلق البرنامج
    while True:
        sleep(1)


whatsapp_app = WhatsAppSender()
