import customtkinter as ctk
from gui.channel_tab import ChannelsTab
from gui.sender_tap import SenderTapWindow
from gui.messages_tab import MessagesTab


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
        
        self.sender_tab_view = SenderTapWindow(self.sender_tab)
        self.sender_tab_view.pack(fill='both', expand=True)
        
        self.messages_tab_view = MessagesTab(self.messages_tab)
        self.messages_tab_view.pack(fill='both', expand=True)