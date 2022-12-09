import tkinter as tk
from app.constants import CONFIG_FILE, GALLERY_CARD_SIZE, GALLERY_ROWS, GALLERY_COL
import os
from PIL import ImageTk, Image
from app.frontend.components import GalleryImage


class Grid(tk.Frame):
    # This page displays when users first startup program and/or when configurations aren't set
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.images = []  # image objects from frontend.components.GalleryImage
        self.thumbnails = []  # label objects created from image objects

    def build(self):
        gallery_dir = CONFIG_FILE.get_config('gallery_dir')
        entries = os.listdir(gallery_dir)
        for entry in entries:
            if 'props' in entry or entry == '.DS_Store':
                entries.remove(entry)

        if len(entries):
            img_path = f"{gallery_dir}/{entries[0]}"
            img = GalleryImage(img_path)
            self.images.append(img)

            for entry in entries[1:]:
                if 'props' in entry or entry == '.DS_Store':
                    continue
                img_path = f"{gallery_dir}/{entry}"
                img = GalleryImage(img_path)
                self.images.append(img)

        if len(self.images):
            # sort images from newest to oldest
            self.images.sort()
            self.populate_grid()

    def populate_grid(self):
        nc = GALLERY_COL  # number of columns
        idx = 0

        self.thumbnails = []  # photo labels

        while True:
            try:
                img_obj = self.images[idx]
                img = ImageTk.PhotoImage(img_obj.img)
            except IndexError:
                # in case images list empty
                break
            # create label using img obj image
            lbl = tk.Label(self, image=img)
            lbl.img = img
            lbl.grid(row=idx // nc, column=idx % nc, padx=5)  # place image in grid
            # add onclick listeners to each thumbnail to open full image

            self.thumbnails.append(lbl)
            idx += 1

        # Display

    def get_thumbnails(self):
        return self.thumbnails

    def get_images(self):
        return self.images
