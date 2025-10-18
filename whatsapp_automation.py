import threading
import random
from time import sleep, time
from typing import List, Dict, Any, Optional
from botasaurus.browser import Driver, Wait
from helper_functions import get_profile, make_data_item, write_message, read_json

class WhatsAppSender:
    """
    Driver-per-thread implementation (fallback to the approach you originally used).
    - Creates a Thread per sender phone.
    - Each thread instantiates its own Driver (attempts to reuse profile folder).
    - Keeps mapping self.drivers: phone -> Driver for start_sending().
    """

    def __init__(self):
        self.start_event = threading.Event()
        self.stop_event = threading.Event()
        self.send_lock = threading.Lock()

        # threads & drivers
        self.browsers_threads: List[threading.Thread] = []
        self.drivers: Dict[str, Driver] = {}        # phone -> driver
        self.drivers_lock = threading.Lock()
        self.browsers_opened: bool = False

        # selectors / settings from your helper json
        self.json_data = read_json()

        # event to signal driver collection complete (best-effort)
        self.all_drivers_ready = threading.Event()

    def _start_driver_for(self, data_item: Dict[str, Any]):
        """
        Run in a dedicated Thread: create Driver, open whatsapp web, attach to thread.
        data_item is a dict from make_data_item(...)
        """
        phone = str(data_item.get("phone_number", "unknown"))
        try:
            # get (and create) profile path for this phone using helper
            profile_path = get_profile(data_item)
            drv: Optional[Driver] = None

            # Try to pass profile path to Driver if supported by your botasaurus version
            try:
                if profile_path:
                    # many Driver implementations accept profile or user_data_dir kw
                    # we try common parameter name 'profile' first
                    drv = Driver(profile=profile_path)
                else:
                    drv = Driver()
            except TypeError:
                # Driver constructor doesn't accept 'profile' — fall back to default Driver()
                print(f"[{phone}] Driver(...) doesn't accept 'profile' parameter; falling back to default Driver() (session persistence may not work).")
                drv = Driver()
            except Exception as e:
                # Unexpected error constructing driver with profile — fallback to default
                print(f"[{phone}] Failed to start Driver(profile=...): {e} — falling back to Driver()")
                drv = Driver()

            # attach to current thread for introspection (optional)
            current = threading.current_thread()
            current.drv = drv
            current.phone = phone

            # expose centrally
            with self.drivers_lock:
                self.drivers[phone] = drv

            # open WhatsApp Web
            try:
                drv.enable_human_mode()
            except Exception:
                # if enable_human_mode not available, ignore
                pass

            drv.google_get("https://web.whatsapp.com/")
            sleep(random.uniform(4, 8))

            # set window title for clarity
            try:
                drv.run_js(f'document.title = "📞 {phone}";')
            except Exception:
                pass

            print(f"[{phone}] ✅ WhatsApp browser ready. (Thread: {current.name})")

            # signal readiness if we've collected at least one driver
            # (caller uses other mechanisms to decide when to start sending)
            self.all_drivers_ready.set()

            # keep thread alive until stop_event set
            while not self.stop_event.is_set():
                sleep(1)

            # when stop_event set, close driver cleanly if possible
            try:
                drv.close()
            except Exception:
                pass

        except Exception as e:
            print(f"[{phone}] exception in driver thread: {e}")

    def open_browser_only(self, numbers_open: List[str]):
        """
        Create a Thread + Driver for each phone in numbers_open.
        This guarantees multiple independent browser windows.
        """
        # prepare data items
        data_items = [make_data_item(p) for p in numbers_open]

        # start one thread per data item
        for item in data_items:
            t = threading.Thread(target=self._start_driver_for, args=(item,), daemon=True)
            t.start()
            self.browsers_threads.append(t)

        # set flag
        self.browsers_opened = True
        print(f"Started {len(self.browsers_threads)} browser thread(s). Log in to each if needed.")
        # Note: do NOT join here — we want threads to keep running and allow start_sending()

    def _collect_drivers(self, timeout: float = 30.0) -> Dict[str, Driver]:
        """
        Wait up to `timeout` seconds for threads to attach drivers,
        return the mapping phone -> driver (best-effort).
        """
        end = time() + timeout
        while time() < end:
            with self.drivers_lock:
                if len(self.drivers) >= 1:
                    # if we've got at least one driver, return what's available (best-effort)
                    return dict(self.drivers)
            sleep(0.5)
        # final return whatever we have
        with self.drivers_lock:
            return dict(self.drivers)

    def logic_to_send(self, driver: Driver, assigned_number: str, receiver: str, message: str):
        """
        Low-level sending actions. Assumes helper_functions.write_message and selectors exist.
        """
        try:
            search_box = driver.get_element_containing_text(
                "Search or start a new chat", wait=Wait.VERY_LONG
            )
            search_box.click()
            write_message(driver, assigned_number, is_message=False)
            sleep(random.uniform(1, 2.5))

            first_chat = driver.is_element_present(selector=self.json_data["first_chat"])
            if first_chat:
                driver.wait_for_element(selector=self.json_data["first_chat"]).click()
            else:
                driver.wait_for_element(selector=self.json_data["clear_button"], wait=Wait.VERY_LONG).click()
                print(f"[{receiver}] ⚠️ Number {assigned_number} not found")

            driver.wait_for_element(selector=self.json_data["type_message_ele"]).click()
            write_message(driver, message, is_message=True)
            sleep(random.uniform(1.5, 3.0))

            try:
                driver.wait_for_element(selector=self.json_data["send_button_1"]).click()
            except Exception:
                driver.wait_for_element(selector=self.json_data["send_button_2"]).click()

            print(f"[{receiver}] ✅ Sent to {assigned_number}")

        except Exception as e:
            print(f">>>> send error {e}")

    def start_sending(
        self,
        senders: List[str],
        recipients: List[str],
        messages: List[str],
        min_delay: float = 1.0,
        max_delay: float = 3.0,
        wait_for_drivers_timeout: float = 30.0,
        background: bool = False,
        on_message_sent=None
    ):
        """
        Round-robin sending using drivers created by open_browser_only.
        - senders: list of phone numbers that must match opened browser phones.
        - recipients: list of targets.
        - messages: list of messages (randomly chosen per send).
        """
        
        
        print(self.browsers_opened)

        if not self.browsers_opened:
            raise RuntimeError("Browsers are not open. Call open_browser_only(...) first.")

        # wait/collect drivers
        drivers = self._collect_drivers(timeout=wait_for_drivers_timeout)
        if not drivers:
            raise RuntimeError("No browser drivers found — make sure browsers opened and attached.")

        # map senders to drivers
        sender_drivers: Dict[str, Driver] = {}
        for s in senders:
            key = str(s)
            if key in drivers:
                sender_drivers[key] = drivers[key]
            else:
                raise ValueError(f"Sender {s} not found among opened browsers: {list(drivers.keys())}")

        n_senders = len(senders)

        def _send_loop():
            print(f"Starting sending: {len(recipients)} recipients, {n_senders} senders.")
            for idx, recipient in enumerate(recipients):
                if self.stop_event.is_set():
                    print("Stop signal received. Aborting sends.")
                    break
                sender_index = idx % n_senders
                sender_phone = str(senders[sender_index])
                driver = sender_drivers[sender_phone]

                message = random.choice(messages)

                try:
                    with self.send_lock:
                        self.logic_to_send(driver, sender_phone, recipient, message)
                        if on_message_sent:
                            on_message_sent(recipient, sender_phone)
                except Exception as e:
                    print(f"Error sending from {sender_phone} to {recipient}: {e}")

                sleep(random.uniform(min_delay, max_delay))

            print("Finished start_sending run.")

        if background:
            t = threading.Thread(target=_send_loop, daemon=True)
            t.start()
            return t
        else:
            _send_loop()

    def stop_sending(self):
        """Signal browser threads to exit and stop any in-progress sending."""
        self.stop_event.set()
        # optionally join threads if you want to wait for them to exit:
        for t in self.browsers_threads:
            if t.is_alive():
                t.join(timeout=1)


if __name__ == "__main__":
    sender = WhatsAppSender()
    senders = ["201103738707"]
    sender.open_browser_only(senders)

    input("بعد تسجيل الدخول في كل نافذة اضغط Enter لبدء الإرسال...")

    recipients = ["201002097448", "201013416458", "201093998000"]
    messages = ["أهلاً 🌟", "رسالة تجريبية", "مرحباً، هذا اختبار"]

    sender.start_sending(senders, recipients, messages, min_delay=1.5, max_delay=3.5, background=True)

    print("العملية شغالة في الخلفية... اضغط Ctrl + C للإيقاف.")

    # 🔴 هـــــــــــــام: منع غلق البرنامج
    while True:
        sleep(1)


whatsapp_app = WhatsAppSender()
