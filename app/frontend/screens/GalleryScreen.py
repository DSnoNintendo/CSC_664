import tkinter as tk
from app.constants import CONFIG_FILE, GALLERY_CARD_SIZE, GALLERY_ROWS, GALLERY_COL
from PIL import ImageTk, Image
from app.frontend.components import ImageViewImage
from app.frontend.frames.gallery import Grid, SortMenu
from app.frontend.windows import ImageView


class GalleryScreen(tk.Frame):
    # This page displays when users first startup program and/or when configurations aren't set
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.sort_menu = SortMenu.SortMenu(self, controller)
        self.canvas = tk.Canvas(self, width=GALLERY_COL*GALLERY_CARD_SIZE, height=GALLERY_ROWS*GALLERY_CARD_SIZE)
        self.grid = Grid.Grid(self, controller)
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

