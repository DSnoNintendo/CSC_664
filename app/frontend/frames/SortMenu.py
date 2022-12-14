import tkinter as tk
from tkinter import ttk
from app.constants import CONFIG_FILE, GALLERY_CARD_SIZE, GALLERY_ROWS, GALLERY_COL
import os
from PIL import ImageTk, Image
from app.frontend.components import GalleryImage
from app.backend.db_adapter import Adapter
from app.constants import WINDOW_WIDTH
from app.frontend.constants import SORT_MENU_WIDTH

adapter = Adapter()
adapter.get_all_encodings()

class SortMenu(ttk.Frame):
    class DateListBox(ttk.Frame):
        def __init__(self, parent):
            def on_click(event):
                selection = event.widget.curselection()
                if selection:
                    index = selection[0]
                    data = event.widget.get(index)
                    #self.event_view.refresh(data)

            ttk.Frame.__init__(self, parent)
            self.listbox = tk.Listbox(self, height=4,
                                      width=15,
                                      bg="grey",
                                      activestyle='dotbox',
                                      font="Helvetica",
                                      fg="black")
            self.listbox.grid(row=0,column=0)
            self.listbox.insert(0, "Event: New to Old")
            self.listbox.insert(1, "Event: Old to New")
            self.listbox.insert(2, "Creation: Old to New")
            self.listbox.insert(3, "Creation: New to Old")
            self.listbox.selection_set(0)
            self.listbox.bind('<<ListboxSelect>>', on_click)
            # self.event_view = parent.parent.event_view

    class PeopleListBox(ttk.Frame):
        def __init__(self, parent):
            def on_click(event):
                selection = event.widget.curselection()
                if selection:
                    index = selection[0]
                    data = event.widget.get(index)
                    #self.event_view.refresh(data)

            def get_events():
                events = adapter.get_all_events()
                people = []
                for e in events:
                    try:
                        p = e['people']
                        if p in people:
                            continue
                        people.append(p)
                    except KeyError:
                        pass
                return people

            ttk.Frame.__init__(self, parent)
            self.listbox = tk.Listbox(self, height=2,
                                      width=15,
                                      bg="grey",
                                      activestyle='dotbox',
                                      font="Helvetica",
                                      fg="black")
            self.listbox.grid(row=0,column=0)
            people_list = get_events()
            if len(people_list):
                for i, person in enumerate(people_list):
                    self.listbox.insert(i, person)
            else:
                self.listbox.insert(0, "No people detected")

            self.listbox.bind('<<ListboxSelect>>', on_click)


            # self.event_view = parent.parent.event_view


    class SortContainer(ttk.Frame):
        def __init__(self, parent, controller):
            ttk.Frame.__init__(self, parent)
            event_date_lbl = tk.Label(self, text="Date:")
            event_date_lbl.grid(row=1, column=0)
            event_date_listbox = parent.DateListBox(self)
            event_date_listbox.grid(row=2, column=0, sticky="nswe")
            people_lbl = tk.Label(self, text="People:")
            people_lbl.grid(row=5, column=0)
            people_listbox = parent.PeopleListBox(self)
            people_listbox.grid(row=6, column=0)


    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.width = SORT_MENU_WIDTH
        sort_by_lbl = tk.Label(self, text="Sort By:", font='underline')
        sort_by_lbl.grid(row=0, column=0, sticky="n")
        date_sortbox = self.SortContainer(self, parent)
        date_sortbox.grid(row=1, column=0, pady=(5, 0))
