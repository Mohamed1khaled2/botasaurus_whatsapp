import multiprocessing
import threading
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

# NOTE: For Windows (spawn) we must create Event/Lock in the parent process
# and pass them into child processes. Module-level objects won't be shared
# across processes started with 'spawn'. Keep globals as fallback for
# backwards compatibility, but prefer the ones passed from `run()`.
start_event = multiprocessing.Event()
send_lock = multiprocessing.Lock()
# Hold references to the most-recent parent synchronization primitives so the
# main process can signal children later (e.g., to stop sending).
current_parent_event = None
current_parent_lock = None
current_parent_stop = None
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
def open_whatsapp_browser(driver: Driver, data, start_sending=True, update_queue=None, start_event=None, send_lock=None, stop_event=None, manager_namespace=None, control_queue=None):
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
            # When opened in "open only" mode we still want the process to
            # stay alive and respond to a GUI start signal later. Instead of
            # returning immediately, wait for the start_event (or a stop
            # signal). If no event was provided (edge case), just keep the
            # browser open until it's closed.
            print(Fore.GREEN + f"[{sender_phone}] 🟢 Browser opened only (waiting for GUI start)...")
            # Use the same event resolution as below
            evt = start_event if start_event is not None else globals().get('start_event')
            stop_evt = stop_event if stop_event is not None else globals().get('current_parent_stop')

            # Wait for start or stop while browser remains open
            while is_browser_open(driver):
                if stop_evt and stop_evt.is_set():
                    print(Fore.MAGENTA + f"[{sender_phone}] ⛔ Stop signal received while waiting (open-only). Exiting.")
                    return
                if evt is None:
                    # no event provided: just keep browser open
                    sleep(2)
                    continue
                if evt.wait(timeout=1):
                    # start was signaled; fall through to sending logic
                    break
            # If browser was closed while waiting, exit
            if not is_browser_open(driver):
                return
        # Use passed-in start_event / send_lock / stop_event when provided
        # (these are created in the parent and passed via kwargs). Otherwise
        # fall back to module-level globals (backwards compatibility).
        evt = start_event if start_event is not None else globals().get('start_event')
        lck = send_lock if send_lock is not None else globals().get('send_lock')
        stop_evt = stop_event if stop_event is not None else globals().get('current_parent_stop')

        print(Fore.YELLOW + f"[{sender_phone}] Waiting for start signal... (evt={evt}, stop_evt={stop_evt})")
        # Wait in a loop so we can respond to a stop signal while waiting.
        while True:
            if stop_evt and stop_evt.is_set():
                print(Fore.MAGENTA + f"[{sender_phone}] ⛔ Stop signal received before start. Exiting.")
                return
            if evt is None:
                # if no event was provided, proceed immediately
                print(Fore.YELLOW + f"[{sender_phone}] No start_event provided; proceeding immediately.")
                break
            # check control queue (parent -> children) for a direct START command
            if control_queue is not None:
                try:
                    msg = control_queue.get_nowait()
                    if msg == 'START':
                        print(Fore.GREEN + f"[{sender_phone}] control_queue START received; proceeding to send.")
                        break
                except Exception:
                    # no message available
                    pass
            # also check manager namespace fallback
            try:
                ns = manager_namespace if manager_namespace is not None else globals().get('current_parent_namespace')
                ns_started = getattr(ns, 'started', None) if ns is not None else None
            except Exception:
                ns_started = None
            # if a namespace flag is set, accept it as a start signal
            if ns_started:
                print(Fore.GREEN + f"[{sender_phone}] manager namespace started flag detected; proceeding to send.")
                break
            try:
                is_set = evt.is_set()
            except Exception:
                is_set = 'unknown'
            try:
                evt_id = id(evt)
            except Exception:
                evt_id = 'unknown'
            print(Fore.BLUE + f"[{sender_phone}] start_event.is_set() = {is_set} (evt_id={evt_id})")
            if evt.wait(timeout=1):
                print(Fore.GREEN + f"[{sender_phone}] start_event.wait() returned True; proceeding to send.")
                break

        # Start sending loop
        run_sender_logic(driver, sender_phone, numbers, messages, update_queue, lock=lck, stop_event=stop_evt)

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
def run_sender_logic(driver: Driver, sender_phone, numbers, messages, update_queue=None, lock=None, stop_event=None):
    numbers_to_send = numbers.copy()
    random.shuffle(numbers_to_send)
    try:
        print(Fore.BLUE + f"[{sender_phone}] run_sender_logic starting: {len(numbers_to_send)} numbers queued, update_queue={bool(update_queue)}")
    except Exception:
        pass
    for assigned_number in numbers_to_send:
        if stop_event and stop_event.is_set():
            print(Fore.MAGENTA + f"[{sender_phone}] ⛔ Stop signal received — stopping sender.")
            break

        if not is_browser_open(driver):
            print(Fore.RED + f"[{sender_phone}] ❌ Browser closed — stopping sender.")
            break

        msg_to_send = random.choice(messages)

        try:
            # use the provided lock (from parent) when available to synchronize
            # actions between processes; otherwise use module-level send_lock.
            use_lock = lock if lock is not None else globals().get('send_lock')
            if use_lock:
                use_ctx = use_lock
            else:
                use_ctx = None

            if use_ctx:
                use_ctx.acquire()
            try:
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

                # 🔹 إرسال تحديث إلى الـ parent عبر الـ queue (إن وُجد)
                if update_queue:
                    try:
                        update_queue.put((assigned_number, sender_phone))
                    except Exception:
                        pass

            finally:
                if use_ctx:
                    use_ctx.release()

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
def run(channels_numbers, messages, sender_numbers, open_only=False, update_gui_callback=None, on_ready=None):
    processes = []

    # Use a multiprocessing.Manager to create proxy events that are
    # visible to child processes launched with the 'spawn' start method
    # (Windows). Keeping the manager reference alive guarantees the
    # proxy objects remain valid for the lifetime of the run.
    manager = multiprocessing.Manager()
    parent_event = manager.Event()
    try:
        parent_lock = manager.Lock()
    except Exception:
        # If manager.Lock isn't available for some manager implementations,
        # fall back to a plain multiprocessing.Lock (still works, but
        # might not be a proxy).
        parent_lock = multiprocessing.Lock()
    parent_stop = manager.Event()
    # namespace fallback for a simple boolean flag accessible from children
    try:
        parent_ns = manager.Namespace()
        parent_ns.started = False
    except Exception:
        parent_ns = None

    # prepare an IPC queue for GUI updates (child -> parent)
    parent_queue = multiprocessing.Queue()
    # control queue for parent -> children commands (reliable start signal)
    parent_control_queue = multiprocessing.Queue()

    # store references so other functions (e.g., stop_sending) can access
    # and signal these primitives
    global current_parent_event, current_parent_lock, current_parent_stop, current_parent_manager
    current_parent_event = parent_event
    current_parent_lock = parent_lock
    current_parent_stop = parent_stop
    # keep manager reference for lifetime of this run
    try:
        current_parent_manager = manager
    except Exception:
        current_parent_manager = None
    # store namespace reference as well
    global current_parent_namespace
    current_parent_namespace = parent_ns
    # placeholder for control queue (filled later)
    global current_parent_control_queue
    current_parent_control_queue = None
    print(Fore.BLUE + "[whatsapp_automation] parent_event created and stored on module (current_parent_event)")
    try:
        print(Fore.BLUE + f"[whatsapp_automation] parent_event info -> is_set={parent_event.is_set()}, id={id(parent_event)}")
    except Exception:
        pass

    # Notify caller (in parent process) that the parent_event is ready.
    # Caller can use this callback to set the event immediately (useful when
    # the user pressed Run in the GUI and expects sending to start as soon
    # as browsers are launched).
    if on_ready is not None:
        try:
            on_ready(parent_event)
        except Exception:
            pass

    # expose control queue globally so GUI can send commands
    try:
        current_parent_control_queue = parent_control_queue
    except Exception:
        current_parent_control_queue = None

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
            args=(data, not open_only),
            kwargs={
                'update_queue': parent_queue,
                'start_event': parent_event,
                'send_lock': parent_lock,
                'stop_event': parent_stop,
                'manager_namespace': parent_ns,
                    'control_queue': parent_control_queue,
            }
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
    # Do not block on console input here. The GUI is responsible for
    # starting sending by setting the `current_parent_event` (this file
    # stores it as `current_parent_event`). If someone wants console
    # control they can call `parent_event.set()` themselves.
    if not open_only:
        print(Fore.YELLOW + "👉 Waiting for start signal from GUI or parent_event.set()...\n")

    # If caller provided a GUI callback, start a listener thread to handle
    # queue updates in the parent process so we don't pass callables to children
    if update_gui_callback:
        def _queue_listener(q, cb, stop_evt):
            try:
                while True:
                    try:
                        item = q.get(timeout=1)
                    except Exception:
                        if stop_evt and stop_evt.is_set():
                            break
                        continue
                    if item is None:
                        break
                    try:
                        number, channel = item
                        cb(number, channel)
                    except Exception:
                        pass
            except Exception:
                pass

        listener = threading.Thread(target=_queue_listener, args=(parent_queue, update_gui_callback, parent_stop), daemon=True)
        listener.start()

    for p in processes:
        p.join()

    # notify listener to exit
    try:
        parent_queue.put(None)
    except Exception:
        pass

    print(Fore.GREEN + "\n🎯 All processes finished.")


def open_profiles(channels_numbers, messages, sender_numbers, update_gui_callback=None):
    """Wrapper to open browsers for profiles only (no sending)."""
    run(channels_numbers, messages, sender_numbers, open_only=True, update_gui_callback=update_gui_callback)


def stop_sending():
    """Signal the running processes to stop sending and close their browsers.

    This sets the last-created parent stop event and also sets the start
    event so any processes waiting to start will awaken and see the stop
    flag.
    """
    global current_parent_event, current_parent_stop
    if current_parent_stop is not None:
        try:
            current_parent_stop.set()
            print(Fore.MAGENTA + "⛔ Stop signal sent to worker processes.")
        except Exception as e:
            print(Fore.RED + f"⚠️ Failed to set stop event: {e}")
    else:
        print(Fore.YELLOW + "⚠️ No active stop event found (no run in progress?).")

    # also set the start event to wake any waiters
    if current_parent_event is not None:
        try:
            current_parent_event.set()
        except Exception:
            pass


if __name__ == "__main__":
    pass