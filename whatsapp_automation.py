"""
# TODO 
    // check whatsapp ban or not 

"""




from helper_functions import *
from botasaurus.browser import browser, Driver, Wait
from time import sleep
import random
import threading

start_event = threading.Event()      # Used to wait for user input once

# Shared synchronization primitives for strict round-robin
turn_cv = threading.Condition()      # used to coordinate turns
shared_index = 0                      # next index in the numbers list to assign
turn = 0                              # whose turn (thread index) it is now

json_data = read_json()

@browser(profile=get_profile)
def open_whatsapp(driver: Driver, data):
    """
    Note: `data` must include a field 'thread_index' indicating this thread's position
    in phone_list (0-based).
    """
    global shared_index, turn

    # variables
    numbers = get_numbers()   # expected shape: list of lists => numbers[0] is the list
    messages = get_message()
    my_idx = int(data.get("thread_index", 0))   # this thread's slot in the round-robin
    num_threads = int(data.get("num_threads", 1))

    driver.enable_human_mode()

    sleep(random.uniform(1.0, 3.0))  
    driver.google_get("https://web.whatsapp.com/")
    
    sleep(random.uniform(5, 10))
    driver.run_js(f'document.title = "📞 {data["phone_number"]}";')
    print(f"Thread {my_idx}: Waiting to start for {data['phone_number']}")
    start_event.wait()  # Wait for user confirmation
    numbers = get_numbers()
    
    driver.run_js(f'document.title = "📞 {data["phone_number"]}";')
    while True:
        # Wait for our turn in strict round-robin, and pick a number only when it's our turn.
        with turn_cv:
            # If everything already assigned, exit
            if shared_index >= len(numbers[0]):
                turn_cv.notify_all()
                print(f"Thread {my_idx}: no more numbers at loop start, exiting.")
                return

            while turn != my_idx:
                # check done condition before waiting to avoid deadlock
                if shared_index >= len(numbers[0]):
                    turn_cv.notify_all()
                    print(f"Thread {my_idx}: no more numbers while waiting, exiting.")
                    return
                turn_cv.wait()

            # It's our turn now. Check again then assign
            if shared_index >= len(numbers[0]):
                # nothing to do, advance turn and exit
                turn = (turn + 1) % num_threads
                turn_cv.notify_all()
                print(f"Thread {my_idx}: no numbers at assignment check, exiting.")
                return

            assigned_index = shared_index
            assigned_number = numbers[0][assigned_index].strip()
            shared_index += 1
            print(f"Thread {my_idx}: assigned number index {assigned_index} -> {assigned_number}")

            # ---------- Do the actual sending WHILE HOLDING the turn_cv lock ----------
            # This ensures strict exclusivity: no other thread runs its send until we finish
            try:
                print(f"Thread {my_idx} ({data['phone_number']}): preparing to send to {assigned_number}")

                # Bring focus (try to click "(You)" or continue)
                element = driver.get_element_containing_text("(You)", wait=Wait.VERY_LONG)
                if element:
                    element.click()
                else:
                    print(f"Thread {my_idx}: could not find '(You)' element — continuing anyway")

                driver.wait_for_element(selector=json_data['input_filed']).click()

                # first send the open chat with phone link
                write_message(driver=driver, message=f"https://web.whatsapp.com/send?phone={assigned_number}")

                sleep(random.uniform(1, 3))

                # click send (try both selectors)
                try:
                    driver.wait_for_element(selector=json_data['send_button_1']).click()
                except Exception:
                    driver.wait_for_element(selector=json_data['send_button_2']).click()

                sleep(random.uniform(1, 3))

                # click the web.whatsapp link that opened (last one)
                driver.get_all_elements_containing_text(text="web.whatsapp.com")[-1].click()

                sleep(random.uniform(1, 3))

                # check if number uses whatsapp
                # edit to write another check for non whatsapp
                # is_not_using_whatsapp = ""
                
       
                is_not_using_whatsapp = driver.is_element_present(json_data["ok_no_phone"])

                    
                if is_not_using_whatsapp :
                    print(f"Thread {my_idx}: number {assigned_number} not using WhatsApp — skipping.")
                    # After skipping, we still finish our turn below.
                    # TODO we need to press button ok
                else:
                    # type and send message
                    driver.click_element_containing_text("Type a message", wait=Wait.LONG)
                    # choose a message (randomize if there are multiple)
                    if len(messages) == 0:
                        msg_to_send = ""
                    else:
                        # random choice makes messages less repetitive; change to messages[0] if you prefer
                        try:
                            msg_to_send = messages[random.randint(0, max(0, len(messages)-1))]
                        except Exception:
                            msg_to_send = messages[0]
                    write_message(driver=driver, message=msg_to_send)

                    # send message button
                    try:
                        driver.wait_for_element(selector=json_data['send_button_1']).click()
                    except Exception:
                        driver.wait_for_element(selector=json_data['send_button_2']).click()
                

                    print(f"Thread {my_idx}: sent message to {assigned_number}")

                # mimic human moving while others wait their turn
                moving_for_duration(random.uniform(5.0, 8.0))
            except Exception as e:
                print(f"Thread {my_idx}: exception during sending to {assigned_number}: {e}")
                # we still finish the turn even on exception

            # After finishing sending (or skipping/error), advance turn and notify others
            turn = (turn + 1) % num_threads
            turn_cv.notify_all()
        # end with turn_cv

        # Continue loop; the next iteration will wait for our next turn (or exit if no numbers left)


# Prepare phone list and assign thread_index for each
_raw_phone_list = [
    {"phone_number": "201068105917", "profile": "201068105917"},
    {"phone_number": "201505774702", "profile": "201505774702"},
    {"phone_number": "201289427756", "profile": "201289427756"},
    {"phone_number": "201280578648", "profile": "201280578648"},
    # {"phone_number": "201552694323", "profile": "201552694323"}, # ban 24 hours
#      {"phone_number": "201289427756", "profile": "201289427756"},
#      {"phone_number": "201280578648", "profile": "201280578648"},
]

# attach thread_index and num_threads to each data dict
phone_list = []
for i, p in enumerate(_raw_phone_list):
    p_copy = p.copy()
    p_copy["thread_index"] = i
    p_copy["num_threads"] = len(_raw_phone_list)
    phone_list.append(p_copy)

# Start the threads (browsers)
threads = []

for phone in phone_list:
    t = threading.Thread(target=lambda p=phone: open_whatsapp(p))
    t.start()
    threads.append(t)

# Wait for user confirmation once
input("Start all browsers? (press Enter)\n")
start_event.set()

# Optional: wait for all threads to finish
for t in threads:
    t.join()
