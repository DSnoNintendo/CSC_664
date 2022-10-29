import tkinter as tk
from app.constants import GALLERY_COL, MONTH_DICT
from PIL import ImageTk, Image


class MiniGrid(tk.Frame):
    def __init__(self, parent, controller, photos):
        tk.Frame.__init__(self, parent)
        self.photos = photos

    def populate_grid(self):
        nc = GALLERY_COL  # number of columns
        idx = 0

        photo_list = []  # photo labels

        curr_year = self.photos[0].year
        curr_month = self.photos[0].month

        while True:
            try:
                img_obj = self.photos[idx]
                img = ImageTk.PhotoImage(img_obj.img)
            except IndexError:
                break
            lbl = tk.Label(self, image=img)
            lbl.img = img
            photo_list.append(lbl)
            photo_list[-1].grid(row=idx // nc, column=idx % nc, padx=5)  # place last img of list on grid
            idx += 1


class DateMiniGrid(MiniGrid):
    def __init__(self, parent, controller, photos, month, year):
        super().__init__(parent, controller, photos)
        self.year = year
        self.month = month
        tk.Label(self, text=str(self.month))
        tk.Label(self, text=f'{MONTH_DICT[1]}')

    def populate_grid(self):
        nc = GALLERY_COL  # number of columns
        idx = 0

        photo_list = []  # photo labels

        while True:
            try:
                img_obj = self.photos[idx]
                curr_year = img_obj.year
                curr_month = img_obj.month
                img = ImageTk.PhotoImage(img_obj.img)
            except IndexError:
                break
            if curr_year != self.year and curr_month != self.month:
                break
            lbl = tk.Label(self, image=img)
            lbl.img = img
            photo_list.append(lbl)
            photo_list[-1].grid(row=idx // nc, column=idx % nc, padx=5)  # place last img of list on grid
            idx += 1
