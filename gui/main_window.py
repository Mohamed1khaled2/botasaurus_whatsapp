import customtkinter as ctk
from gui.sender_whatsapp_window import SenderWhatsappWindow
from gui.convert_tocsv_window import ConvertorGUI


class App(ctk.CTk):
    def __init__(self, *args, **kwargs):
        
        super().__init__(*args, **kwargs)
        self._set_appearance_mode('System')

        
        self.available_tabs = []
        self.windows = {}
        
        self.geometry("400x300")
        self.title("Altmyz Home")
        

        
        self.whatsapp_sender = ctk.CTkButton(
            self,
            text="Open Whatsapp Sender 🚀",
            height=50, 
            fg_color='green', 
            font=('arial', 22, "bold"),
            command=self.open_sender_whatsapp_window)
        
        self.whatsapp_sender.pack(expand='true')  

        self.convert_txt_tocsv = ctk.CTkButton(
            self, text="Open to Convert Text To CSV",    
            height=50, 
            fg_color='green', 
            font=('arial', 22, "bold"),command=self.open_convertor
        )
        
        self.convert_txt_tocsv.pack(expand= 'true')

    def open_sender_whatsapp_window(self):
        if not self.available_tabs:
            next_num = max([int(k.replace("tap", "")) for k in self.windows.keys()], default=0) + 1
            self.available_tabs.append(next_num)
        tab_num = self.available_tabs.pop(0)  # خد أول رقم متاح   
        key = f"tap{tab_num}"
        self.windows[key] = SenderWhatsappWindow(self, name=f"Tab{tab_num}")
        
    
    def _icon_path(self):
        import sys, os
        icon_path = ''
        if hasattr(sys, "_MEIPASS"):
            print(sys._MEIPASS)
            icon_path = os.path.join(sys._MEIPASS, "logo.ico")
        else:
            icon_path = r"E:\devlopment\office\botasaurus_whatsapp\gui\assets\logo.ico"
        return icon_path
    
    
    def open_convertor(self):
        ConvertorGUI(self, icon_path=self._icon_path())
        
    