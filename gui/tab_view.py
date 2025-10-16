import customtkinter as ctk
from gui.channel_tab import ChannelsTab
from gui.sender_tap import SenderTapWindow
from gui.messages_tab import MessagesTab

class MyTabView(ctk.CTkTabview):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # 🧩 إنشاء التبويبات
        self.channels_tab = self.add("Channels")
        self.sender_tab = self.add("Sender")
        self.messages_tab = self.add("Messages")

        # 📱 القنوات
        self.channels_view = ChannelsTab(self.channels_tab)
        self.channels_view.pack(fill="both", expand=True)

        # 💬 الرسائل
        self.messages_tab_view = MessagesTab(self.messages_tab)
        self.messages_tab_view.pack(fill="both", expand=True)

        # 🚀 الإرسال
        self.sender_tab_view = SenderTapWindow(
            self.sender_tab,
            messages_tab=self.messages_tab_view,
            channels_tab=self.channels_view
        )
        self.sender_tab_view.pack(fill="both", expand=True)
