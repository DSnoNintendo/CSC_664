import tkinter as tk
from tkinter import ttk
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
        container = ctk.CTkFrame(self)
        container.pack(side="top", fill="both", expand=True)

        container.pack()

        # frame map
        self.frames = {}
        self.curr_frame = None

        home_screen = HomeScreen
        set_config = SetConfig
        self.screen_list = []
        self.screen_list.append(home_screen)
        self.screen_list.append(set_config)

        # iterating through a tuple consisting
        # of the different page layouts
        for F in self.screen_list:
            # create screen; App.container is parent. App is controller
            frame = F(container, self)

            # initializing frame of that object from
            # for loop
            self.frames[F] = frame


        if CONFIG_FILE.has_required_configs(REQUIRED_CONFIGS):
            self.show_frame(home_screen)
        else:
            self.show_frame(set_config)

    def show_frame(self, cont):
        self.curr_frame = self.frames[cont]
        self.curr_frame.pack()
        self.curr_frame.build()
        self.curr_frame.tkraise()
        try:
            print('showing frame')
            menubar = self.curr_frame.menubar(self)
            self.configure(menu=menubar)
        except Exception as e:
            print(e)
            pass

    def show_mainframeframe(self):
        self.curr_frame.lower()
        self.curr_frame = self.frames[self.screen_list[0]]
        self.curr_frame.build()
        self.curr_frame.tkraise()
        try:
            print('showing frame')
            menubar = self.curr_frame.menubar(self)
            self.configure(menu=menubar)
        except Exception as e:
            print(e)
            pass

    def refresh(self):
        self.root.update()
        self.root.after(1000, self.refresh)
