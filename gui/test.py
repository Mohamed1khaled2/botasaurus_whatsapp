import customtkinter as ctk
from tkinter import ttk

app = ctk.CTk()
app.title("Treeview Live Search (with Delay)")
app.geometry("500x400")

# إنشاء Treeview
tree = ttk.Treeview(app, columns=("Name", "Age", "Country"), show="headings")
for col in ("Name", "Age", "Country"):
    tree.heading(col, text=col)
tree.pack(expand=True, fill="both", pady=10)

# بيانات تجريبية
data = [
    ("Ali", 21, "Egypt"),
    ("Mona", 30, "Jordan"),
    ("Salma", 26, "Lebanon"),
    ("Mahmoud", 40, "Egypt"),
    ("Lina", 35, "Syria"),
    ("Hassan", 45, "Morocco"),
]

# تحميل البيانات في الجدول
def load_data(rows):
    tree.delete(*tree.get_children())
    for row in rows:
        tree.insert("", "end", values=row)

# ---- البحث مع delay ----
search_after_id = None  # متغير لحفظ الـ after ID

def live_search(event=None):
    global search_after_id
    if search_after_id:
        app.after_cancel(search_after_id)  # إلغاء أي عملية بحث قديمة
    search_after_id = app.after(300, do_search)  # انتظر 300 مللي ثانية قبل البحث

def do_search():
    keyword = search_entry.get().lower().strip()
    if keyword == "":
        load_data(data)
    else:
        filtered = [r for r in data if keyword in str(r).lower()]
        load_data(filtered)

# مربع البحث
search_entry = ctk.CTkEntry(app, placeholder_text="Type to search...")
search_entry.pack(pady=10)
search_entry.bind("<KeyRelease>", live_search)

# تحميل أولي للبيانات
load_data(data)

app.mainloop()
