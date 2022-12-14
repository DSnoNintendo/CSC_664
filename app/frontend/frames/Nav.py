import tkinter as tk
from tkinter import ttk
from app.constants import WINDOW_WIDTH


class Nav(ttk.Frame):
    def __init__(self, parent, controller):
        # PARENT - CALENDAR SCREEN
        self.parent = parent
        self.controller = controller
        ttk.Frame.__init__(self, parent, width=WINDOW_WIDTH, style="Nav.TFrame")
        self.container = parent.event_view
        self.view_button = tk.Button(self, text="□", command=lambda: self.change_view())
        self.add_event_button = tk.Button(self, text="+", command=lambda: self.new_event())

    def build(self):
        self.view_button.pack(side=tk.LEFT)
        self.add_event_button.pack(side=tk.LEFT)
        # self.calendar_button.pack(side=tk.LEFT)

    def change_view(self):
        if self.view_button.cget('text') == "□":
            self.container.show_calendar()
            self.view_button["text"] = "≡"

        elif self.view_button.cget('text') == "≡":
            self.container.show_list_view()
            self.view_button["text"] = "□"


