import tkinter as tk
from tkinter import ttk
from .screens import screen_list, start_screen, gallery_screen, calendar_screen
from app.constants import REQUIRED_CONFIGS, CONFIG_FILE
from app.helpers import make_label
from .HomeScreen import HomeScreen
from .popups import SetConfig
import customtkinter as ctk

LARGEFONT =("Verdana", 35)


class GUI(ctk.CTk):
    # start app
    def __init__(self, *args, **kwargs):
        # __init__ function for class Tk
        ctk.CTk.__init__(self, *args, **kwargs)
        s = ttk.Style()

        #s.theme_use('classic')
        ctk.set_appearance_mode("dark")
        self.title("Event Grouper")

        # creating a container
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)

        container.pack()

        # frame map
        self.frames = {}

        home_screen = HomeScreen
        set_config = SetConfig
        screen_list.append(home_screen)
        screen_list.append(set_config)

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
            self.show_frame(home_screen)
        else:
            self.show_frame(set_config)

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
