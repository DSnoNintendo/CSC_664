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


class DirectoryDialog(tk.Frame):
    # *args and **kwargs required for components
    def __init__(self, param, row, parent):
        tk.Frame.__init__(self, parent)
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

        self.setting_label = ctk.CTkLabel(self, text=f"{param}:")
        self.setting_label.grid(row=row, column=1)

        self.browse_button = ctk.CTkButton(self, text="Browse", command=self.browse)
        self.browse_button.grid(row=row, column=2)

        self.dir_label = tk.Label(self, text=" ")
        self.dir_label.grid(row=row, column=3)

    def browse(self):
        # Allow user to select a directory and store it in global var
        # called folder_path
        filename = filedialog.askdirectory()
        self.folder_path.set(filename)
        self.dir_label.config(text=f"{filename}")

    def confirm(self):
        """
        :return: True if param is correctly written to config file
        """
        for d in self.dir_dialog_l:
            if os.path.exists(d.folder_path.get()):
                CONFIG_FILE.set_config(d.param, d.folder_path.get())
                print(CONFIG_FILE.get_config('gallery_dir'))
                return True
            return False

    def build_confirm_button(self, row, column, l):
        confirm_button = tk.Button(self, text="Confirm", command=self.confirm)
        self.dir_dialog_l = l
        confirm_button.grid(row=row, column=column)

class MenuBar:
    def __init__(self, root):
        menu_bar = tk.Menu(root)

