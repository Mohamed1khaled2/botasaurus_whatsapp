import customtkinter as ctk
from tkinter import ttk, PhotoImage, TclError
from PIL import Image, ImageTk

class CheckBoxTreeview(ctk.CTkFrame):
    def __init__(self, parent, data=None, img_checked_path=None, img_unchecked_path=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)




        self.use_images = False
        self.checked_state = {}

        # style Tree view
        
        self.style = ttk.Style()

        self.style.configure("Treeview",
                background="white",
                foreground="black",
                rowheight=25,
                fieldbackground="lightgray",
                font=('Arial', 10))
        
        
        
        self.style.configure("Treeview.Heading",
                background="black",
                foreground="black",
                font=('Arial', 12, 'bold'),
                relief="flat")
        
        self.style.map("Treeview",
          background=[('selected', 'green')],
          foreground=[('selected', 'white')])

        # --------- حاول تحمل الصور أول ---------- 
        if img_checked_path and img_unchecked_path:
            try:
                self.img_unchecked = PhotoImage(file=img_unchecked_path)
                self.img_checked = PhotoImage(file=img_checked_path)
                self.use_images = True
            except (TclError, Exception):
                try:
                    im1 = Image.open(img_unchecked_path).resize((16, 16), Image.LANCZOS)
                    im2 = Image.open(img_checked_path).resize((16, 16), Image.LANCZOS)
                    self.img_unchecked = ImageTk.PhotoImage(im1)
                    self.img_checked = ImageTk.PhotoImage(im2)
                    self.use_images = True
                except Exception:
                    self.use_images = False

        # ---------- بناء الـ Treeview ----------
        if self.use_images:
            columns = ("id", "name", "job")
            self.tree = ttk.Treeview(self, columns=columns, show="tree headings", height=10)

            self.tree.heading("#0", text="#")
            self.tree.column("#0", width=40, anchor="center", stretch=False, minwidth=40)

            self.tree.heading("id", text="ID")
            self.tree.column("id", width=60, anchor="center")
            self.tree.heading("name", text="Name")
            self.tree.column("name", width=250, anchor="w")
            self.tree.heading("job", text="Job")
            self.tree.column("job", width=200, anchor="w")
            self.tree.tag_configure("oddrow", background="black")
            self.tree.tag_configure("evenrow", background="black")
            if data:
                for row in data:
                    iid = self.tree.insert("", "end", text="", image=self.img_unchecked, values=row)
                    self.checked_state[iid] = False

        else:
            columns = ("check", "id", "name", "job")
            self.tree = ttk.Treeview(self, columns=columns, show="headings", height=10)

            self.tree.heading("check", text="")
            self.tree.column("check", width=40, anchor="center")
            self.tree.heading("id", text="ID")
            self.tree.column("id", width=60, anchor="center")
            self.tree.heading("name", text="Name")
            self.tree.column("name", width=250, anchor="w")
            self.tree.heading("job", text="Job")
            self.tree.column("job", width=200, anchor="w")

            if data:
                for row in data:
                    self.tree.insert("", "end", values=("⬜",) + row)

        self.tree.pack(fill="both", expand=True, padx=12, pady=12)
        self.tree.bind("<Button-1>", self.on_tree_click)

    def on_tree_click(self, event):
        col = self.tree.identify_column(event.x)
        row = self.tree.identify_row(event.y)
        if not row:
            return

        if self.use_images:
            if col != "#0":
                return
            state = not self.checked_state.get(row, False)
            self.checked_state[row] = state
            self.tree.item(row, image=self.img_checked if state else self.img_unchecked)
        else:
            if col != "#1":
                return
            vals = list(self.tree.item(row, "values"))
            vals[0] = "✔" if vals[0] == "⬜" else "⬜"
            self.tree.item(row, values=vals)

    def get_selected(self):
        """ترجع كل الصفوف المتعلمة"""
        selected = []
        if self.use_images:
            for iid, state in self.checked_state.items():
                if state:
                    selected.append(self.tree.item(iid, "values"))
        else:
            for iid in self.tree.get_children():
                vals = self.tree.item(iid, "values")
                if vals[0] in ("✔", "☑", "✅"):
                    selected.append(vals[1:])
        return selected
