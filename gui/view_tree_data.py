import customtkinter as ctk
from tkinter import ttk

class ModernCTkTable(ctk.CTkFrame):
    def __init__(self, parent, data, headers, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.data = data
        self.headers = [""] + headers  # عمود checkbox
        self.checked_state = {}

        self.setup_widgets()
        self.insert_data()
        self.update_scrollbar_visibility()

        # تحديث scrollbar عند تغيير الحجم
        self.tree.bind("<Configure>", lambda e: self.update_scrollbar_visibility())
        self.bind("<Configure>", lambda e: self.update_scrollbar_visibility())

    def setup_widgets(self):
        style = ttk.Style()
        style.theme_use('clam')

        # ألوان ثابتة للثيم الداكن
        bg_color = "#2b2b2b"         # خلفية الصفوف
        fg_color = "#e0e0e0"         # لون النص
        heading_bg = "#1f1f1f"       # خلفية رؤوس الأعمدة
        heading_fg = "#f0f0f0"       # لون نص الرؤوس
        select_bg = "#4a90e2"        # لون تحديد الصف
        select_fg = "#ffffff"

        style.configure("Treeview",
                        background=bg_color,
                        foreground=fg_color,
                        rowheight=30,
                        fieldbackground=bg_color,
                        font=("Segoe UI", 10))

        style.configure("Treeview.Heading",
                        background=heading_bg,
                        foreground=heading_fg,
                        font=("Segoe UI", 11, "bold"),
                        relief="flat")

        style.map("Treeview.Heading",
                background=[("active", heading_bg)],
                relief=[("active", "flat")])
        style.map("Treeview",
                  background=[("selected", select_bg)],
                  foreground=[("selected", select_fg)])

        self.tree = ttk.Treeview(self, columns=self.headers, show="headings", selectmode="browse")
        self.tree.pack(fill="both", expand=True, side="left")

        for i, header in enumerate(self.headers):
            width = 40 if i == 0 else 150
            anchor = "center" if i == 0 else "w"
            self.tree.heading(header, text=header)
            self.tree.column(header, width=width, anchor=anchor)

        self.vsb = ctk.CTkScrollbar(self, orientation="vertical", command=self.tree.yview)
        self.vsb.pack_forget()  # مخفية بشكل افتراضي
        self.tree.configure(yscrollcommand=self.vsb.set)

        # استخدام ألوان ثابتة للـ tags
        self.tree.tag_configure('odd', background="#303030")
        self.tree.tag_configure('even', background="#232323")

        self.tree.bind("<Button-1>", self.on_click)

    def insert_data(self):
        for index, row in enumerate(self.data):
            checkbox = "⬜"
            values = [checkbox] + list(row)
            tag = 'even' if index % 2 == 0 else 'odd'
            iid = self.tree.insert("", "end", values=values, tags=(tag,))
            self.checked_state[iid] = False

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


if __name__ == "__main__":
    ctk.set_appearance_mode("dark")  # اختار "dark" أو "light"
    ctk.set_default_color_theme("blue")  # "blue", "dark-blue", "green"

    root = ctk.CTk()
    root.geometry("700x450")
    root.title("Modern Table with Checkboxes - customtkinter")

    sample_data = [
        ("1", "Ahmed", "Developer"),
        ("2", "Mona", "Designer"),
        ("3", "Khaled", "Manager"),
        ("4", "Sara", "HR"),
        ("5", "Ali", "Tester"),
        ("6", "Layla", "Analyst"),
        ("7", "Omar", "Support"),
        ("8", "Nour", "Sales"),
    ]
    headers = ["ID", "Name", "Job"]

    table = ModernCTkTable(root, sample_data, headers)
    table.pack(fill="both", expand=True, padx=15, pady=15)

    root.mainloop()
