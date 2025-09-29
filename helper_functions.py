from botasaurus.browser import Driver
import os
import json
import time
import pyautogui
import random   



def get_numbers(folder_path) -> list[str]:
    all_numbers = []

    folder = os.listdir(folder_path)

    for txt_file in folder:
        if "numbers" in txt_file:
            with open(os.path.join(folder_path, txt_file), "r") as num_file:
                lines = num_file.readlines()
                cleaned = [line.strip() for line in lines if line.strip()]
                all_numbers.extend(cleaned)

    return all_numbers



def get_message(folder_path) -> list[str]:
    
    messages = []
    text_messages = []

    
    foler = os.listdir(folder_path)
    
    
    for txt_file in foler:
        if txt_file.find("message") != -1:
            messages.append(txt_file)
     
    for message in messages:
        with open(folder_path+"/"+message, "r", encoding="utf-8") as msg:
            msg_ = msg.read()
            if len(msg_) != 0:
                text_messages.append(msg_)
    
    return text_messages




def write_message(driver: Driver, message: str, is_message:bool):
    driver.run_js(f'''
        const input = document.querySelector('div[contenteditable="true"][role="textbox"][data-tab="{'10' if is_message else '3'}"]');
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


# def main():
    
#     print(len(get_message()))
#     # try:
#     #     print(len(message))
#     #     message = get_message()
#     #     number = get_numbers()
#     #     if len(message) == 0 or len(number) == 0:
#     #         raise Exception("ERROR: message or number is not found \n hint: Must the file of message name is message and number file name is number")
#     # # COMMit that becuse nake the random messages to sent
#     # #     if len(number) != len(message):
#     # #         raise Exception("ERROR: count of files numbers and messages not equal \n hint: Must the file of message name is message and number file name is number")
    
#     # except TypeError:
#     #     sys.exit("You need to create file numbers.txt and file message.txt")
#     # except Exception as e:
#     #     sys.exit(e)
    

# main()
