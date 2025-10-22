import customtkinter as ctk
from gui.view_tree_data import ModernCTkTable
import threading
from whatsapp_automation import whatsapp_app
from tkinter import IntVar, StringVar

class SenderTapWindow(ctk.CTkFrame):
    def __init__(self, master, messages_tab, channels_tab, setting_tab, **kwargs):
        super().__init__(master, **kwargs)

        self.whatsapp_sender = whatsapp_app
        self.messages_tab = messages_tab
        self.channels_tab = channels_tab
        self.settings_tab = setting_tab

        self.selected_numbers = []
        self.messages = []
        self.data_numbers = []
        self.settings = {}

        # 🔗 الربط مع التبويبات
        self.channels_tab.on_selection_changed = self.update_selected_numbers
        self.messages_tab.on_messages_changed = self.update_messages
        self.settings_tab.on_settings_changed = self.settings_changed

        self.columnconfigure((0, 1, 2, 3, 4), weight=1)
        self.rowconfigure((0), weight=1)
        self.rowconfigure((1), weight=2)
        self.rowconfigure((2), weight=1)

        self.numbers_sendit = IntVar()
        self.numbers_nophone = IntVar()
        self.count_numbers_sendit_var = StringVar(value="Sent: 0")
        self.count_numbers_nophone_var = StringVar(value="No Phone: 0")

        self.count_numbers_sent_it = ctk.CTkLabel(
            self,
            textvariable=self.count_numbers_sendit_var,
            font=("arial", 20, "bold"),
            bg_color="green",
            corner_radius=5,
        )
        self.count_numbers_sent_it.grid(row=0, column=0, columnspan=3)
        self.count_numbers_no_phone = ctk.CTkLabel(
            self,
            textvariable=self.count_numbers_nophone_var,
            font=("arial", 20, "bold"),
            bg_color="gray",
            corner_radius=5,
        )
        self.count_numbers_no_phone.grid(row=0, column=2, columnspan=2)

        header = ["Send To", "Send From"]
        self.view_tree_results = ModernCTkTable(
            self, headers=header, data=self.data_numbers, checked_column=False
        )
        self.view_tree_results.grid(row=1, column=0, columnspan=5, sticky="nsew")

        # 🧭 الأزرار
        self.run_btn = ctk.CTkButton(
            self, text="Run Sending 🚀", command=self.start_sending,
            fg_color="green", font=("arial", 12, "bold")
        )
        self.run_btn.grid(row=2, column=0)

        self.stop_btn = ctk.CTkButton(
            self, text="Stop Sending ⛔", command=self.stopping_sending,
            font=("arial", 12, "bold")
        )
        self.stop_btn.grid(row=2, column=1)

        self.resume_btn = ctk.CTkButton(
            self, text="Resume Sending", command=self.resume_fun,
            font=("arial", 12, "bold")
        )
        self.resume_btn.grid(row=2, column=2)

        self.import_numbers_btn = ctk.CTkButton(
            self, text="Import Numbers", command=self.import_numbers_fun,
            font=("arial", 12, "bold")
        )
        self.import_numbers_btn.grid(row=2, column=3)

        self.clear_numbers = ctk.CTkButton(
            self, text="Clear Numbers", command=self.clear_numbers_fun,
            font=("arial", 12, "bold")
        )
        self.clear_numbers.grid(row=2, column=4)

        # 🧠 تحميل الإعدادات الحالية
        self.settings = self.settings_tab.settings

        # 📋 Label لعرض الإعدادات الحالية
        self.settings_label = ctk.CTkLabel(
            self, text=f"Settings: {self.settings.get('ways_to_send', {})}",
            font=("arial", 14)
        )
        self.settings_label.grid(row=3, column=0, columnspan=5, pady=5)

    def settings_changed(self, settings: dict):
        self.settings = settings
        self.settings_label.configure(text=f"Settings: {self.settings.get('ways_to_send', {})}")
        print("⚙️ Settings Updated in SenderTapWindow:", settings)

    def _increase(self, stringvar, intvar, text: str):
        intvar.set(intvar.get() + 1)
        stringvar.set(f"{text}: {intvar.get()}")

    def resume_fun(self):
        self.whatsapp_sender.resume_sending()

    def update_selected_numbers(self, numbers):
        self.selected_numbers = numbers
        print("📱 Selected Numbers Updated:", numbers)

    def update_messages(self, messages):
        self.messages = messages
        print("💬 Messages Updated:", messages)

    def start_sending(self):
        if not self.selected_numbers or not self.messages or not self.data_numbers:
            print("⚠️ تأكد من اختيار القنوات والأرقام والرسائل أولًا.")
            return

        print("🧩 Settings before sending:", self.settings)

        threading.Thread(
            target=self.whatsapp_sender.start_sending,
            args=(
                self.selected_numbers,
                self.data_numbers,
                self.messages,
                self.settings,
                1.5,
                3.5,
                True,
            ),
            kwargs={"on_message_sent": self.update_gui},
            daemon=True,
        ).start()

    def update_gui(self, number, channel):
        if channel is None:
            self._increase(self.count_numbers_nophone_var, self.numbers_nophone, "No Phone")
        else:
            self._increase(self.count_numbers_sendit_var, self.numbers_sendit, "Sent: ")

        self.after(2, lambda: self._safe_gui_update(number, channel))

    def _safe_gui_update(self, number, channel):
        row_index = self.view_tree_results.get_row_index_by_value(number)
        if row_index >= 0:
            self.view_tree_results.update_cell_value(row_index, 1, channel)

    def stopping_sending(self):
        print("⛔ Stopping sending...")
        try:
            self.whatsapp_sender.stop_sending()
        except Exception as e:
            print(f"⚠️ خطأ أثناء محاولة الإيقاف: {e}")

    def clear_numbers_fun(self):
        self.data_numbers.clear()
        self.view_tree_results.clear()
        print("🧹 Numbers cleared.")

    def import_numbers_fun(self):
        filepath = ctk.filedialog.askopenfilename()
        if not filepath:
            return
        try:
            new_rows = []
            with open(filepath, "r", encoding="utf-8") as f:
                for line in f:
                    n = line.strip()
                    if n:
                        row = [n]
                        self.data_numbers.append(row)
                        new_rows.append(row)
            if new_rows:
                self.view_tree_results.add_data(new_rows)
                print(f"✅ Imported {len(new_rows)} numbers.")
        except Exception as e:
            print(f"⚠️ خطأ أثناء قراءة الملف: {e}")
