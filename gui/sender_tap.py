import customtkinter as ctk
from gui.view_tree_data import ModernCTkTable
import threading
import whatsapp_automation
import time

class SenderTapWindow(ctk.CTkFrame):
    def __init__(self, master, messages_tab, channels_tab, **kwargs):
        super().__init__(master, **kwargs)
        
        self.messages_tab = messages_tab
        self.channels_tab = channels_tab

        self.selected_numbers = []
        self.messages = []
        self.data_numbers = []

        self.channels_tab.on_selection_changed = self.update_selected_numbers
        self.messages_tab.on_messages_changed = self.update_messages

        self.columnconfigure((0, 1, 2, 3), weight=1)
        self.rowconfigure((0), weight=1)
        self.rowconfigure((1), weight=2)
        self.rowconfigure((2), weight=1)
        
        self.count_numbers_sent_it = ctk.CTkLabel(self, text="Sent: ", font=('arial', 20, 'bold'))
        self.count_numbers_sent_it.grid(row=0, column=0 , columnspan=2)
        self.count_numbers_no_phone = ctk.CTkLabel(self, text="No Phone: ", font=('arial', 20, 'bold'))
        self.count_numbers_no_phone.grid(row=0, column=2 , columnspan=2)

        header = ["Send To", "Send From"]
        self.view_tree_results = ModernCTkTable(self, headers=header, data=self.data_numbers, checked_column=False)
        self.view_tree_results.grid(row=1, column=0, columnspan=4, sticky='nsew')
        
        self.run_btn = ctk.CTkButton(self, text="Run Sending 🚀", command=self.start_sending, fg_color='green', font=('arial', 12, 'bold'))
        self.run_btn.grid(row=2, column=0)
        self.stop_btn = ctk.CTkButton(self, text="Stop Sending ⛔", command=self.stopping_sending, font=('arial', 12, 'bold'))
        self.stop_btn.grid(row=2, column=1)
        self.import_numbers_btn = ctk.CTkButton(self, text="Import Numbers", command=self.import_numbers_fun, font=('arial', 12, 'bold'))
        self.import_numbers_btn.grid(row=2, column=2)
        self.clear_numbers = ctk.CTkButton(self, text="Clear Numbers", command=self.clear_numers_fun, font=('arial', 12, 'bold'))
        self.clear_numbers.grid(row=2, column=3)

    def update_selected_numbers(self, numbers):
        self.selected_numbers = numbers
        print("📱 Selected Numbers Updated:", numbers)

    def update_messages(self, messages):
        self.messages = messages
        print("💬 Messages Updated:", messages)
        

       # 🚀 بدء الإرسال
    def start_sending(self):
        if not self.selected_numbers or not self.messages or not self.data_numbers:
            print("⚠️ تأكد من اختيار القنوات والأرقام والرسائل أولًا.")
            return

        senders = [{"phone_number": num, "profile": num} for num in self.selected_numbers]
        receivers = [row[0] for row in self.data_numbers]
        messages = self.messages

        print(f"🚀 Starting sending...\nSenders: {len(senders)}\nReceivers: {len(receivers)}\nMessages: {len(messages)}")

    # شغل الإرسال في Thread علشان الـ UI ما يعلقش
        threading.Thread(target=whatsapp_automation.start_sending, args=(senders, receivers, messages), daemon=True).start()

    def stopping_sending(self):
        print("⛔ Stopping sending...")
        try:
            whatsapp_automation.stop_sending()
        except Exception as e:
            print(f"⚠️ خطأ أثناء محاولة إيقاف الإرسال: {e}")

    def clear_numers_fun(self):
        self.data_numbers.clear()
        self.view_tree_results.clear()
        print("🧹 Numbers cleared from table.")

    def import_numbers_fun(self):
        filepath = ctk.filedialog.askopenfilename()
        if not filepath:
            return
        new_rows = []
        try:
            with open(filepath, mode='r', encoding='utf-8') as file_obj:
                for line in file_obj:
                    n = line.strip()
                    if n:
                        row = [n]
                        self.data_numbers.append(row)
                        new_rows.append(row)
            if new_rows:
                self.view_tree_results.add_data(new_rows)
                print(f"✅ Imported {len(new_rows)} numbers successfully.")
        except Exception as e:
            print(f"⚠️ خطأ أثناء قراءة الملف: {e}")
