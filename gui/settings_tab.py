import customtkinter as ctk


class WaysToSendFrame(ctk.CTkFrame):
    def __init__(self, master, notify_fun, **kwargs):
        super().__init__(master, **kwargs)
        self.notify_fun = notify_fun  # ✅ حفظ الدالة المرسلة

        self.columnconfigure((0, 1), weight=1)
        self.rowconfigure((0, 1), weight=1)

        # ✅ المتغيرات
        self.with_google_contacts_var = ctk.BooleanVar(value=False)
        self.with_chat_me_li_var = ctk.BooleanVar(value=True)
        self.with_chat_me_num_var = ctk.BooleanVar(value=False)


        # ✅ Checkboxes
        self.with_google_contacts_cb = ctk.CTkCheckBox(
            self,
            text="By Google Contacts",
            command=self.checkbox_event,
            variable=self.with_google_contacts_var,
            font=('arial', 13, 'bold')
        )

        self.with_chat_with_me_li_cb = ctk.CTkCheckBox(
            self,
            text="Chat With Me Link",
            command=self.checkbox_event,
            variable=self.with_chat_me_li_var,
            font=('arial', 13, 'bold')
        )

        self.with_chat_with_me_num_cb = ctk.CTkCheckBox(
            self,
            text="Chat With Me Num",
            command=self.checkbox_event,
            variable=self.with_chat_me_num_var,
            font=('arial', 13, 'bold')
        )
        self.with_google_contacts_cb.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.with_chat_with_me_li_cb.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.with_chat_with_me_num_cb.grid(row=0, column=1, padx=0, pady=10, sticky="w")
        
        
    def checkbox_event(self):
        print("Google Contacts:", self.with_google_contacts_var.get())
        print("Chat With Me Link:", self.with_chat_me_li_var.get())
        print("Chat With Me Number:", self.with_chat_me_num_var.get())
        print("-----")

        # ✅ نبلغ SettingTab إن في تغيير حصل
        self.notify_fun()


class SettingTab(ctk.CTkFrame):
    def __init__(self, master, on_settings_changed=None, **kwargs):
        super().__init__(master, **kwargs)

        self.settings = {}

        self.columnconfigure((0, 1), weight=1)
        self.rowconfigure((0, 1, 2), weight=1)

        self.label_settings = ctk.CTkLabel(self, text="Settings", font=('Arial', 35, 'bold'))
        self.label_settings.grid(row=0, column=0, columnspan=2, pady=20)

        self.on_settings_changed = on_settings_changed

        self.ways_to_send = WaysToSendFrame(self, notify_fun=self.notify_settings_changed)
        self.ways_to_send.grid(column=0, row=1, sticky='nswe', padx=5, pady=20)

    def notify_settings_changed(self):
        # ✅ هنا ممكن تجمع القيم الجديدة من WaysToSendFrame
        self.settings = {
            "google_contacts": self.ways_to_send.with_google_contacts_var.get(),
            "chat_me_link": self.ways_to_send.with_chat_me_li_var.get(),
            "chat_me_number": self.ways_to_send.with_chat_me_num_var.get()
        }
        print("Updated Settings:", self.settings)

        # ✅ لو في callback خارجي، بلّغه
        if self.on_settings_changed:
            self.on_settings_changed(self.settings)


if __name__ == "__main__":
    app = ctk.CTk()
    app.geometry("500x300")
    app.title("Settings Example")

    setting_tab = SettingTab(app)
    setting_tab.pack(expand=True, fill="both")

    app.mainloop()
