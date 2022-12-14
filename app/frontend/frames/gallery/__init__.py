import tkinter as tk
from app.constants import CONFIG_FILE
import os
from PIL import ImageTk, Image
from app.frontend.components import GalleryImage

class ScrollableFrame(tk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        canvas = tk.Canvas(self)
        scrollbar = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

class Gallery(ScrollableFrame):
    # This page displays when users first startup program and/or when configurations aren't set
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

    def build(self):
        self.gallery_dir = CONFIG_FILE.get_config('gallery_dir')
        self.images = []
        entries = os.listdir(self.gallery_dir)

        if len(entries):
            img_path = f"{self.gallery_dir}/{entries[0]}"
            img = GalleryImage(img_path)
            self.images.append(img)

            for entry in entries[1:]:
                img_path = f"{self.gallery_dir}/{entry}"

                img = GalleryImage(img_path)
                self.images.append(img)

        if len(self.images):
            self.images.sort()
            self.populate_grid()

    def populate_grid(self):
        nr = 3  # number of rows
        nc = 3  # number of columns
        idx = 0

        photo_list = []

        for i in range(nr * nc):
            try:
                img = ImageTk.PhotoImage(self.images[idx].img)
            except IndexError:
                break
            lbl = tk.Label(self, image=img)
            lbl.img = img
            photo_list.append(lbl)
            photo_list[-1].grid(row=i // nc, column=i % nc)
            idx += 1
