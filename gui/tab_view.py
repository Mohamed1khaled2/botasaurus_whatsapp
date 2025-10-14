import customtkinter as ctk
from gui.channel_tab import ChannelsTab


# ======================================================
# 🧩 التبويبات الرئيسية
# ======================================================
class MyTabView(ctk.CTkTabview):
    """واجهة التبويبات الرئيسية"""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.channels_tab = self.add("Channels")
        self.sender_tab = self.add("Sender")
        self.messages_tab = self.add("Messages")

        self.channels_view = ChannelsTab(self.channels_tab)
        self.channels_view.pack(fill="both", expand=True)