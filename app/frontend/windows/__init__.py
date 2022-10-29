import tkinter as tk
from app.constants import CONFIG_FILE, GALLERY_CARD_SIZE, GALLERY_ROWS, GALLERY_COL
from PIL import ImageTk, Image
from app.frontend.components import ImageViewImage
from app.frontend.frames.gallery import Grid, SortMenu


class ImageView:
    def __init__(self, parent, img_path):
        img_obj = ImageViewImage(img_path)
        self.top = tk.Toplevel(parent)
        self.top.geometry(f"{img_obj.width}x{img_obj.height}")
        img = ImageTk.PhotoImage(img_obj.img)
        lbl = tk.Label(self.top, image=img)
        lbl.image = img
        lbl.pack()
        self.top.title(img_path)

    def destroy(self):
        self.top.destroy()
        self.top.update()