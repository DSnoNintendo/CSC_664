import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from app.backend.helpers import Config
from app.frontend.components import DirectoryDialog
from app.constants import REQUIRED_CONFIGS

LARGEFONT =("Verdana", 35)


class StartPage(tk.Frame):
    # This page displays when users first startup program and/or when configurations aren't set
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.dir_dialog_l = []

    def build(self):
        idx = 0
        for i, s in enumerate(REQUIRED_CONFIGS):
            # Create a dialog component for every required setting
            self.dir_dialog_l.append(DirectoryDialog(row=i, param=s))
            idx += i

        # Build a Confirm button after the last dialogue
        self.dir_dialog_l[-1].build_confirm_button(row=idx + 1, column=3, l=self.dir_dialog_l)
