import customtkinter as ctk
from tkinter import ttk
from typing import Any, List, Tuple, Optional


class ModernCTkTable(ctk.CTkFrame):
    """
    جدول عرض بيانات متطور باستخدام CustomTkinter.
    - يعرض البيانات فقط (Viewer).
    - لا يتعامل مباشرة مع قاعدة البيانات.
    - يمكن تفعيله بعمود ✅ باستخدام checked_column=True.
    """

    def __init__(
        self,
        parent: Any,
        headers: List[str],
        data: Optional[List[Tuple[Any, ...]]] = None,
        checked_column: bool = False,
        on_check_changed=None,  # ✅ دالة يتم استدعاؤها عند تغيير ✅
        *args,
        **kwargs
    ):
        super().__init__(parent, *args, **kwargs)

        # ✅ خزّن الدالة عشان تُستخدم لما يتغير الاختيار
        self.on_check_changed = on_check_changed

        # الإعدادات العامة
        self.checked_column: bool = checked_column
        self.headers: List[str] = [""] + headers if checked_column else headers
        self.data: List[Tuple[Any, ...]] = data or []
        self.checked_state: dict[str, bool] = {}

        # إنشاء إطار الجدول
        self.table_frame = ctk.CTkFrame(self)
        self.table_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.setup_widgets()
        self.insert_data(self.data)
        self.update_scrollbar_visibility()

        self.tree.bind("<Configure>", lambda e: self.update_scrollbar_visibility())
        self.bind("<Configure>", lambda e: self.update_scrollbar_visibility())

    # ---------------------------------------------------------------------
    def setup_widgets(self) -> None:
        """تجهيز شكل الجدول"""
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

        self.tree = ttk.Treeview(
            self.table_frame,
            columns=self.headers,
            show="headings",
            selectmode="browse"
        )
        self.tree.pack(fill="both", expand=True, side="left")

        for i, header in enumerate(self.headers):
            width = 40 if (self.checked_column and i == 0) else 150
            self.tree.heading(header, text=header, anchor="center")
            self.tree.column(header, width=width, anchor="center")

        # Scrollbar
        self.vsb = ctk.CTkScrollbar(
            self.table_frame, orientation="vertical", command=self.tree.yview)
        self.vsb.pack_forget()
        self.tree.configure(yscrollcommand=self.vsb.set)

        # ألوان الصفوف
        self.tree.tag_configure('odd', background="#303030")
        self.tree.tag_configure('even', background="#232323")

        if self.checked_column:
            self.tree.bind("<Button-1>", self.on_click)

    # ---------------------------------------------------------------------
    def insert_data(self, data: List[Tuple[Any, ...]]) -> None:
        """عرض البيانات الجديدة بالكامل"""
        self.tree.delete(*self.tree.get_children())
        self.checked_state.clear()
        self.data = data

        for index, row in enumerate(data):
            tag = 'even' if index % 2 == 0 else 'odd'
            if self.checked_column:
                values = ["⬜"] + list(row)
                iid = self.tree.insert("", "end", values=values, tags=(tag,))
                self.checked_state[iid] = False
            else:
                self.tree.insert("", "end", values=list(row), tags=(tag,))

    # ---------------------------------------------------------------------
    def on_click(self, event) -> None:
        """تبديل ✅"""
        if not self.checked_column:
            return

        region = self.tree.identify("region", event.x, event.y)
        if region != "cell":
            return

        col = self.tree.identify_column(event.x)
        row = self.tree.identify_row(event.y)

        if col == "#1" and row:
            current_vals = list(self.tree.item(row, "values"))
            is_checked = self.checked_state.get(row, False)
            current_vals[0] = "✅" if not is_checked else "⬜"
            self.tree.item(row, values=current_vals)
            self.checked_state[row] = not is_checked

            # ✅ نادِ الدالة لو موجودة
            if self.on_check_changed:
                self.on_check_changed()

    # ---------------------------------------------------------------------
    def get_selected_rows(self) -> List[Tuple[Any, ...]]:
        """إرجاع الصفوف المحددة ✅"""
        if not self.checked_column:
            return [self.tree.item(iid, "values") for iid in self.tree.get_children()]

        selected = []
        for iid, checked in self.checked_state.items():
            if checked:
                vals = self.tree.item(iid, "values")[1:]
                selected.append(vals)
        return selected

    # ---------------------------------------------------------------------
    def clear(self) -> None:
        """مسح جميع الصفوف من العرض فقط"""
        self.tree.delete(*self.tree.get_children())
        self.checked_state.clear()
        self.data.clear()
        self.update_scrollbar_visibility()

    # ---------------------------------------------------------------------
    def update_scrollbar_visibility(self) -> None:
        """إظهار أو إخفاء Scrollbar تلقائيًا"""
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
            
    # ---------------------------------------------------------------------
   
    def add_data(self, new_rows: List[List[Any]]) -> None:
        """إضافة صفوف جديدة للعرض فقط (بدون تعديل قاعدة البيانات)"""
        start_index = len(self.data)
        for row in new_rows:
            # لو فيه checked_column → أضف ID و Last Used
            if self.checked_column:
                next_id = start_index + 1
                full_row = [next_id] + row + ["#"]  # ID + Number + Last Used
            else:
                full_row = row

            self.data.append(tuple(full_row))

            tag = 'even' if len(self.data) % 2 == 0 else 'odd'
            values = ["⬜"] + list(full_row) if self.checked_column else list(full_row)
            iid = self.tree.insert("", "end", values=values, tags=(tag,))
            if self.checked_column:
                self.checked_state[iid] = False

        self.update_scrollbar_visibility()
        
    def update_data(self, new_data: List[Tuple[Any, ...]]) -> None:
        """تحديث الجدول ببيانات جديدة مع الحفاظ على ✅ المحددة"""
        selected = set()
        if self.checked_column:
            for iid, checked in self.checked_state.items():
                if checked:
                    vals = self.tree.item(iid, "values")
                    if len(vals) >= 2:
                        selected.add(str(vals[1]).strip())

        self.data = new_data
        yview = self.tree.yview()
        self.tree.delete(*self.tree.get_children())
        self.checked_state.clear()

        for index, row in enumerate(new_data):
            tag = 'even' if index % 2 == 0 else 'odd'
            number = str(row[0]).strip() if row else ""
            is_checked = number in selected
            checkbox = "✅" if is_checked else "⬜"
            values = [checkbox] + list(row) if self.checked_column else list(row)
            iid = self.tree.insert("", "end", values=values, tags=(tag,))
            self.checked_state[iid] = is_checked

        self.tree.yview_moveto(yview[0])
        if self.checked_column:
            self.tree.bind("<Button-1>", self.on_click)
        self.update_scrollbar_visibility()
        
        
    def get_row_index_by_value(self, value: str) -> int:
        """
        تبحث في كل صفوف الجدول عن القيمة المحددة وتعيد رقم الصف (index) لو لقتها.
        لو مش لاقياها، ترجع -1.

        Args:
            value (str): القيمة المطلوب البحث عنها

        Returns:
            int: رقم الصف (0 أو أكثر) أو -1 لو القيمة مش موجودة
        """
        for i, iid in enumerate(self.tree.get_children()):
            row_values = self.tree.item(iid, "values")
            for cell in row_values:
                if str(cell).strip().lower() == str(value).strip().lower():
                    return i
        return -1
    
    
    def update_cell_value(self, row_index: int, col_index: int, new_value: str) -> None:
        """
        تحديث قيمة خلية معينة داخل الجدول بناءً على رقم الصف والعمود.

        Args:
            row_index (int): رقم الصف (يبدأ من 0)
            col_index (int): رقم العمود (يبدأ من 0، ولو فيه عمود ✅ بيتحسب كمان)
            new_value (str): القيمة الجديدة اللي هتتحط
        """
        # الحصول على كل صفوف الجدول
        items = self.tree.get_children()
        if row_index < 0 or row_index >= len(items):
            print("⚠️ رقم الصف غير صالح.")
            return

        iid = items[row_index]
        values = list(self.tree.item(iid, "values"))

        if col_index < 0 or col_index >= len(values):
            print("⚠️ رقم العمود غير صالح.")
            return

        # تعديل القيمة المطلوبة
        values[col_index] = new_value
        self.tree.item(iid, values=values)

        # تحديث النسخة المحلية self.data لو حابب تحافظ على التزامن
        if row_index < len(self.data):
            row_data = list(self.data[row_index])
            try:
                # لو فيه عمود ✅ يبقى أول عمود مش من الداتا الأصلية
                real_col_index = col_index - 1 if self.checked_column else col_index
                if 0 <= real_col_index < len(row_data):
                    row_data[real_col_index] = new_value
                    self.data[row_index] = tuple(row_data)
            except Exception as e:
                print(f"⚠️ خطأ أثناء تحديث self.data: {e}")
                
                
    def delete_rows(self, rows_to_delete: Optional[List[Tuple[Any, ...]]] = None) -> None:
        """
        حذف صفوف محددة من الجدول.
        
        Args:
            rows_to_delete (Optional[List[Tuple[Any, ...]]]): 
                قائمة الصفوف التي سيتم حذفها.
                إذا لم يتم تمريرها، سيتم حذف الصفوف المحددة ✅ فقط.
        """
        # لو الجدول فيه checkbox واختار ✅
        if self.checked_column and rows_to_delete is None:
            rows_to_delete = self.get_selected_rows()

        if not rows_to_delete:
            print("⚠️ لا توجد صفوف لحذفها.")
            return

        # نحول الصفوف إلى مجموعة لسهولة المقارنة
        rows_to_delete_set = {tuple(map(str, r)) for r in rows_to_delete}

        remaining_data = []
        for iid in self.tree.get_children():
            row_values = list(self.tree.item(iid, "values"))
            if self.checked_column:
                row_values = row_values[1:]  # استبعد عمود ✅

            if tuple(map(str, row_values)) not in rows_to_delete_set:
                remaining_data.append(row_values)
            else:
                self.tree.delete(iid)
                if iid in self.checked_state:
                    del self.checked_state[iid]
        # تحديث البيانات المعروضة
        self.data = remaining_data
        self.update_scrollbar_visibility()
        