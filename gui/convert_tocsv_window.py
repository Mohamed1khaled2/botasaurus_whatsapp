import customtkinter
import os
from CTkMessagebox import CTkMessagebox
import winsound
from convert_txt_tocsv import converter


class ConvertorGUI(customtkinter.CTkToplevel):
    def __init__(self, parent, icon_path, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.converter = converter

        self.title("Convert App")
        print(icon_path)
        if os.path.exists(icon_path):
            self.iconbitmap(icon_path)

        self.geometry("600x500")
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure((0, 1, 2, 3), weight=1)

        self.title_label = customtkinter.CTkLabel(
            self, text="Convert TXT → CSV", font=("Arial", 28, "bold")
        )
        self.title_label.grid(row=0, column=0, columnspan=2, pady=10)

        self.name_file_label = customtkinter.CTkLabel(
            self, text="NameFile", font=("arial", 32)
        )
        self.name_file_label.grid(row=1, column=0, columnspan=2)
        #! debug
        # self.open_file_location_btn = customtkinter.CTkButton(
        #     self, text="Open File Location", font=("arial", 32), command=self.open_file_location)

        self.select_file_btn = customtkinter.CTkButton(
            self, text="Select Text File", command=self.open_file
        )
        self.select_file_btn.grid(row=2, column=0, padx=20, pady=20,
                                  columnspan=2)

        self.convert_btn = customtkinter.CTkButton(
            self, text="Convert", font=("arial", 32), command=self.convert_fun
        )

    #! debug
    # def open_file_location(self):
    #     import subprocess

    #     folder_path = r"{}".format('/'.join(self.file_path.split('/')[:-2]))
    #     if os.path.exists(folder_path):
    #         subprocess.Popen(f'explorer "{folder_path}"')
    #     else:
    #         print("❌ الملف غير موجود")
    
    
    def open_file(self):

        self.file_path = customtkinter.filedialog.askopenfilename()
        self.name_file = self.file_path.split("/")[-1]

        if self.name_file.find(".txt") != -1:
            self.name_file_label.configure(
                text=self.name_file, text_color="black")
            self.convert_btn.grid(
                row=3, column=0, padx=20, pady=20, sticky="ew", columnspan=2
            )
            self.convert_btn.configure(fg_color="green")
        else:
            self.name_file_label.configure(
                text="Your Choose Wrong File,\n please check extension of file is txt",
                text_color="red",
                font=("arial", 24),
            )
            self.convert_btn.grid_forget()

        self.select_file_btn.configure(text='Re-select File')

    def convert_fun(self):

        self.path = self.file_path.split("/")[:-1]  # path of file

        # list of all file in path
        self.all_files = os.listdir("\\".join(self.path))

        self.csv_path = os.path.splitext(self.file_path)[0] + ".csv"

        if self.csv_path.split('/')[-1] in self.all_files:
            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
            CTkMessagebox(
                title="Error", message="This File Converted Before", icon="cancel"
            )
        else:

            self.save_as = self.converter.create_csv_file(self.file_path)
            print(self.save_as)
            if self.save_as:
                self.name_file_label.configure(
                    text=f"✅ File created successfully!\nSaved as: {os.path.basename(self.save_as)}",
                    text_color="green",
                )


    def _open_folder(self):
        import subprocess
        folder_path = r"C:\Users\YourUser\Downloads"  # مسار المجلد
        if os.path.exists(folder_path):
            subprocess.Popen(f'explorer "{folder_path}"')
        else:
            print("❌ المجلد غير موجود")
