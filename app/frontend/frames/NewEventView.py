import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
import datetime
import tkcalendar
from app.FileFinder import start_filefinder
from app.helpers import get_unique
import threading
from PIL import Image, ImageTk
from itertools import count, cycle
from app.constants import CWD, MUSIC_DIR, WINDOW_HEIGHT, WINDOW_WIDTH
import app.frontend.constants as const
from app.utils.image import decode_heic
from pathlib import Path
import subprocess, os, platform
from app.backend.db_adapter import Adapter

adapter = Adapter()

class NewEventView(ctk.CTkFrame):
    def handle_entry_click(self, event):
        self.descr_entry.configure(textvariable=self.descr_sv)
        self.descr_sv.set(self.descr_entry.get())
        print(self.descr_sv.get())

    def trace_entry(self):
        print('tracing')
        self.descr_sv.trace("w", lambda name, index, mode, sv=self.descr_sv: self.reset_confirm_btn())
        print(self.descr_sv.get())

    def reset_confirm_btn(self):
        print('resetting')
        self.confirm_button.configure(fg_color='#206AA5', hover='#144870', text='Confirm',
                                      command=lambda: self.param_view.start_analysis_thread())
        self.param_view.remove_widgets()

    def start_event_creation(self):
        # hide widgets
        event_props = dict()
        event_props['description'] = self.descr_entry.get()
        event_props['date'] = self.date_calendar.get_date()
        event_props['location'] = self.param_view.get_location()
        event_props['people'] = self.param_view.get_people()
        start_filefinder(self, self.parent, event_props)
        self.pack_propagate(0)
        self.display_loading()

    def display_loading(self):
        self.destroy_all_widgets()
        loading_img = ImageLabel(self)
        loading_img.load(f'{CWD}/images/src/loading.gif')
        loading_img.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        self.loading_label = tk.Label(self, text="Searching for media associated with event...")
        self.loading_label.place(relx=0.5, rely=0.5 + self.loading_label.winfo_height() / 3, anchor=tk.CENTER)

    def display_event_files(self, event_files, event_props):
        def cancel():
            self.display_new_event_form()

        def confirm():
            event_files_final = images_view.get_paths() + file_view.get_paths()
            self.event_dict['files'] = event_files_final
            self.event_dict['created'] = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
            adapter.commit_event(self.event_dict)
            self.controller.switch_tab_view('Events')
            self.display_new_event_form()


        self.destroy_all_widgets()
        self.event_dict = event_props
        image_files = event_files['Image']
        text_files = event_files['Text']
        mp3_files = event_files['MP3']
        img_lbl = ctk.CTkLabel(self, text="Event Images:", font=('helvetica', 16))
        img_lbl.pack(pady=25)
        if image_files:
            images_view = EventImages(self, image_files)
            images_view.pack()

        other_files_lbl = ctk.CTkLabel(self, text='Other Event Files:', font=('helvetica', 16))
        other_files_lbl.pack(pady=25)

        file_view = EventFiles(self, text_files)
        file_view.pack()

        confirm_button = ctk.CTkButton(self, text='Confirm', command=lambda: confirm())
        confirm_button.pack()

        cancel_button = ctk.CTkButton(self, text='Cancel', command=lambda: cancel())
        cancel_button.pack()

    def display_new_event_form(self):
        self.destroy_all_widgets()
        self.today = datetime.datetime.today()
        self.placeholder = ctk.CTkLabel(self, text='', width=const.LISTVIEW_ROW_WIDTH - 45)
        self.placeholder.pack(padx=(0, 5))
        self.descr_sv = tk.StringVar(self)
        self.descr_entry = ctk.CTkEntry(self,
                                        width=const.LISTVIEW_ROW_WIDTH - 100)
        self.descr_entry.configure(placeholder_text="Event Description (capitalize cities, states. countries "
                                                    "& peoples' names)")
        self.descr_entry.pack()
        self.descr_entry.bind('<1>', self.handle_entry_click)
        self.date_lbl = ctk.CTkLabel(self, text="Event Date:", font=('helvetica', 16))
        self.date_lbl.pack(pady=(45, 0))
        self.date_calendar = Calendar(self)
        self.date_calendar.pack(pady=(5, 0))
        self.confirm_button = ctk.CTkButton(self, text='Confirm',
                                            command=lambda: self.param_view.start_analysis_thread())
        self.confirm_button.pack(pady=(25, 0))
        self.param_view = self.EventParams(self)
        self.param_view.pack(pady=(25))

    def destroy_all_widgets(self):
        for widget in self.winfo_children():
            widget.destroy()

    def __init__(self, parent, controller):
        ctk.CTkFrame.__init__(self, parent)
        self.parent = parent
        self.controller = controller
        self.display_new_event_form()
        '''
        def after_event_creation(self, events_props):
            # After event is created, destroy this window and navigate to month of event on Calendar
            # NAV -> SCREEN -> CONTAINER -> SET VIEW -> DATE
            view_container = self.parent.parent.event_view
            # view_container.show_calendar()
            view_container.list_view.refresh()
            view_container.show_list_view()

            # view_container.calendar.calendar_nav.set_month(events_props['date'])
            self.destroy()
            '''

    class EventParams(tk.Frame):
        def __init__(self, parent):
            tk.Frame.__init__(self, parent, bg='#333333')
            self.parent = parent
            self.name_label = ctk.CTkLabel(self, text='People Detected:', anchor='w')
            self.location_label = ctk.CTkLabel(self, text='Place Detected:', anchor='w')
            self.buttons = []
            self.location = []
            self.people = []

        def start_analysis_thread(self):
            print('starting analysis')
            #t = threading.Thread(target=lambda: self.analyze(self.parent.descr_entry.get()))
            t = threading.Thread(target=lambda: self.analyze(self.parent.descr_entry.get()))

            self.parent.confirm_button.configure(text='...', state='disabled')

            t.start()

        def analyze(self, s):
            dict = get_unique(s)
            people = dict['people']
            location = dict['location']
            if len(people):
                self.create_name_lbl(people)
                for person in people:
                    self.people.append(person)

                print(self.people)

            if len(location):
                print(location)
                self.create_location_lbl(location)
                self.location = location

            self.parent.confirm_button.configure(text='Create Event', state='normal', fg_color='#6A8759',
                                                 hover_color='#addc91', command=lambda: self.parent.start_event_creation())
            self.parent.trace_entry()

        def remove_widgets(self):
            self.name_label.grid_remove()
            self.location_label.grid_remove()
            for button in self.buttons:
                button.destroy()
                self.buttons.remove(button)

        def create_name_lbl(self, l):
            self.name_label.grid(row=0, column=0, sticky='w')
            col = 1
            for i, name in enumerate(l):
                name_btn = ctk.CTkButton(self, text=name)
                name_btn.grid(row=0, column=col, ipady=0, ipadx=0, pady=0, padx=0)
                col += 1
                self.buttons.append(name_btn)


        def create_location_lbl(self, loc):
            self.location_label.grid(row=1, column=0, sticky='w')
            col = 1
            location_btn = ctk.CTkButton(self, text=loc, hover_color='#e83120')
            location_btn.grid(row=1, column=col, ipady=0, ipadx=0, pady=(5, 0), padx=0)
            self.buttons.append(location_btn)
            self.location = loc

        def get_location(self):
            return self.location

        def get_people(self):
            return self.people

class EventImages(ctk.CTkFrame):
    def __init__(self, parent, paths):
        ctk.CTkFrame.__init__(self, parent)
        self.paths = paths
        COLUMNS = 3
        image_count = 0
        for path in paths:
            image_count += 1
            r, c = divmod(image_count - 1, COLUMNS)
            img = self.EventImage(self, path)
            img.grid(row=r, column=c, padx=25, pady=25)

    def get_paths(self):
        return self.paths

    class EventImage(tk.Label):
        def __init__(self, parent, path):
            self.parent = parent
            self.path = path
            if Path(path).suffix == '.heic':
                im = decode_heic(path)
            else:
                im = Image.open(path)
            im.thumbnail((200, 200))
            tkimage = ImageTk.PhotoImage(im)
            tk.Label.__init__(self, parent, image=tkimage, bg='#2B2B2B')
            self.image = tkimage
            self.bind("<Button-1>", lambda e: self.delete())
            self.bind("<Enter>", lambda e: self.change_highlight())
            self.bind("<Leave>", lambda e: self.revert_highlight())

        def delete(self):
            self.parent.paths.remove(self.path)
            self.destroy()

        def change_highlight(self):
            self.configure(bg='red')
            print('hi')

        def revert_highlight(self):
            self.configure(bg='#2B2B2B')

class EventFiles(ctk.CTkFrame):
    def __init__(self, parent, paths):
        ctk.CTkFrame.__init__(self, parent)
        self.paths = paths
        self.listbox = tk.Listbox(self, width=50, height=5)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH)
        self.scrollbar = tk.Scrollbar(self)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.BOTH)
        for values in range(100):
            self.listbox.insert(tk.END, values)

        # Attaching Listbox to Scrollbar
        # Since we need to have a vertical
        # scroll we use yscrollcommand
        self.listbox.config(yscrollcommand=self.scrollbar.set)

        # setting scrollbar command parameter
        # to listbox.yview method its yview because
        # we need to have a vertical view
        self.scrollbar.configure(command=self.listbox.yview)

        #for i, path in enumerate(paths):
            #self.listbox.insert(i, path)

        self.listbox.bind('<Return>', lambda event: self.open_file())
        self.bind('<Double-Button-1>', lambda e: self.open_file())
        self.listbox.bind("<BackSpace>", lambda e: self.delete_entry())

    def open_file(self):
        path = self.listbox.get(tk.ACTIVE)
        if platform.system() == 'Darwin':  # macOS
            subprocess.call(('open', path))
        elif platform.system() == 'Windows':  # Windows
            os.startfile(path)
        else:  # linux variants
            subprocess.call(('xdg-open', path))

    def delete_entry(self):
        path = self.listbox.get(tk.ACTIVE)
        idx = self.listbox.get(0, tk.END).index(path)
        self.listbox.delete(idx)
        self.paths.remove(path)

    def get_paths(self):
        return self.paths

class ImageLabel(tk.Label):
    """
    A Label that displays images, and plays them if they are gifs
    :im: A PIL Image instance or a string filename
    """

    def load(self, im):
        if isinstance(im, str):
            im = Image.open(im)

        frames = []

        try:
            for i in count(1):
                frames.append(ImageTk.PhotoImage(im.copy()))
                im.seek(i)
        except EOFError:
            pass

        self.frames = cycle(frames)
        try:
            self.delay = im.info['duration']
        except:
            self.delay = 60

        if len(frames) == 1:
            self.config(image=next(self.frames))
        else:
            self.next_frame()

    def unload(self):
        self.config(image=None)
        self.frames = None

    def next_frame(self):
        if self.frames:
            self.config(image=next(self.frames))
            self.config(borderwidth=0, bg="#333333")
            self.after(self.delay, self.next_frame)


class Calendar(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent, width=500, height=750)
        self.date_calendar = tkcalendar.Calendar(self, font="Helvetica 24", selectmode='day', year=parent.today.year,
                                                 month=parent.today.month, day=parent.today.day,
                                                 date_pattern='MM/dd/yyyy', background="#353638",
                                                 disabledbackground="#565B5E", bordercolor="#565B5E",
                                                 headersbackground="black", normalbackground="#353638",
                                                 foreground='white', normalforeground='white', headersforeground='white',
                                                 showweeknumbers=False)
        #self.date_calendar.config(background="#53525c")
        self.date_calendar.pack()
        style = ttk.Style(self)
        style.theme_use('clam')

    def get_date(self):
        return self.date_calendar.get_date()