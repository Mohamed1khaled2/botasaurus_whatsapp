import threading
import whatsapp_automation 
import customtkinter as ctk
from gui.view_tree_data import ModernCTkTable
import conn_database

class ChannelsTab(ctk.CTkFrame):
    def __init__(self, master, on_selection_changed=None, **kwargs):
        super().__init__(master, **kwargs)
       
        self.on_selection_changed = on_selection_changed  # ✅ callback عند التغيير
        self.connection_database = conn_database.ChanDataBase()
        self.search_after_id = None

        headers = ["ID", "Number", "Last Time Used"]
        self.columnconfigure((0, 1, 2, 3), weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=3)
        self.rowconfigure(2, weight=1)

        self.search_entry = ctk.CTkEntry(self, placeholder_text="Type to search...", width=-220)
        self.search_entry.grid(row=0, column=1, columnspan=2, pady=10, sticky="nsew")
        self.search_entry.bind("<KeyRelease>", self.live_search)

        self.table = ModernCTkTable(
            self, 
            headers=headers, 
            data=self.connection_database.get_all_numbers(), 
            checked_column=True,
            on_check_changed=self.notify_selection_changed  # ✅ تحديث الأرقام عند الاختيار
        )
        self.table.grid(row=1, column=0, columnspan=4, sticky="nsew", padx=10, pady=5)

        open_btn = ctk.CTkButton(self, text="Open Only", command=self.open_only, corner_radius=8 , font=('arial', 12, 'bold'))
        open_btn.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)
        add_number_btn = ctk.CTkButton(self, text="Add Number", command=self.input_dialog, corner_radius=8, font=('arial', 12, 'bold') )
        add_number_btn.grid(row=2, column=1, sticky="nsew", padx=5, pady=5)

        clear_numbers_btn = ctk.CTkButton(self, text='Clear Numbers', fg_color='#7a0e02', hover_color='red', corner_radius=8,  command=self.clear_number, font=('arial', 12, 'bold'))
        clear_numbers_btn.grid(row=2, column=2, sticky="nsew", padx=5, pady=5)

        deleted_selected_rows_btn = ctk.CTkButton(self, text='Delete Selected Numbers', corner_radius=8,  fg_color='#7a0e02', hover_color='red', command=self.del_selected_number, font=('arial', 12, 'bold'))
        deleted_selected_rows_btn.grid(row=2, column=3, sticky="nsew", padx=5, pady=5)
    
    def notify_selection_changed(self):
        """تنبيه للتابات الأخرى عند تغيير الاختيار"""
        if self.on_selection_changed:
            self.on_selection_changed(self.get_selected_numbers())

    def get_selected_numbers(self):
        return [row[1] for row in self.table.get_selected_rows()]

    def clear_number(self):
        confirm = ctk.CTkInputDialog(
            text=f"سيتم حذف {len(self.table.get_selected_rows())} صف. اكتب 'yes' للتأكيد:",
            title="تأكيد الحذف"
        ).get_input()
        
        if confirm and confirm.lower() == 'yes':
            self.table.clear()
            self.connection_database.clear_all_numbers()
            self.notify_selection_changed()

    def del_selected_number(self):
        confirm = ctk.CTkInputDialog(
            text=f"سيتم حذف {len(self.table.get_selected_rows())} صف. اكتب 'yes' للتأكيد:",
            title="تأكيد الحذف"
        ).get_input()
        
        if confirm and confirm.lower() == 'yes':
            for n in self.table.get_selected_rows():
                self.table.delete_rows()
                self.connection_database.delete_number(n[1])
            self.notify_selection_changed()
        else:
            print("❌ لم يتم حذف أي رقم")

    def input_dialog(self):
        dialog = ctk.CTkInputDialog(text="Type in a number:", title="Test")
        number = dialog.get_input()
        if number:
            self.table.add_data([[number]])
            self.connection_database.add_number(number, "#")
            
            

    def live_search(self, event=None):
        if self.search_after_id:
            self.after_cancel(self.search_after_id)
        self.search_after_id = self.after(300, self.do_search)

    def do_search(self):
        keyword = self.search_entry.get().strip()
        if not keyword:
            filtered = self.connection_database.get_all_numbers()
        else:
            filtered = self.connection_database.search_numbers(keyword)
        self.table.update_data(filtered)

    def open_only(self):
        selected_senders = self.get_selected_numbers()  # أرقام المرسلين المختارة
        # selected_receivers = self.get_selected_receivers()  # أرقام المستقبلين من جدول أو input
        # selected_messages = self.messages_tab.get_messages()  # قائمة الرسائل

        # if not selected_senders:
        #     print("⚠️ اختر رقم واحد على الأقل من المرسلين.")
        #     return
        # if not selected_receivers:
        #     print("⚠️ اختر رقم واحد على الأقل من المستقبلين.")
        #     return
        # if not selected_messages:
        #     print("⚠️ لم يتم تحديد أي رسالة للإرسال.")
        #     return

        print("🟢 Opening browsers only...")

        # تحويل تلقائي للقائمة إلى dict إذا كانت مجرد strings
        prepared_senders = []
        for s in selected_senders:
            if isinstance(s, str):
                prepared_senders.append({"phone_number": s, "profile": s})
            elif isinstance(s, dict):
                prepared_senders.append(s)
            else:
                print(f"⚠️ تجاهل عنصر غير مدعوم: {s}")

        # تشغيل فتح المتصفحات في ثريد منفصل وتمرير المستلمين والرسائل
        threading.Thread(
            target=lambda: whatsapp_automation.open_browser(
                prepared_senders,
            ),
            daemon=True,
        ).start()


