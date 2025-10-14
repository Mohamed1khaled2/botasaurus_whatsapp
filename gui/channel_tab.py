import threading
import whatsapp_automation 
import customtkinter as ctk
from gui.view_tree_data import ModernCTkTable


class ChannelsTab(ctk.CTkFrame):
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # ✅ بيانات افتراضية
        headers = ["ID", "Number", "Last Time Used"]

        

        self.search_after_id = None

        # توزيع الأعمدة والصفوف
        self.columnconfigure((0, 1, 2, 3), weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=3)
        self.rowconfigure(2, weight=1)

        # 🔍 مربع البحث في النص فوق
        self.search_entry = ctk.CTkEntry(self, placeholder_text="Type to search...", width=-220)
        
        self.search_entry.grid(row=0, column=1, columnspan=2,  pady=10, sticky="nsew")
        self.search_entry.bind("<KeyRelease>", self.live_search)

        # 📋 الجدول
        self.table = ModernCTkTable(self, headers=headers)
        self.table.grid(row=1, column=0, columnspan=4, sticky="nsew", padx=10, pady=5)

        # 🔘 الأزرار تحت

        open_btn = ctk.CTkButton(self, text="Open Only", command=self.open_only)
        open_btn.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)
        add_number_btn = ctk.CTkButton(self, text="Add Number", command=self.input_dialog)
        add_number_btn.grid(row=2, column=1, sticky="nsew", padx=5, pady=5)

        clear_numbers_btn = ctk.CTkButton(self, text='Clear Numbers', fg_color='red', command=self.clear_number)
        clear_numbers_btn.grid(row=2, column=2, sticky="nsew", padx=5, pady=5)

        deleted_selected_rows_btn = ctk.CTkButton(self, text='Delete Selected Numbers', fg_color='red', command=self.del_selected_number)
        deleted_selected_rows_btn.grid(row=2, column=3, sticky="nsew", padx=5, pady=5)
        
    def clear_number(self):
        self.table.clear_all_data()

    def del_selected_number(self):
        self.table.del_selected_rows()

    def input_dialog(self):
        dialog = ctk.CTkInputDialog(text="Type in a number:", title="Test")
        self.table.add_data(dialog.get_input())

    # ======================================================
    # 🔍 بحث حي
    # ======================================================
    def live_search(self, event=None):
        if self.search_after_id:
            self.after_cancel(self.search_after_id)
        self.search_after_id = self.after(300, self.do_search)

    def do_search(self):

        keyword = self.search_entry.get().strip()

        # لو البحث فاضي → رجع كل الأرقام
        if not keyword:
            filtered = self.table.connection_database.get_all_numbers()
        else:
            filtered = self.table.connection_database.search_numbers(keyword)

        # حدث الجدول بالنتائج
        self.table.update_data(filtered)


    # ======================================================
    # 📱 دوال التحكم في واتساب
    # ======================================================
    def get_selected_numbers(self):
        """ترجع الأرقام اللي المستخدم محددها من الجدول"""
        return [row[1] for row in self.table.get_selected_rows()]

    def open_only(self):
        """فتح واتساب فقط بدون إرسال"""
        selected = self.get_selected_numbers()
        if not selected:
            print("⚠️ اختر رقم واحد على الأقل من الجدول.")
            return
        print("🟢 Opening browsers only...")
        threading.Thread(
            target=whatsapp_automation.run,
            args=(selected, ['hello'], ['01002097448'], True),  # True = open_only
            daemon=True,
        ).start()

    def start_sending(self):
        """فتح واتساب + إرسال الرسائل"""
        selected = self.get_selected_numbers()
        if not selected:
            print("⚠️ اختر رقم واحد على الأقل من الجدول.")
            return
        print("🚀 Starting full automation...")
        threading.Thread(
            target=whatsapp_automation.run,
            args=(selected, ['hello', 'hi'], ['01002097448', '01093998000'], False),  # False = start_sending
            daemon=True,
        ).start()   
        

