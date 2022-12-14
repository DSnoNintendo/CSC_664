import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from app.frontend.components.Calendar import Calendar
from app.frontend.components.ListView import ListView, TableHeader

class EventView(ttk.Frame):
    def __init__(self, parent, controller):
        self.parent = parent
        ttk.Frame.__init__(self, parent)
        self.calendar = Calendar(self, parent)
        self.sort_combobox = ctk.CTkComboBox(parent,
                                             values=["Event Date: New to Old", "Event Date: Old to New",
                                                                               "Creation Date: New to Old",
                                                                               "Creation Date: Old to New"])

        self.search_bar = ctk.CTkEntry(parent, placeholder_text="Search")
        self.table_header = TableHeader(parent)
        self.list_view = ListView(parent, controller)

    def build(self):
        self.sort_combobox.grid(row=1, column=0, sticky='w', padx=(6, 0), pady=(6, 25))
        self.search_bar.grid(row=1, column=1, sticky='e', padx=(0, 6), pady=(6, 25))
        self.table_header.grid(row=2, column=0, columnspan=2, padx=(6, 0))
        self.list_view.grid(row=3, column=0, columnspan=2)


    def show_calendar(self):
        self.list_view.pack_forget()
        self.calendar.pack()

    def show_list_view(self):
        self.calendar.pack_forget()
        self.list_view.refresh()
        self.list_view.pack()