import tkinter as tk
from app.constants import CONFIG_FILE, GALLERY_CARD_SIZE, GALLERY_ROWS, GALLERY_COL
import os
from PIL import ImageTk, Image
from app.frontend.components import GalleryImage


class SortMenu(tk.Frame):
    # This page displays when users first startup program and/or when configurations aren't set
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        sort_by_lbl = tk.Label(self, text="Sort By:")
        listbox = tk.Listbox(self, height=10,
                             width=15,
                             bg="grey",
                             activestyle='dotbox',
                             font="Helvetica",
                             fg="black")
        listbox.insert(1, "Date")
        sort_by_lbl.pack()
        listbox.pack()
        listbox.bind('<<ListboxSelect>>', self.onselect)
        self.config(width=GALLERY_CARD_SIZE * GALLERY_ROWS * 0.25, bg='grey')

    def onselect(self, evt):
        w = evt.widget
        index = int(w.curselection()[0])
        value = w.get(index)

