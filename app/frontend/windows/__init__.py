import tkinter as tk
from PIL import ImageTk, Image
from app.frontend.components import ImageViewImage
from app.constants import IMG_PROP_DIR
from app.helpers import Config
import os
from app.frontend.frames.gallery import Grid, SortMenu

'''
Module for popup windows that aren't the main GUI.
'''


class ImageView(tk.Frame):
    class DetailMenu(tk.Frame):
        # This page displays when users first startup program and/or when configurations aren't set
        def __init__(self, parent, prop_file, img_obj):
            tk.Frame.__init__(self, parent)
            self.parent = parent
            self.labels = []
            self.date_created_label = tk.Label(text="Date:")
            self.labels.append(self.date_created_label)
            self.date_created_label2 = tk.Label(text=img_obj.time_created_str)
            self.labels.append(self.date_created_label2)
            self.num_people_label = tk.Label(text="# of people in photo")
            if prop_file.config_exists("num_faces"):
                self.num_people_label2 = tk.Label(text=prop_file.get_config("num_faces"))
            else:
                self.num_people_label2 = tk.Label(text="Unknown")

            self.labels.append(self.num_people_label2)

            if prop_file.config_exists("people_in_photo"):
                people = prop_file.get_config("people_in_photo")
                for person in people:
                    label = tk.Label(text=person)
                    self.label.append(label)

            for l in self.labels:
                l.pack()

    def __init__(self, parent, img_path):
        tk.Frame.__init__(self, parent)
        img_obj = ImageViewImage(img_path)
        self.top = tk.Toplevel(parent)
        self.top.geometry(f"{img_obj.width}x{img_obj.height}")
        prop_file = self.get_or_create_img_props(img_path)
        img = ImageTk.PhotoImage(img_obj.img)
        lbl = tk.Label(self.top, image=img)
        lbl.image = img
        lbl.pack()
        '''
        self.detail_menu = self.DetailMenu(self, prop_file, img_obj)
        self.detail_menu.pack(side=tk.LEFT, fill='y')
        '''
        self.top.title(img_path)

    def get_or_create_img_props(self, path):
        # creates a properties file for an image
        img_filename = path.split('/')[-1]
        config_filename = f'.{os.path.splitext(img_filename)[0]}'
        config_path = f'{IMG_PROP_DIR}/{config_filename}'
        config_file = Config.Config(config_path)
        return config_file

    def destroy(self):
        self.top.destroy()
        self.top.update()


class FaceView:
    def __init__(self, parent, face_img):
        img_obj = ImageViewImage(face_img)
        self.top = tk.Toplevel(parent)
        self.top.geometry(f"{img_obj.width}x{img_obj.height}")
        img = ImageTk.PhotoImage(img_obj.img)
        lbl = tk.Label(self.top, image=img)
        lbl.image = img
        lbl.pack()
        self.top.title('Face detected')

    def destroy(self):
        self.top.destroy()
        self.top.update()
