import tkinter as tk
from app.frontend.windows import ImageView
from app.helpers.recognizer import start_facefinder
from app.constants import CONFIG_FILE, GALLERY_CARD_SIZE, GALLERY_ROWS, GALLERY_COL
import os
from PIL import ImageTk, Image
from app.frontend.components import GalleryImage
from app.frontend.frames import SortMenu


class GalleryScreen(tk.Frame):
    # This page displays when users first startup program and/or when configurations aren't set
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.controller = controller
        self.sort_menu = SortMenu(self, controller)
        self.canvas = tk.Canvas(self, width=GALLERY_COL*GALLERY_CARD_SIZE, height=GALLERY_ROWS*GALLERY_CARD_SIZE)
        self.grid = Grid(self, controller)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.grid.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        self.image_thumbnails = []
        self.image_view = None

    def build(self):
        self.grid.build()
        self.grid.pack()
        self.sort_menu.pack(side=tk.LEFT, fill='y')
        self.canvas.pack(side=tk.LEFT, padx=(0, 50))
        self.scrollbar.pack(side=tk.RIGHT, fill='y')
        self.canvas.create_window((0, 0), window=self.grid, anchor="nw")
        thumbnails = self.grid.get_thumbnails()
        images = self.grid.get_images()

        # add command to labels to open imageview on click
        for i, thumbnail in enumerate(thumbnails):
            thumbnail.bind("<Button-1>", lambda e, path=images[i].path: self.open_imageview(path))

    def open_imageview(self, path):
        if self.image_view:
            self.image_view.destroy()

        self.image_view = ImageView(self, path)
    '''
        img_obj = ImageViewImage(path)
        top = tk.Toplevel(self)
        top.geometry(f"{img_obj.width}x{img_obj.height}")
        img = ImageTk.PhotoImage(img_obj.img)
        lbl = tk.Label(top, image=img)
        lbl.image = img
        lbl.pack()
        top.title("Child Window")
        '''

    def menubar(self, root):
        menubar = tk.Menu(root)

        preferences_menu = tk.Menu(menubar, tearoff=0)
        preferences_menu.add_command(label="Start facial recogniton", command=lambda: start_facefinder(self,
                                                                                                       self.controller,
                                                                                                       self.parent))
        menubar.add_cascade(label="Actions"
                                  "", menu=preferences_menu)

        return menubar

class Grid(tk.Frame):
    # This page displays when users first startup program and/or when configurations aren't set
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.images = []  # automatically ordered from old to new
        self.images_new_to_old = []
        self.thumbnails = []  # label objects created from image objects
        self.order = 'Date (New to Old)' # current order of grid

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
            # sort images from oldest to new
            self.images.sort()
            self.images_new_to_old = self.images[::-1]
            self.populate_grid(self.images_new_to_old)

    def populate_grid(self, img_list):
        nc = GALLERY_COL  # number of columns
        idx = 0

        self.thumbnails = []  # photo labels

        while True:
            try:
                img_obj = img_list[idx]
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

    def refresh(self, command):
        if command != self.order:
            for label in self.grid_slaves():
                label.grid_forget()
            self.thumbnails.clear()

            if command == "Date (New to Old)":
                self.populate_grid(self.images_new_to_old)

            elif command == "Date (Old to New)":
                for label in self.grid_slaves():
                    label.grid_forget()
                self.thumbnails.clear()
                self.populate_grid(self.images)

    def get_thumbnails(self):
        return self.thumbnails

    def get_images(self):
        return self.images
