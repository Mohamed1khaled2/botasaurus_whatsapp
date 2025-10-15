import customtkinter as ctk
from gui.view_tree_data import ModernCTkTable


class SenderTapWindow(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        
        # buttons:
            # stop
            # run
            # import Numbers
        
        self.columnconfigure((0,1,2), weight=1)
        self.rowconfigure((0), weight=1)
        self.rowconfigure((1), weight=2)
        self.rowconfigure((2), weight=1)
        
        self.count_numbers_sent_it = ctk.CTkLabel(self, text="Sent: ", bg_color='green',corner_radius=20,font=('arial', 20, 'bold'))
        self.count_numbers_sent_it.grid(row=0, column=0 , columnspan=2)
        self.count_numbers_no_phone = ctk.CTkLabel(self, text="No Phone: ", bg_color='gray',corner_radius=20,font=('arial', 20, 'bold'))
        self.count_numbers_no_phone.grid(row=0, column=1 , columnspan=2)
        
        
        # table
        header = ["Send To", "Send From" ]
        self.data = []
        
        self.view_tree_results = ModernCTkTable(self, headers=header, data=self.data, checked_column=False)
        self.view_tree_results.grid(row=1, column=0, columnspan=3, sticky='nsew')
        
        # button
            # run
            # import numbers
            
        self.run_btn = ctk.CTkButton(self, text="Run Sending 🚀")
        self.run_btn.grid(row=2, column=0)
        self.import_numbers_btn = ctk.CTkButton(self, text="Import Numbers", command=self.import_numbers_fun)
        self.import_numbers_btn.grid(row=2, column=2)
        
        
    def import_numbers_fun(self):
        file_num = ctk.filedialog.askopenfile()
        for num in file_num:
            self.data.append([num.replace('\n', ''), ''])
        
        self.view_tree_results.add_data(self.data)
        
        