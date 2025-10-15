import customtkinter as ctk

class MessagesTab(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.rowconfigure((0), weight=2)
        self.rowconfigure((1), weight=1)
        self.columnconfigure((0,1), weight=1)
        
        
        self.scroll_frame = ctk.CTkScrollableFrame(self, width=400, height=200)
        self.scroll_frame.grid(padx=20, pady=10, row=0, column=0, columnspan=2, sticky="nsew")
        
        self.import_messages = ctk.CTkButton(self, text="Import Messages", command=self.import_messages_fun)
        self.import_messages.grid(column=0, row=1)
        
        self.clear_messages = ctk.CTkButton(self, text="Clear Messages")
        self.clear_messages.grid(column=1, row=1)

        
    def import_messages_fun(self):
        pass