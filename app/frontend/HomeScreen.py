from tkinter import ttk, PhotoImage
import tkinter as tk
import customtkinter as ctk
from app.constants import WINDOW_HEIGHT
from app.backend.db_adapter import Adapter
from app.frontend.helpers import configure_style
from app.frontend.frames import Nav, SortMenu, EventView, NewEventView
import app.frontend.constants as const

adapter = Adapter()
adapter.get_all_encodings()


class HomeScreen(ttk.Frame):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent, style="EventView.TFrame")
        self.style = ttk.Style(self)
        self.tabview = ctk.CTkTabview(self, width=const.LISTVIEW_ROW_WIDTH, height=const.LISTVIEW_ROW_WIDTH * .8)
        self.tabview.add("Events")
        self.tabview.add("New Event")
        self.event_view = EventView(self.tabview.tab("Events"), self)  # contains event view
        self.new_event_view = NewEventView(self.tabview.tab("New Event"), self)
        #self.new_event_view = NewEventView(self, parent)
        self.nav = Nav(self, parent)

    def change_tabview_tab_color(self, tab, color):
        self.tabview._segmented_button._buttons_dict[tab].configure(fg_color=color)

    def build(self):
        self.nav.build()
        self.event_view.build()
        self.nav.grid(row=0, column=0, sticky='nswe', columnspan=2)
        self.tabview.grid(row=1, column=0, columnspan=2)
        self.new_event_view.grid(row=0, column=0, columnspan=2, pady=(5, 0), sticky='nwe')

        configure_style(self)

    def switch_tab_view(self, name):
        self.event_view.list_view.refresh()
        self.tabview.set(name)



    def menubar(self, root):
        return "f"
