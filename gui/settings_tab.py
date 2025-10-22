import customtkinter as ctk
from mange_settings import *

class WaysToSendFrame(ctk.CTkFrame):
    def __init__(self, master, notify_fun, **kwargs):
        super().__init__(master, **kwargs)

        self.notify_fun = notify_fun

        self.columnconfigure((0, 1), weight=1)
        self.rowconfigure((0, 1), weight=1)

        self.ws_json = load_settings()['ways_to_send']

        # ✅ المتغيرات
        self.with_google_contacts_var = ctk.BooleanVar(value=self.ws_json['google_contacts'])
        self.with_chat_me_li_var = ctk.BooleanVar(value=self.ws_json['chat_me_link'])
        self.with_chat_me_num_var = ctk.BooleanVar(value=self.ws_json['chat_me_number'])

        # ✅ Checkboxes
        self.with_google_contacts_cb = ctk.CTkCheckBox(
            self,
            text="By Google Contacts",
            command=self.checkbox_event,
            variable=self.with_google_contacts_var,
            font=("arial", 13, "bold"),
        )

        self.with_chat_with_me_li_cb = ctk.CTkCheckBox(
            self,
            text="Chat With Me Link",
            command=self.checkbox_event,
            variable=self.with_chat_me_li_var,
            font=("arial", 13, "bold"),
        )

        self.with_chat_with_me_num_cb = ctk.CTkCheckBox(
            self,
            text="Chat With Me Num",
            command=self.checkbox_event,
            variable=self.with_chat_me_num_var,
            font=("arial", 13, "bold"),
        )

        self.with_google_contacts_cb.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.with_chat_with_me_li_cb.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.with_chat_with_me_num_cb.grid(row=0, column=1, padx=0, pady=10, sticky="w")

    def checkbox_event(self):
        print("Google Contacts:", self.with_google_contacts_var.get())
        print("Chat With Me Link:", self.with_chat_me_li_var.get())
        print("Chat With Me Number:", self.with_chat_me_num_var.get())
        print("-----")

        self.notify_fun()


class SettingTab(ctk.CTkFrame):
    def __init__(self, master, on_settings_changed=None, **kwargs):
        super().__init__(master, **kwargs)

        self.settings = load_settings()
        self.on_settings_changed = on_settings_changed

        self.columnconfigure((0, 1), weight=1)
        self.rowconfigure((0, 1, 2), weight=1)

        self.label_settings = ctk.CTkLabel(
            self, text="Settings", font=("Arial", 35, "bold")
        )
        self.label_settings.grid(row=0, column=0, columnspan=2, pady=20)

        self.ways_to_send = WaysToSendFrame(
            self, notify_fun=self.notify_settings_changed
        )
        self.ways_to_send.grid(column=0, row=1, sticky="nswe", padx=5, pady=20)

        # ✅ تحديث أولي
        self.notify_settings_changed()

    def update_ways_to_send(self):
        google_contacts = self.ways_to_send.with_google_contacts_var.get()
        chat_me_link = self.ways_to_send.with_chat_me_li_var.get()
        chat_me_number = self.ways_to_send.with_chat_me_num_var.get()

        if not google_contacts and not chat_me_link and not chat_me_number:
            self.ways_to_send.with_chat_me_li_var.set(value=True)

        set_setting('ways_to_send.google_contacts', google_contacts)
        set_setting('ways_to_send.chat_me_link', chat_me_link)
        set_setting('ways_to_send.chat_me_number', chat_me_number)

    def notify_settings_changed(self):
        self.update_ways_to_send()
        self.settings = load_settings()
        print("Updated Settings:", self.settings)
        if self.on_settings_changed:
            self.on_settings_changed(self.settings)



if __name__ == "__main__":
    app = ctk.CTk()
    app.geometry("500x300")
    app.title("Settings Example")

    setting_tab = SettingTab(app)
    setting_tab.pack(expand=True, fill="both")

    app.mainloop()
