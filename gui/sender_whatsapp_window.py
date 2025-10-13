import ctypes
from gui.tab_view import MyTabView
import customtkinter as ctk



class SenderWhatsappWindow(ctk.CTkToplevel):
    def __init__(self, parent, *args, **kwargs):
        self.name = kwargs.pop("name", "بدون اسم")  
        super().__init__(parent, *args, **kwargs)

        self.parent = parent  # نخزن المرجع للـ App

        self.geometry("800x600")
        self.title(f"🚀 Sender Whatsapp {self.name}")
        
        # ✅ خليها تظهر مستقلة في شريط المهام
        hwnd = ctypes.windll.user32.GetParent(self.winfo_id())
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(f"altmyz.{self.name}.window")
        ctypes.windll.user32.SetWindowLongW(hwnd, -8, 0)
        
        self.attributes('-topmost', True)
        self.focus_force()
        self.lift()
        
        self.after(200, lambda: self.attributes('-topmost', False))
              
        self.tab_view = MyTabView(master=self)
        self.tab_view.pack(fill="both", expand=True, padx=20, pady=20)
        
        # هنا بنحدد إيه اللي يحصل لما النافذة تتقفل
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        


    def on_close(self):
        """امسح النافذة من قاموس parent بعد ما تتقفل"""
        for key, win in list(self.parent.windows.items()):
            if win == self:
                del self.parent.windows[key]
                # رجّع الرقم للـ available_tabs علشان ممكن نستخدمه تاني
                num = int(key.replace("tap", ""))
                self.parent.available_tabs.append(num)
                self.parent.available_tabs.sort()
        self.destroy()
