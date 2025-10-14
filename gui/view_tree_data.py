import customtkinter as ctk
from tkinter import ttk
import conn_database
from manage_profiles import ManageFiles



class ModernCTkTable(ctk.CTkFrame):
    def __init__(self, parent, headers, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        
        self.connection_database = conn_database.ChanDataBase()
        
        self.data = self.connection_database.get_all_numbers()
        self.headers = [""] + headers
        self.checked_state = {}

        self.table_frame = ctk.CTkFrame(self)
        self.table_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.setup_widgets()
        self.insert_data()
        self.update_scrollbar_visibility()

        self.tree.bind("<Configure>", lambda e: self.update_scrollbar_visibility())
        self.bind("<Configure>", lambda e: self.update_scrollbar_visibility())

    def setup_widgets(self):
        style = ttk.Style()
        style.theme_use('clam')

        style.configure("Treeview",
                        background="#2b2b2b",
                        foreground="#e0e0e0",
                        rowheight=30,
                        fieldbackground="#2b2b2b",
                        font=("Segoe UI", 10))

        style.configure("Treeview.Heading",
                        background="#1f1f1f",
                        foreground="#f0f0f0",
                        font=("Segoe UI", 11, "bold"),
                        relief="flat")

        style.map("Treeview.Heading",
                  background=[("active", "#1f1f1f")],
                  relief=[("active", "flat")])
     
        style.map("Treeview",
                  background=[("selected", "#4a90e2")],
                  foreground=[("selected", "#ffffff")])

        self.tree = ttk.Treeview(self.table_frame, columns=self.headers, show="headings", selectmode="browse")
        self.tree.pack(fill="both", expand=True, side="left")

        for i, header in enumerate(self.headers):
            width = 40 if i == 0 else 150
            self.tree.heading(header, text=header, anchor="center")
            self.tree.column(header, width=width, anchor="center")

        self.vsb = ctk.CTkScrollbar(self.table_frame, orientation="vertical", command=self.tree.yview)
        self.vsb.pack_forget()
        self.tree.configure(yscrollcommand=self.vsb.set)

        self.tree.tag_configure('odd', background="#303030")
        self.tree.tag_configure('even', background="#232323")

        self.tree.bind("<Button-1>", self.on_click)

    def insert_data(self):
        self.tree.delete(*self.tree.get_children())
        self.checked_state.clear()

        for index, row in enumerate(self.data):
            checkbox = "⬜"
            values = [checkbox] + list(row)
            tag = 'even' if index % 2 == 0 else 'odd'
            iid = self.tree.insert("", "end", values=values, tags=(tag,))
            self.checked_state[iid] = False

    def update_data(self, new_data):
        """استبدال البيانات القديمة بالجديدة مع الحفاظ على حالة التحديد ✅"""

        # حفظ الأرقام اللي كانت محددة ✅ قبل التحديث
        selected_numbers = set()
        for iid, checked in self.checked_state.items():
            if checked:
                vals = self.tree.item(iid, "values")
                if len(vals) >= 3:
                    selected_numbers.add(str(vals[2]).strip())

        # تحديث البيانات
        self.data = new_data

        # حفظ موضع الـ scrollbar
        yview = self.tree.yview()

        # مسح الجدول الحالي
        self.tree.delete(*self.tree.get_children())
        self.checked_state.clear()

        # إعادة إدخال البيانات الجديدة
        for index, row in enumerate(self.data):
            number = str(row[1]).strip() if len(row) > 1 else ""
            is_checked = number in selected_numbers  # لو الرقم كان محدد ✅
            checkbox = "✅" if is_checked else "⬜"

            values = [checkbox] + list(row)
            tag = 'even' if index % 2 == 0 else 'odd'
            iid = self.tree.insert("", "end", values=values, tags=(tag,))
            self.checked_state[iid] = is_checked

        # إعادة موضع الـ scrollbar
        self.tree.yview_moveto(yview[0])

        # إعادة تفعيل حدث الكليك بعد التحديث
        self.tree.bind("<Button-1>", self.on_click)

        # تحديث حالة الـ scrollbar
        self.update_scrollbar_visibility()


    def add_data(self, phone_numbers):
        
        if isinstance(phone_numbers, (str, int)):
            phone_numbers = [phone_numbers]

        # جمع الأرقام الحالية في الجدول (العمود الثاني)
        existing_numbers = {str(self.tree.item(iid, "values")[2]).strip() for iid in self.tree.get_children()}


        print(existing_numbers)
        
        new_rows = []
        for number in phone_numbers:
            if str(number).strip() in existing_numbers:
                print(f"⚠️ الرقم {number} موجود بالفعل في الجدول ولن يُضاف.")
                continue  # تجاهل الرقم المكرر

            # إضافة الرقم في قاعدة البيانات
            new_row = self.connection_database.add_number(number, "#")
            new_rows.append(new_row)
            existing_numbers.add(str(number).strip())

        # تحديث البيانات المعروضة في الجدول
        self.data.extend(new_rows)
        start_index = len(self.data) - len(new_rows)

        for i, row in enumerate(new_rows):
            index = start_index + i
            checkbox = "⬜"
            values = [checkbox] + list(row)
            tag = 'even' if index % 2 == 0 else 'odd'
            iid = self.tree.insert("", "end", values=values, tags=(tag,))
            self.checked_state[iid] = False

        self.update_scrollbar_visibility()
        
    def update_scrollbar_visibility(self):
        total_rows = len(self.data)
        row_height = 30
        tree_height_px = self.tree.winfo_height()
        if tree_height_px <= 1:
            self.after(100, self.update_scrollbar_visibility)
            return

        visible_rows = tree_height_px // row_height
        if total_rows > visible_rows:
            self.vsb.pack(side="right", fill="y")
            self.tree.configure(yscrollcommand=self.vsb.set)
        else:
            self.vsb.pack_forget()
            self.tree.configure(yscrollcommand=None)

    def on_click(self, event):
        region = self.tree.identify("region", event.x, event.y)
        if region != "cell":
            return

        col = self.tree.identify_column(event.x)
        row = self.tree.identify_row(event.y)

        if col == "#1" and row:
            current_vals = list(self.tree.item(row, "values"))
            is_checked = self.checked_state.get(row, False)

            new_checkbox = "✅" if not is_checked else "⬜"
            current_vals[0] = new_checkbox
            self.tree.item(row, values=current_vals)
            self.checked_state[row] = not is_checked

    def get_selected_rows(self):
        selected = []
        for iid, checked in self.checked_state.items():
            if checked:
                vals = self.tree.item(iid, "values")[1:]
                selected.append(vals)
        return selected
    
    def del_selected_rows(self):
        """حذف كل الصفوف اللي عليها ✅ من الجدول وقاعدة البيانات"""
        checked_rows = []
        for iid, checked in list(self.checked_state.items()):
            if checked:
                vals = self.tree.item(iid, "values")
                if len(vals) >= 3:
                    _id = vals[1]
                    number = vals[2]
                    checked_rows.append((iid, number))

        if not checked_rows:
            print("⚠️ لا يوجد صفوف محددة للحذف.")
            return

        confirm = ctk.CTkInputDialog(
            text=f"سيتم حذف {len(checked_rows)} صف. اكتب 'yes' للتأكيد:",
            title="تأكيد الحذف"
        ).get_input()

        if not confirm or confirm.lower().strip() != "yes":
            print("🚫 تم إلغاء عملية الحذف.")
            return

        # حذف من قاعدة البيانات
        for _, number in checked_rows:
            self.connection_database.delete_number(number)

        # حذف من الواجهة
        for iid, _ in checked_rows:
            self.tree.delete(iid)
            self.checked_state.pop(iid, None)

        # تحديث self.data (إزالة المحذوفين)
        remaining = []
        for row in self.data:
            if str(row[1]) not in [num for _, num in checked_rows]:
                remaining.append(row)
        self.data = remaining

        self.update_scrollbar_visibility()
        
        ManageFiles().del_profile([checked_rows[0][1]])
        print(f"🗑️ تم حذف {len(checked_rows)} صف بنجاح.")
            
    def clear_all_data(self):
        """مسح جميع البيانات من قاعدة البيانات والجدول"""
        confirm = ctk.CTkInputDialog(
            text="⚠️ هل أنت متأكد من حذف كل البيانات؟ اكتب 'yes' للتأكيد:",
            title="تأكيد الحذف"
        ).get_input()

        if confirm and confirm.lower().strip() == "yes":
            # حذف من قاعدة البيانات
            self.connection_database.clear_all_numbers()
            
            
            # حذف من الواجهة
            self.tree.delete(*self.tree.get_children())
            self.checked_state.clear()
            self.data.clear()
            self.update_scrollbar_visibility()
            
            
            # ManageFiles().del_profile([checked_rows[0][1]])

            print(self.tree.get_children())

            print("🧹 تم مسح كل البيانات بنجاح.")
        else:
            print("🚫 تم إلغاء عملية الحذف.")