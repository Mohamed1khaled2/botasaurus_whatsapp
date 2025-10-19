import customtkinter as ctk

class SettingTab(ctk.CTkFrame):
    def __init__(self, master, on_settings_changed=None, **kwargs):
        super().__init__(master, **kwargs)
        
        self.settings = {"Hello World": "settings_tab"}
        
        
        self.columnconfigure((0, 1), weight=1)
        self.rowconfigure((0, 1), weight=1)
        self.on_settings_changed = on_settings_changed        
    
        self.one_button = ctk.CTkButton(self, text="Change Name", command=self.change_name)
        
        self.one_button.grid(row=1, column=1)
        
    def notify_settings_changed(self):
        if self.on_settings_changed:
            self.on_settings_changed(self.settings)
    
    def change_name(self):
        self.settings['Hello World'] = "Ahmed Khaled"
        print(self.settings)
        
        self.notify_settings_changed()