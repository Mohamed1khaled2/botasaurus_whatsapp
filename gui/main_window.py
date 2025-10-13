import customtkinter as ctk
from gui.sender_whatsapp_window import SenderWhatsappWindow

class App(ctk.CTk):
    def __init__(self, *args, **kwargs):
        
        super().__init__(*args, **kwargs)
        self._set_appearance_mode('System')

        
        self.available_tabs = []
        self.windows = {}
        
        self.geometry("400x300")
        self.title("Altmyz Home")
        

        
        self.button_pressed = ctk.CTkButton(
            self,
            text="Open Whatsapp Sender 🚀",
            height=50, 
            fg_color='green', 
            font=('arial', 22, "bold"),
            command=self.open_sender_whatsapp_window)
        
        self.button_pressed.pack(expand='true')  
    

    def open_sender_whatsapp_window(self):
        if not self.available_tabs:
            next_num = max([int(k.replace("tap", "")) for k in self.windows.keys()], default=0) + 1
            self.available_tabs.append(next_num)
        tab_num = self.available_tabs.pop(0)  # خد أول رقم متاح   
        key = f"tap{tab_num}"
        self.windows[key] = SenderWhatsappWindow(self, name=f"Tab{tab_num}")