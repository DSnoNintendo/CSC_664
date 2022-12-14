from PIL import Image
from app.constants import CONFIG_FILE
import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog
import os
from app.constants import GALLERY_CARD_SIZE
from datetime import datetime
from .ListView import TableHeader


class GalleryImage:
    def __init__(self, path):
        self.path = path
        self.img = Image.open(self.path)
        self.height = self.img.height
        self.width = self.img.width
        self.format = self.img.format
        self.img.thumbnail((GALLERY_CARD_SIZE, GALLERY_CARD_SIZE))
        try:
            self.time_created_str = self.img._getexif()[36867]
        except (KeyError, TypeError):
            self.time_created_str = datetime.today().isoformat("/")
        self.year = int(self.time_created_str[0:4])
        self.month = int(self.time_created_str[5:7])
        self.day = int(self.time_created_str[8:10])
        self.hour = int(self.time_created_str[11:13])
        self.minute = int(self.time_created_str[14:16])

    def __lt__(self, other):
        return self.time_created_str < other.time_created_str

    def __str__(self):
        return self.path

    def get_time_created(self):
        return self.time_created_str


class ImageViewImage:
    def __init__(self, path):
        self.path = path
        self.img = Image.open(self.path)
        self.height = self.img.height
        self.width = self.img.width
        self.format = self.img.format
        try:
            self.time_created_str = self.img._getexif()[36867]
        except TypeError:
            self.time_created_str = datetime.today().isoformat("/")
        self.year = int(self.time_created_str[0:4])
        self.month = int(self.time_created_str[5:7])
        self.day = int(self.time_created_str[8:10])
        self.hour = int(self.time_created_str[11:13])
        self.minute = int(self.time_created_str[14:16])


class DirectoryDialog(ctk.CTkFrame):
    # *args and **kwargs required for components
    def __init__(self, param, row, parent, controller):
        ctk.CTkFrame.__init__(self, parent, fg_color='#333333')
        self.controller = controller
        """
        Creates dialog for users to select directory

            Parameters:
                    param (string): The setting of the configuration file, being changed
                    row (int): row of GUI grid that component will be placed at
                    has_confirm (bool): If True, creates a confirm button for the dialog

            Returns:
                    binary_sum (str): Binary string of the sum of a and b
        """
        self.param = param
        self.folder_path = tk.StringVar()
        self.dir_dialog_l = []

        if param == 'gallery_dir':
            lbl_txt = 'Gallery Directory'
        elif param == 'document_dir':
            lbl_txt = 'Text Document Directory'
        elif param == 'music_dir':
            lbl_txt = 'Music Directory'

        self.setting_label = ctk.CTkLabel(self, text=f"{lbl_txt}:")
        self.setting_label.grid(row=1, column=1, sticky='e', padx=(10, 0))

        self.browse_button = ctk.CTkButton(self, text="Browse", command=self.browse)
        self.browse_button.grid(row=1, column=2, sticky='e')

        self.dir_label = ctk.CTkLabel(self, text=" ", wraplength=300)
        self.dir_label.grid(row=1, column=3, columnspan=2, sticky='w', padx=(10, 0))

        for i in range(1, 4):
            self.columnconfigure(i, minsize=150)

        self.columnconfigure(4, minsize=200)

    def browse(self):
        # Allow user to select a directory and store it in global var
        # called folder_path
        path = filedialog.askdirectory()
        self.folder_path.set(str(path))
        self.dir_label.configure(text=f"{path}")

    def confirm(self):
        """
        :return: True if param is correctly written to config file
        """
        for d in self.dir_dialog_l:
            if os.path.exists(d.folder_path.get()):
                CONFIG_FILE.set_config(d.param, d.folder_path.get())
        self.controller.show_mainframeframe()
        self.destroy()





    def build_confirm_button(self, row, column, l):
        confirm_button = ctk.CTkButton(self, text="Confirm", command=lambda: self.confirm())
        self.dir_dialog_l = l
        confirm_button.grid(row=row, column=column, pady=25, sticky='e', padx=(0, 10))

class MenuBar:
    def __init__(self, root):
        menu_bar = tk.Menu(root)

