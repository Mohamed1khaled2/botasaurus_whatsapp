import customtkinter as ctk
from gui.view_tree_data import ModernCTkTable
import threading
from whatsapp_automation import whatsapp_app
import time


class SenderTapWindow(ctk.CTkFrame):
    def __init__(self, master, messages_tab, channels_tab, **kwargs):
        super().__init__(master, **kwargs)

        self.whatsapp_sender = whatsapp_app
        self.messages_tab = messages_tab
        self.channels_tab = channels_tab

        self.selected_numbers = []
        self.messages = []
        self.data_numbers = []

        self.channels_tab.on_selection_changed = self.update_selected_numbers
        self.messages_tab.on_messages_changed = self.update_messages

        self.columnconfigure((0, 1, 2, 3, 4), weight=1)
        self.rowconfigure((0), weight=1)
        self.rowconfigure((1), weight=2)
        self.rowconfigure((2), weight=1)

        self.count_numbers_sent_it = ctk.CTkLabel(
            self, text="Sent: ", font=("arial", 20, "bold")
        )
        self.count_numbers_sent_it.grid(row=0, column=0, columnspan=2)
        self.count_numbers_no_phone = ctk.CTkLabel(
            self, text="No Phone: ", font=("arial", 20, "bold")
        )
        self.count_numbers_no_phone.grid(row=0, column=2, columnspan=2)

        header = ["Send To", "Send From"]

        self.view_tree_results = ModernCTkTable(
            self, headers=header, data=self.data_numbers, checked_column=False
        )
        self.view_tree_results.grid(row=1, column=0, columnspan=5, sticky="nsew")

        self.run_btn = ctk.CTkButton(
            self,
            text="Run Sending 🚀",
            command=self.start_sending,
            fg_color="green",
            font=("arial", 12, "bold"),
        )
        self.run_btn.grid(row=2, column=0)

        self.stop_btn = ctk.CTkButton(
            self,
            text="Stop Sending ⛔",
            command=self.stopping_sending,
            font=("arial", 12, "bold"),
        )
        self.stop_btn.grid(row=2, column=1)

        self.resume_btn = ctk.CTkButton(
            self,
            text="Resume Button",
            command=self.resume_fun,
            font=("arial", 12, "bold"),
        )

        self.resume_btn.grid(row=2, column=2)

        self.import_numbers_btn = ctk.CTkButton(
            self,
            text="Import Numbers",
            command=self.import_numbers_fun,
            font=("arial", 12, "bold"),
        )
        self.import_numbers_btn.grid(row=2, column=3)

        self.clear_numbers = ctk.CTkButton(
            self,
            text="Clear Numbers",
            command=self.clear_numbers_fun,
            font=("arial", 12, "bold"),
        )
        self.clear_numbers.grid(row=2, column=4)

    def resume_fun(self):
        whatsapp_app.resume_sending()

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

        # ✅ افتح المتصفحات مرة واحدة فقط
        # if not self.whatsapp_sender.browsers_opened:
        #     self.whatsapp_sender.open_browser_only(self.selected_numbers)
        #     print("💬 سجل دخول الواتساب في كل نافذة، ثم اضغط Run مرة أخرى")
        #     return

        # ✅ ابدأ الإرسال بالخلفية
        threading.Thread(
            target=self.whatsapp_sender.start_sending,
            args=(
                self.selected_numbers,
                self.data_numbers,
                self.messages,
                1.5,
                3.5,
                True,
            ),
            kwargs={"on_message_sent": self.update_gui},  # 👈 تمرير callback
            daemon=True,
        ).start()

    def update_gui(self, number, channel):
        if channel == None:
            print("NOT sender ")
        # لازم التنفيذ في Main Thread
        print(f"Gui: Number: {number}, Channel {channel}")
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
            print(f"⚠️ خطأ أثناء محاولة إيقاف الإرسال: {e}")

    def clear_numbers_fun(self):
        self.data_numbers.clear()
        self.view_tree_results.clear()
        print("🧹 Numbers cleared from table.")

    def import_numbers_fun(self):
        filepath = ctk.filedialog.askopenfilename()
        if not filepath:
            return
        new_rows = []
        try:
            with open(filepath, mode="r", encoding="utf-8") as file_obj:
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
