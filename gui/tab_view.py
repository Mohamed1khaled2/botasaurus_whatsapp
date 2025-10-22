import customtkinter as ctk
from gui.channel_tab import ChannelsTab
from gui.sender_tap import SenderTapWindow
from gui.messages_tab import MessagesTab
from gui.settings_tab import SettingTab

class MyTabView(ctk.CTkTabview):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.channels_tab = self.add("Channels")
        self.sender_tab = self.add("Sender")
        self.messages_tab = self.add("Messages")
        self.settings_tab = self.add("Settings")

        self.channels_view = ChannelsTab(self.channels_tab)
        self.channels_view.pack(fill="both", expand=True)

        self.messages_tab_view = MessagesTab(self.messages_tab)
        self.messages_tab_view.pack(fill="both", expand=True)

        self.settings_view = SettingTab(self.settings_tab)
        self.settings_view.pack(fill="both", expand=True)

        self.sender_tab_view = SenderTapWindow(
            self.sender_tab,
            messages_tab=self.messages_tab_view,
            channels_tab=self.channels_view,
            setting_tab=self.settings_view,
        )
        self.sender_tab_view.pack(fill="both", expand=True)

        # ✅ الربط بين الإعدادات ونافذة الإرسال
        self.settings_view.on_settings_changed = self.sender_tab_view.settings_changed
