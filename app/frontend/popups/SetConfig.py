import tkinter as tk
import customtkinter as ctk
from app.frontend.components import DirectoryDialog
from app.constants import REQUIRED_CONFIGS

LARGEFONT =("Verdana", 35)


class SetConfig(ctk.CTkFrame):
    # This page displays when users first startup program and/or when configurations aren't set
    def __init__(self, parent, controller):
        ctk.CTkFrame.__init__(self, parent, width=300, height=300)

        self.dir_dialog_l = []

    def build(self):
        idx = 0
        for i, s in enumerate(REQUIRED_CONFIGS):
            # Create a dialog component for every required setting
            ddl = DirectoryDialog(row=i, param=s, parent=self)
            self.dir_dialog_l.append(ddl)
            ddl.pack()
            idx += i

        # Build a Confirm button after the last dialogue, and pass all earlier dialogues to the confirm button
        self.dir_dialog_l[-1].build_confirm_button(row=idx + 1, column=3, l=self.dir_dialog_l)

    def menubar(self, root):
        menubar = tk.Menu(root)

        preferences_menu = tk.Menu(menubar, tearoff=0)
        preferences_menu.add_command(label="Start facial recogniton", command=self.bind())
        menubar.add_cascade(label="PageOne", menu=preferences_menu)
        return menubar