import tkinter as tk
import customtkinter as ctk
from PIL import ImageTk, Image
from app.frontend.components import ImageViewImage
from app.constants import IMG_PROP_DIR
from app.helpers import Config
import os

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


class FaceFoundWindow(ctk.CTkToplevel):
    def radio_event(self):
        print(self.radio_var.get())
        if self.radio_var.get() == 0:
            self.radio_btn.deselect()
        if self.radio_var.get() == 1:
            self.radio_btn.select()

    def __init__(self, parent, image):
        ctk.CTkToplevel.__init__(self, parent)
        self.geometry('450x450')
        self.widgets = []
        self.name = None


        l1 = ctk.CTkLabel(self, text='A face in an image that may be associated with your event has been found. Specify '
                                     'or click Skip', wraplength=425, anchor=tk.CENTER)
        l1.grid(row=0, column=0, padx=5, pady=25, sticky='news')
        img = ImageTk.PhotoImage(image)
        image_lbl = ctk.CTkLabel(self, image=img, text='', anchor=tk.CENTER)
        image_lbl.grid(row=1, column=0, padx=5, pady=(0, 25))
        self.name_entry = ctk.CTkEntry(self, placeholder_text="Name")
        self.name_entry.grid(row=3, column=0, padx=5, pady=5)
        self.radio_var = tk.IntVar()
        self.radio_var.set(0)
        self.widgets.append(self.radio_var)
        #self.radio_btn = ctk.CTkCheckBox(self, text='This is me', text_color='white',
        #                                 onvalue=1, offvalue=0, variable=self.radio_var)
        #self.widgets.append(self.radio_btn)
        #self.radio_btn.deselect()
        #self.radio_btn.grid(row=2, column=0, pady=5)
        confirm = ctk.CTkButton(self, text='Confirm', command=lambda: self.confirm())
        confirm.grid(row=4, column=0, sticky='w', padx=(50, 0), pady=(25, 0))
        skip_button = ctk.CTkButton(self, text='Skip', command=lambda: self.skip())
        skip_button.grid(row=4,column=0, sticky='e', padx=(0, 50), pady=(25,0))

    def show(self):
        self.wm_protocol("WM_DELETE_WINDOW", self.destroy)
        self.wait_window()
        return self.name


    def confirm(self):
        self.name = self.name_entry.get()
        if self.name:
            self.destroy()

    def skip(self):
        self.destroy()
