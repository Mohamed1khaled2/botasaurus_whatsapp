import customtkinter as ctk
from PIL import Image
from tkinter import Listbox, ttk, END, StringVar, DoubleVar, PhotoImage
from threading import Thread
import time
from view_tree_data import ModernCTkTable
import ctypes


class MyTabView(ctk.CTkTabview):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # create tabs
        self.channels_tap = self.add("Channels")
        self.sender_tap = self.add("Sender")
        self.messages = self.add("Messages")

        #* chaneels tap
        self.channels_tap.columnconfigure((0,1), weight=1)
        self.channels_tap.rowconfigure(0, weight=1)
        self.channels_tap.rowconfigure(1, weight=3)
        self.channels_tap.rowconfigure(2, weight=1)

        ctk.CTkLabel(self.channels_tap, text="Row 0", fg_color="red")
        
        # self.option_menu = ctk.CTkOptionMenu(self.channels_tap, values=['we', 'vodaphone', 'etitsalt', 'orange'], button_hover_color='green')
        # self.option_menu.grid(row=0, column=0)
        
        headers = ["ID", "Name", "Job"]
        data = [
        ["1", "Ahmed", "Developer"],
        ["2", "Mona", "Designer"],
        ["3", "Khaled", "Manager"],
        ["4", "Sara", "HR"],
        ["5", "Ali", "Tester"]
    ]


        self.table = ModernCTkTable(self.channels_tap, data=data, headers=headers).grid(row=1, column=0,columnspan=2,  sticky="nsew")

        # إنشاء الجدول
        # self.table = TreeviewWithCheckboxes(
        #     self.channels_tap, 
        #     data=data,
        #     img_checked_path=r"D:\Mada\devlopment\botasaurus_whatsapp-main\gui\assets\checked.png",
        #     img_unchecked_path=r"D:\Mada\devlopment\botasaurus_whatsapp-main\gui\assets\unchecked.png"
        # ).grid(row=1, column=0,columnspan=2,  sticky="nsew")
        
        
        
        ctk.CTkLabel(self.channels_tap, text="Row 2", fg_color="blue").grid(row=2, column=0, sticky="nsew")




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


# النافذة الرئيسية
class App(ctk.CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._set_appearance_mode('System')
        self.str_var = StringVar() 
        
        self.available_tabs = []
        self.windows = {}
        
        self.geometry("400x300")
        self.title("Altmyz Home")
        
        
        self.list_box_ = Listbox(self, height = 10, 
                  width = 15, 
                  bg = "grey",
                  activestyle = 'dotbox', 
                  font = "Helvetica",
                  fg = "yellow")

        # self.list_box_.place(x=10, y=20)
        
        
        # * frame
        # self.frame_one = ctk.CTkFrame(self, width=350, height=200, corner_radius=10)
        # self.frame_one.place(x=10, y=20)
        # self.frame_one.pack(padx=20, pady=10, fill='x')
        # self.frame_one.grid(row=0, column=0)
        # self.frame_two = customtkinter.CTkFrame(self, width=350, height=200)  
        # self.frame_two.grid(row=0, column=1, padx=10)
        
        """
        # we have three way to show this widget in the main window
        self.frame_one.place()
        self.frame_one.pack()
        self.frame_one.grid()
        """
        
        # * Text
        # self.hello_label = customtkinter.CTkLabel(self.frame_one, text="Hello World", font=('arial', 32, 'bold'))
        # self.hello_label.pack(pady=20)
        
        # * image
        # img_light = Image.open(r"D:\Mada\devlopment\botasaurus_whatsapp-main\gui\assets\logo_python.png")
        
        # img = customtkinter.CTkImage(light_image=img_light, size=(250, 250))
        # self.hello_label = customtkinter.CTkLabel(self.frame_one, text="", image=img, height=300)
        # self.hello_label.pack(pady=20)
                
        # * switch 
        # self.switch_mode = customtkinter.CTkSwitch(self.frame_one, text='mode', command=self.switch_mode)
        # self.switch_mode.pack(pady=20)
        
        # * button
        # self.go_lable = customtkinter.CTkLabel(self.frame_one, text="ahmed")
        # self.go_lable.pack(pady = 20)
        
        # self.button_pressed = customtkinter.CTkButton(self.frame_one, text="Press Me !", command=self.change_name)
        # self.button_pressed.pack(pady=20)  
        
        
        
        # * entry        
        # ! if using text_variable we don't show placeholder_text
        # self.entry_name = customtkinter.CTkEntry(self.frame_one, textvariable=self.str_var, placeholder_text="Name..")
        # self.entry_name.pack(pady=20)
        
        # self.hello_label = customtkinter.CTkLabel(self.frame_one, text="Hello World", font=('arial', 32, 'bold'))
        # self.hello_label.pack(pady=20)
        
        # self.button_pressed = customtkinter.CTkButton(self.frame_one, text="Press Me !", command=self.change_name)
        # self.button_pressed.pack(pady=20)  
        
        # * check box
        
        # self.check_box = customtkinter.CTkCheckBox(self.frame_one, text="Python")
        # self.check_box.pack(pady=20)
        
        #* progrss bar
        # self.button_pressed = customtkinter.CTkButton(self.frame_one, text="Press Me !", command=self.run_progrss)
        # self.button_pressed.pack(pady=20)  
        
        # self.double_var = DoubleVar(value=0.25)
        
        # self.prog = customtkinter.CTkProgressBar(self.frame_one, variable=self.double_var)
        # self.prog.pack(pady=20)  

        # * option Menu
        # self.button_pressed = ctk.CTkButton(self.frame_one, text="Press Me !", command=self._get_option)
        # self.button_pressed.pack(pady=20)  
        # self.option_menu = ctk.CTkOptionMenu(self.frame_one, values=['we', 'vodaphone', 'etitsalt', 'orange'], button_hover_color='green', command=self.opt_fun)
        # self.option_menu.pack(pady=20)  
        
    

        

        self.button_pressed = ctk.CTkButton(self, text="Open Whatsapp Sender 🚀",height=50, fg_color='green', font=( 'arial', 22, "bold"), command=self.open_sender_whatsapp_window)
        self.button_pressed.pack(expand='true')  
        
        
        
        # ============= جدول البيانات (Excel-like) =============
        
        data = [
            (1, "Ahmed", "Developer"),
            (2, "Mona", "Designer"),
            (3, "Omar", "Tester"),
        ]

        # إنشاء الجدول
        # self.table = TreeviewWithCheckboxes(
        #     self, 
        #     data=data,
        #     img_checked_path=r"D:\Mada\devlopment\botasaurus_whatsapp-main\gui\assets\checked.png",
        #     img_unchecked_path=r"D:\Mada\devlopment\botasaurus_whatsapp-main\gui\assets\unchecked.png"
        # )

        # self.table.pack(fill="both", expand=True, padx=20, pady=20)



        # زرار يطبع الصفوف المتعلمة
        # btn = ctk.CTkButton(self, text="📌 Print Selected", command=self.print_selected)
        # btn.pack(pady=10)




    def opt_fun(self, value):
        print(value)
    
    def _get_option(self):
        print( self.option_menu.get())
    
    def run_prgrss_fun(self):
        temp = self.double_var.get()
        while temp < 1:
            temp += 0.01
            self.double_var.set(temp)
            print(temp)
            time.sleep(0.01)
    
    def run_progrss(self):
        t1 = Thread(target=self.run_prgrss_fun)
        t1.start()
    
    def change_name(self):
        name = self.str_var.get()
        self.hello_label.configure(text = name, bg_color='red')
        self.entry_name.delete(first_index=0,last_index=END)
        
    def open_sender_whatsapp_window(self):
        # لو مفيش أرقام متاحة → ضيف رقم جديد
        if not self.available_tabs:
            next_num = max([int(k.replace("tap", "")) for k in self.windows.keys()], default=0) + 1
            self.available_tabs.append(next_num)

        tab_num = self.available_tabs.pop(0)  # خد أول رقم متاح   
        key = f"tap{tab_num}"
        self.windows[key] = SenderWhatsappWindow(self, name=f"Tab{tab_num}")

    def switch_mode(self):
        print(self._get_appearance_mode())
        if self.switch_mode.get() and self._get_appearance_mode() != 'dark':
            self._set_appearance_mode('dark')
            
        elif self.switch_mode.get() == 0 :  
            self._set_appearance_mode('light')
    
    
    
    def toggle_checkbox(self, event):
        """تغيير حالة الـ checkbox عند الضغط"""
        region = self.tree.identify("region", event.x, event.y)
        if region != "tree":  # لازم يكون الضغط على عمود الصور (#0)
            return

        row_id = self.tree.identify_row(event.y)
        if not row_id:
            return

        # عكس الحالة
        self.checked_state[row_id] = not self.checked_state[row_id]
        new_img = self.img_checked if self.checked_state[row_id] else self.img_unchecked
        self.tree.item(row_id, image=new_img)

    def print_selected(self):
        """طباعة الصفوف المتعلمة"""
        for row_id, state in self.checked_state.items():
            if state:
                print("✔ Selected:", self.tree.item(row_id, "values"))

    
    
app = App()

app._set_appearance_mode('System')
app.mainloop()
