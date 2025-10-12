import customtkinter as ctk
from tkinter import ttk

class ModernCTkTable(ctk.CTkFrame):
    def __init__(self, parent, data, headers, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.original_data = data[:]  
        self.data = data
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
        """استبدال البيانات القديمة بالجديدة"""
        self.data = new_data
        self.insert_data()
        self.update_scrollbar_visibility()

    def add_data(self, phone_numbers):
        """
        تضيف رقم أو أكتر للجدول الحالي.
        - phone_numbers ممكن يكون رقم واحد أو list من الأرقام.
        - الـ ID بيتولّد تلقائي.
        - Last Used بيتساب فاضي أو بـ "#" مؤقتًا.
        """
        if isinstance(phone_numbers, (str, int)):
            phone_numbers = [phone_numbers]

        # تحديد آخر ID موجود
        if self.data:
            try:
                last_id = int(self.data[-1][0])
            except Exception:
                last_id = len(self.data)
        else:
            last_id = 0

        new_rows = []
        for i, number in enumerate(phone_numbers, start=1):
            new_id = str(last_id + i)
            new_rows.append([new_id, str(number), "#"])  # last used = "#"

        # تحديث البيانات
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
