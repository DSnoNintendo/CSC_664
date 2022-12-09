import tkinter as tk
from tkinter import ttk
from .screens import screen_list, start_screen, gallery_screen, calendar_screen
from app.constants import REQUIRED_CONFIGS, CONFIG_FILE
from app.helpers import make_label

LARGEFONT =("Verdana", 35)


class GUI(tk.Tk):
    # start app
    def __init__(self, *args, **kwargs):
        # __init__ function for class Tk
        tk.Tk.__init__(self, *args, **kwargs)
        s = ttk.Style()
        s.theme_use('classic')

        # creating a container
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)

        container.pack()

        # frame map
        self.frames = {}

        # iterating through a tuple consisting
        # of the different page layouts
        for F in screen_list:
            # create screen; App.container is parent. App is controller
            frame = F(container, self)

            # initializing frame of that object from
            # for loop
            self.frames[F] = frame

            frame.pack()

        if CONFIG_FILE.has_required_configs(REQUIRED_CONFIGS):
            print('available')
            self.show_frame(calendar_screen)
        else:

            self.show_frame(start_screen)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.build()
        frame.tkraise()
        try:
            print('showing frame')
            menubar = frame.menubar(self)
            self.configure(menu=menubar)
        except Exception as e:
            print(e)
            pass

    def refresh(self):
        self.root.update()
        self.root.after(1000, self.refresh)
