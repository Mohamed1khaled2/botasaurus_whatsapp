from helper_functions import *
from botasaurus.browser import browser, Driver, Wait
from time import sleep
import random
import threading

start_event = threading.Event()      # Used to wait for user input once

# Used to prevent multiple browsers from acting at the same time
exclusive_lock = threading.Lock()


json_data = read_json()

@browser(profile=get_profile)
def open_whatsapp(driver: Driver, data):
    
    # variables
    numbers = get_numbers()
    messages = get_message()
    index = 0
    print(numbers)
    print(messages)
    driver.enable_human_mode()
    sleep(random.uniform(1.0, 5.0))
    driver.google_get("https://web.whatsapp.com/")
    sleep(random.uniform(1, 10))
    driver.run_js(f'document.title = "📞 {data["phone_number"]}";')

    print(f"Waiting to start: {data['phone_number']}")
    start_event.wait()  # Wait for user confirmation

    # Lock this section so only one browser at a time enters
    with exclusive_lock:
        print(f"🔓 {data['phone_number']} is now active.")

        # Safe zone: only one browser at a time can be here
        while True:
            
            print(f"{data['phone_number']} is idle...")

            
            element = driver.get_element_containing_text(
                "(You)", wait=Wait.VERY_LONG)
            if element:
                element.click()
            else:
                print(
                    f"❌ Error: Could not find the contact for {data['phone_number']}")
            
            driver.wait_for_element(selector=json_data['input_filed']).click()

            write_message(driver=driver, message=f"https://web.whatsapp.com/send?phone={numbers[0][index]}")

            sleep(random.uniform(1, 3))

                
            driver.wait_for_element(selector=json_data['send_button']).click()

            sleep(random.uniform(1, 3))

            driver.get_all_elements_containing_text(text="web.whatsapp.com")[-1].click()

            sleep(random.uniform(1, 3))

            # TODO check if number using whatsapp or not
            is_not_using_whatsapp = driver.is_element_present(json_data["ok_no_phone"])
            if is_not_using_whatsapp :
                index+=1
                continue
            
            print(is_not_using_whatsapp)
            print(''.join(messages[0]))
                
                
            driver.click_element_containing_text("Type a message")
                
            write_message(driver=driver, message=messages[0])
                
            # send button
            driver.wait_for_element(selector=json_data['send_button']).click()
            
            # to get another number
            index+=1
            
            moving_for_duration(random.uniform(30.0, 60.0))
         

            # checks to break
            if index == len(numbers[0]):
                break



phone_list = [
    # {"phone_number": "201289422813", "profile": "201289422813"},
    {"phone_number": "201552694323", "profile": "201552694323"},
]

# Start the threads (browsers)
thread = threading.Thread(target=lambda: open_whatsapp(
    phone_list, parallel=len(phone_list)))
thread.start()

# Wait for user confirmation once
input("Start all browsers? (press Enter)\n")
start_event.set()


"""
    TODO: after send message make random move on whatsapp and return send to another person
"""