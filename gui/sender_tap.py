import customtkinter as ctk
from gui.view_tree_data import ModernCTkTable
import threading
import whatsapp_automation

class SenderTapWindow(ctk.CTkFrame):
    def __init__(self, master, messages_tab, channels_tab, **kwargs):
        super().__init__(master, **kwargs)
        
        self.messages_tab = messages_tab
        self.channels_tab = channels_tab

        # ✅ بيانات حية
        self.selected_numbers = []
        self.messages = []

        # ✅ ربط إشعارات التغيير
        self.channels_tab.on_selection_changed = self.update_selected_numbers
        self.messages_tab.on_messages_changed = self.update_messages

        self.columnconfigure((0, 1, 2, 3), weight=1)
        self.rowconfigure((0), weight=1)
        self.rowconfigure((1), weight=2)
        self.rowconfigure((2), weight=1)
        
        self.count_numbers_sent_it = ctk.CTkLabel(self, text="Sent: ", bg_color='green', corner_radius=20, font=('arial', 20, 'bold'))
        self.count_numbers_sent_it.grid(row=0, column=0 , columnspan=2)
        self.count_numbers_no_phone = ctk.CTkLabel(self, text="No Phone: ", bg_color='gray', corner_radius=20, font=('arial', 20, 'bold'))
        self.count_numbers_no_phone.grid(row=0, column=2 , columnspan=2)

        header = ["Send To", "Send From"]
        self.data_numbers = []
        self.view_tree_results = ModernCTkTable(self, headers=header, data=self.data, checked_column=False)
        self.view_tree_results.grid(row=1, column=0, columnspan=4, sticky='nsew')
        
        self.run_btn = ctk.CTkButton(self, text="Run Sending 🚀", command=self.start_sending, fg_color='green', font=('arial', 12, 'bold'))
        self.run_btn.grid(row=2, column=0)
        self.stop_btn = ctk.CTkButton(self, text="Stop Sending ⛔", command=self.stopping_sending, font=('arial', 12, 'bold'))
        self.stop_btn.grid(row=2, column=1)
        self.import_numbers_btn = ctk.CTkButton(self, text="Import Numbers", command=self.import_numbers_fun, font=('arial', 12, 'bold'))
        self.import_numbers_btn.grid(row=2, column=2)
        self.clear_numbers = ctk.CTkButton(self, text="Clear Numbers", command=self.clear_numers_fun, font=('arial', 12, 'bold'))
        self.clear_numbers.grid(row=2, column=3)

    # 🔄 تحديث البيانات تلقائيًا
    def update_selected_numbers(self, numbers):
        self.selected_numbers = numbers
        print("📱 Selected Numbers Updated:", numbers)

    def update_messages(self, messages):
        self.messages = messages
        print("💬 Messages Updated:", messages)

    # 🚀 بدء الإرسال
    def start_sending(self):
        if not self.selected_numbers or not self.messages or not self.data_numbers:
            print("⚠️ تأكد من اختيار أرقام، رسائل، وقنوات الإرسال قبل الإرسال.")
            return

        # 🔹 تعريف callback لتحديث الجدول
        def update_gui(number, channel):
            row_index = self.view_tree_results.get_row_index_by_value(number)
            if row_index >= 0:
                self.view_tree_results.update_cell_value(row_index, 1, channel)  # عمود Send From

        import whatsapp_automation
        threading.Thread(
            target=whatsapp_automation.run,
            args=(self.selected_numbers, self.messages, self.data_numbers, False, update_gui),
            daemon=True
        ).start()
    def stopping_sending(self):
        print("⛔ Stopping sending...")

    def clear_numers_fun(self):
        self.data_numbers.clear()
        self.view_tree_results.clear()

    def import_numbers_fun(self):
        file_num = ctk.filedialog.askopenfile()
        for num in file_num:
            self.data_numbers.append([num.replace('\n', '')])
        
        self.view_tree_results.add_data(self.data)
        
