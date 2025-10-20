import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from gui.main_window import App
import customtkinter as ctk
import tkinter as tk


if __name__ == "__main__":
    # ✅ باتش عام لكل CTkEntry لتفعيل Ctrl+V
    _original_ctkentry_init = ctk.CTkEntry.__init__

    def _patched_ctkentry_init(self, *args, **kwargs):
        _original_ctkentry_init(self, *args, **kwargs)
        self.bind("<Control-v>", lambda e: self.event_generate("<<Paste>>"))
        self.bind("<Control-V>", lambda e: self.event_generate("<<Paste>>"))
        self.bind("<Control-c>", lambda e: self.event_generate("<<Copy>>"))
        self.bind("<Control-C>", lambda e: self.event_generate("<<Copy>>"))
        self.bind("<Control-a>", lambda e: self.event_generate("<<SelectAll>>"))
        self.bind("<Control-A>", lambda e: self.event_generate("<<SelectAll>>"))

    ctk.CTkEntry.__init__ = _patched_ctkentry_init

    # ✅ شغّل التطبيق
    app = App()

    # ✅ نحصل على الـ root الحقيقي
    root = app.winfo_toplevel()

    # ✅ إنشاء قائمة كليك يمين عامة لكل Entry
    context_menu = tk.Menu(root, tearoff=0)
    context_menu.add_command(label="Cut", command=lambda: root.focus_get().event_generate("<<Cut>>"))
    context_menu.add_command(label="Copy", command=lambda: root.focus_get().event_generate("<<Copy>>"))
    context_menu.add_command(label="Paste", command=lambda: root.focus_get().event_generate("<<Paste>>"))
    context_menu.add_separator()
    context_menu.add_command(label="Select All", command=lambda: root.focus_get().event_generate("<<SelectAll>>"))

    def _show_entry_menu(event):
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()

    # ✅ نربط كليك يمين بكل حقول الإدخال
    root.bind_class("Entry", "<Button-3>", _show_entry_menu)

    # ✅ تشغيل التطبيق
    app.mainloop()


"""
🧩 أمر التحزيم:
python -m nuitka main.py --standalone --enable-plugin=tk-inter --include-package=customtkinter \
--include-data-file=rocket.ico=rocket.ico --include-data-file=locations.json=locations.json \
--windows-icon-from-ico="rocket.ico" --output-filename="Rocket Sender.exe" \
--windows-console-mode=force --mingw64
"""
