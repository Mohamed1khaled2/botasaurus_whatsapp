import customtkinter as ctk
import os

class MessagesTab(ctk.CTkFrame):
    def __init__(self, master, on_messages_changed=None, **kwargs):
        super().__init__(master, **kwargs)
        self.messages_list = []
        self.on_messages_changed = on_messages_changed  # ✅ callback عند التغيير

        self.rowconfigure((0), weight=2)
        self.rowconfigure((1), weight=1)
        self.columnconfigure((0,1), weight=1)

        self.scroll_frame = ctk.CTkScrollableFrame(self, width=400, height=200)
        self.scroll_frame.grid(padx=20, pady=10, row=0, column=0, columnspan=2, sticky="nsew")

        self.label_path_show = ctk.CTkLabel(
            self.scroll_frame,
            text="",
            font=('Tahoma', 14, 'bold'),
            justify="right",
            anchor='e',
            wraplength=380,
        )
        self.label_path_show.pack(anchor="e", pady=5, fill="x", padx=10)

        self.import_messages = ctk.CTkButton(self, text="Import Messages", command=self.import_messages_fun)
        self.import_messages.grid(column=0, row=1)

        self.clear_messages = ctk.CTkButton(self, text="Clear Messages", command=self.clear_messages_fun)
        self.clear_messages.grid(column=1, row=1)

    def import_messages_fun(self):
        path_messages = ctk.filedialog.askopenfilenames(
            filetypes=[("Text Files", "*.txt")],
            title="Select Text Files"
        )
        if not path_messages:
            return
        
        names = [os.path.basename(path) for path in path_messages]
        self.label_path_show.configure(text='\n'.join(names))
        
        for path_message in path_messages:
            with open(path_message, mode='r', encoding='utf-8') as file:
                msg_ = file.read().strip()
                if msg_:
                    self.messages_list.append(msg_)

        if self.on_messages_changed:
            self.on_messages_changed(self.messages_list)

    def clear_messages_fun(self):
        self.messages_list.clear()
        self.label_path_show.configure(text="")
        if self.on_messages_changed:
            self.on_messages_changed(self.messages_list)

    @property
    def messages(self):
        return self.messages_list
