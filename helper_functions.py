from botasaurus.browser import Driver
import os
import sys
import json
import time
import pyautogui
import random   




files = os.listdir(path=os.getcwd())

# search about .txt
txt_files = []
for file in files:

    if file.endswith(".txt"):
        txt_files.append(file)


def get_numbers() -> list[list[str]]:
    numbers = []
    text_numbers = []

    for txt_file in txt_files:
        if txt_file.find("numbers") != -1:
            numbers.append(txt_file)

    for number in numbers:
        with open(number, "r") as num:
            num_ = num.readlines()
            if len(num_) != 0:
                text_numbers.append(num_)
    return text_numbers


def get_message() -> list[str]:
    messages = []
    text_messages = []

    
    
    for txt_file in txt_files:
        if txt_file.find("message") != -1:
            messages.append(txt_file)

    for message in messages:
        with open(message, "r", encoding="utf-8") as msg:
            msg_ = msg.read()
            if len(msg_) != 0:
                text_messages.append(msg_)

    return text_messages


def write_message(driver: Driver, message: str):
    driver.run_js(f'''
        const input = document.querySelector('div[contenteditable="true"][role="textbox"][data-tab="10"]');
        const dataTransfer = new DataTransfer();
        dataTransfer.setData('text', `{message}`);

        const event = new ClipboardEvent('paste', {{
            clipboardData: dataTransfer,
            bubbles: true
        }});

        input.focus();
        input.dispatchEvent(event);
    ''')


def get_profile(data):
    return data["profile"]

def read_json():
    with open("locations.json", 'r') as file:    
        json_data = json.load(file)
        return json_data


def moving_for_duration(duration_seconds):
    start_time = time.time() 
    screenW, screenH = pyautogui.size()
    while time.time() - start_time < duration_seconds:
        x = random.randint(0, screenW-1)
        y = random.randint(0, screenH-1)
        duration = random.uniform(0.2, 1.0)
        pyautogui.moveTo(x, y, duration=duration, _pause=False)
        time.sleep(random.uniform(0.5, 2.0))
        time.sleep(1)  
        
    print("Time finished")


def main():
    try:
        message = get_message()
        number = get_numbers()
        
        if len(message) == 0 or len(number) == 0:
            raise Exception("ERROR: message or number is not found \n hint: Must the file of message name is message and number file name is number")
    # COMMit that becuse nake the random messages to sent
    #     if len(number) != len(message):
    #         raise Exception("ERROR: count of files numbers and messages not equal \n hint: Must the file of message name is message and number file name is number")
    
    except TypeError:
        sys.exit("You need to create file numbers.txt and file message.txt")
    except Exception as e:
        sys.exit(e)
    

main()
