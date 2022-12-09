import datetime
import threading
from datetime import date
from calendar import monthrange
import tkinter as tk
from tkinter import ttk, PhotoImage
from PIL import Image, ImageTk
from itertools import count, cycle
from .constants import CALENDAR_CELL_WIDTH, CALENDAR_CELL_HEIGHT
from app.constants import CWD, MUSIC_DIR, WINDOW_HEIGHT, WINDOW_WIDTH
from app.backend.db_adapter import Adapter
from urllib3.connectionpool import xrange
from dateutil.relativedelta import relativedelta
from app.helpers.recognizer import start_filefinder
from app.helpers import get_unique
import tkcalendar
import subprocess, os, platform
import math

adapter = Adapter()
adapter.get_all_encodings()

class CalendarScreen(ttk.Frame):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent, style="EventView.TFrame")
        self.style = ttk.Style(self)

        self.sort_menu = SortMenu(self, parent)
        self.event_view = EventView(self, parent)  # contains event view

        self.nav = Nav(self, parent)

    def build(self):
        self.nav.build()
        self.event_view.build()
        self.nav.grid(row=0, column=0, sticky='nswe', columnspan=2)
        self.rowconfigure(0, minsize=WINDOW_HEIGHT*0.03)
        self.event_view.grid(row=1, column=1)
        self.sort_menu.grid(row=1, column=0, sticky='nwe')

        # self.style.configure('TButton', font=('Helvetica', 12))

        self.style.configure('EventView.TFrame', background="#add8e6")
        self.style.configure('Weekday.TLabel', background='white', borderwidth=7)
        self.style.configure('Weekday.TFrame', background='white')

        self.style.configure('Nav.TFrame',
                             background="white")
        self.style.map('CalendarTileNoEvent.TFrame',
                       background=[('!active', 'grey'), ('active', '#b4e3fb')])
        self.style.map('CalendarTileNoEventHOVER.TFrame',
                       background=[('!active', '#b4e3fb'), ('active', '#b4e3fb')])
        self.style.configure('CalendarTileNoEvent.TLabel',
                             background='grey')
        self.style.configure('CalendarTileYesEvent.TFrame',
                             background='#65a1c2')
        self.style.configure('CalendarTileYesEvent.TLabel',
                             background='#65a1c2')
        self.style.configure('CalendarHeaderMonth.TLabel',
                             background='white',
                             font=('Helvetica', 16))
        self.style.configure("CalendarHeader.TFrame",
                             width=CALENDAR_CELL_WIDTH*10)
        self.style.configure("EventParam.TButton",
                             relief='flat', padding=(0,0,0,0), height=0, width=0)

    def menubar(self, root):
        menubar = tk.Menu(root)

        preferences_menu = tk.Menu(menubar, tearoff=0)
        preferences_menu.add_command(label="Start facial recogniton", command=lambda: start_facefinder(self,
                                                                                                       self.controller,
                                                                                                       self.parent))
        menubar.add_cascade(label="Actions"
                                  "", menu=preferences_menu)
        return menubar


class Nav(ttk.Frame):
    def __init__(self, parent, controller):
        # PARENT - CALENDAR SCREEN
        self.parent = parent
        self.controller = controller
        ttk.Frame.__init__(self, parent, width=WINDOW_WIDTH, style="Nav.TFrame")
        self.container = parent.event_view
        self.view_button = tk.Button(self, text="□", command=lambda: self.change_view())
        self.add_event_button = tk.Button(self, text="+", command=lambda: self.new_event())

    def build(self):
        self.view_button.pack(side=tk.LEFT)
        self.add_event_button.pack(side=tk.LEFT)
        # self.calendar_button.pack(side=tk.LEFT)

    def change_view(self):
        if self.view_button.cget('text') == "□":
            self.container.show_calendar()
            self.view_button["text"] = "≡"

        elif self.view_button.cget('text') == "≡":
            self.container.show_list_view()
            self.view_button["text"] = "□"

    def new_event(self):
        event_view = NewEventView(self, self.controller)


class EventView(ttk.Frame):
    def __init__(self, parent, controller):
        self.parent = parent
        ttk.Frame.__init__(self, parent)
        self.calendar = Calendar(self, parent)
        self.list_view = ListView(self, parent)

    def build(self):
        self.list_view.pack()

    def show_calendar(self):
        self.list_view.pack_forget()
        self.calendar.pack()

    def show_list_view(self):
        self.calendar.pack_forget()
        self.list_view.refresh()
        self.list_view.pack()


class SortMenu(ttk.Frame):
    class DateListBox(ttk.Frame):
        def __init__(self, parent):
            def on_click(event):
                selection = event.widget.curselection()
                if selection:
                    index = selection[0]
                    data = event.widget.get(index)
                    #self.event_view.refresh(data)

            ttk.Frame.__init__(self, parent)
            self.listbox = tk.Listbox(self, height=4,
                                      width=15,
                                      bg="grey",
                                      activestyle='dotbox',
                                      font="Helvetica",
                                      fg="black")
            self.listbox.grid(row=0,column=0)
            self.listbox.insert(0, "Event: New to Old")
            self.listbox.insert(1, "Event: Old to New")
            self.listbox.insert(2, "Creation: Old to New")
            self.listbox.insert(3, "Creation: New to Old")
            self.listbox.selection_set(0)
            self.listbox.bind('<<ListboxSelect>>', on_click)
            # self.event_view = parent.parent.event_view

    class PeopleListBox(ttk.Frame):
        def __init__(self, parent):
            def on_click(event):
                selection = event.widget.curselection()
                if selection:
                    index = selection[0]
                    data = event.widget.get(index)
                    #self.event_view.refresh(data)

            def get_events():
                events = adapter.get_all_events()
                people = []
                for e in events:
                    try:
                        p = e['people']
                        if p in people:
                            continue
                        people.append(p)
                    except KeyError:
                        pass
                return people

            ttk.Frame.__init__(self, parent)
            self.listbox = tk.Listbox(self, height=2,
                                      width=15,
                                      bg="grey",
                                      activestyle='dotbox',
                                      font="Helvetica",
                                      fg="black")
            self.listbox.grid(row=0,column=0)
            people_list = get_events()
            if len(people_list):
                for i, person in enumerate(people_list):
                    self.listbox.insert(i, person)
            else:
                self.listbox.insert(0, "No people detected")

            self.listbox.bind('<<ListboxSelect>>', on_click)


            # self.event_view = parent.parent.event_view


    class SortContainer(ttk.Frame):
        def __init__(self, parent, controller):
            ttk.Frame.__init__(self, parent)
            event_date_lbl = tk.Label(self, text="Date:")
            event_date_lbl.grid(row=1, column=0)
            event_date_listbox = parent.DateListBox(self)
            event_date_listbox.grid(row=2, column=0, sticky="nswe")
            people_lbl = tk.Label(self, text="People:")
            people_lbl.grid(row=5, column=0)
            people_listbox = parent.PeopleListBox(self)
            people_listbox.grid(row=6, column=0)


    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.width = WINDOW_WIDTH * 0.1
        sort_by_lbl = tk.Label(self, text="Sort By:", font='underline')
        sort_by_lbl.grid(row=0, column=0, sticky="n")
        date_sortbox = self.SortContainer(self, parent)
        date_sortbox.grid(row=1, column=0, pady=(5, 0))


class NewEventView(ttk.Frame):
    def __init__(self, parent, controller):
        # PARENT - NEW EVENT VIEW
        ttk.Frame.__init__(self, parent)
        self.widgets = []
        self.parent = parent
        self.top = tk.Toplevel(parent)
        self.top.wm_geometry("375x250")
        self.today = datetime.datetime.today()
        self.descr_lbl = tk.Label(self.top, text="Description:")
        self.descr_lbl.grid(row=1, column=0)
        self.widgets.append(self.descr_lbl)
        self.descr = tk.StringVar(self)
        self.descr_entry = tk.Entry(self.top, bd=5, textvariable=self.descr)
        self.descr_entry.grid(row=1, column=1)
        self.widgets.append(self.descr_entry)

        self.date_lbl = tk.Label(self.top, text="Date:")
        self.date_lbl.grid(row=2, column=0)
        self.widgets.append(self.date_lbl)
        self.date_calendar = tkcalendar.Calendar(self.top, selectmode='day', year=self.today.year,
                                                 month=self.today.month, day=self.today.day, date_pattern='MM/dd/yyyy')
        self.date_calendar.grid(row=2, column=1)

        self.param_view = self.EventParams(self.top, self.descr)
        self.param_view.grid(row=4, column=0, columnspan=3, sticky='w')
        self.descr_entry.bind('<Return>', lambda e: self.param_view.start_analysis_thread())
        self.widgets.append(self.param_view)

        self.confirm_btn = tk.Button(self.top, text="Confirm", command=lambda: self.start_event_creation())
        self.confirm_btn.grid(row=5, column=3, pady=3, padx=3)
        self.widgets.append(self.confirm_btn)

    def start_event_creation(self):
        event_props = dict()
        event_props['description'] = self.descr.get()
        event_props['date'] = self.date_calendar.get_date()
        event_props['location'] = self.param_view.get_location()
        event_props['people'] = self.param_view.get_people()
        start_filefinder(self, self.parent, event_props)
        self.date_calendar.destroy()
        for w in self.widgets:
            w.destroy()
        loading_img = ImageLabel(self.top)
        loading_img.pack()
        loading_img.load(f'{CWD}/images/src/loading.gif')
        self.widgets.append(loading_img)
        loading_label = tk.Label(self.top, text="Searching for media associated with event...")
        loading_label.pack()
        self.widgets.append(loading_label)

    def after_event_creation(self, events_props):
        # After event is created, destroy this window and navigate to month of event on Calendar
        # NAV -> SCREEN -> CONTAINER -> SET VIEW -> DATE
        view_container = self.parent.parent.event_view
        #view_container.show_calendar()
        view_container.list_view.refresh()
        view_container.show_list_view()


        #view_container.calendar.calendar_nav.set_month(events_props['date'])
        self.destroy()

    class EventParams(ttk.Frame):
        def __init__(self, parent, stringvar):
            ttk.Frame.__init__(self, parent)
            self.name_label = tk.Label(self, text='person detected:', fg='green')
            self.location_label = tk.Label(self, text='place detected:', fg='green')
            self.sv = stringvar
            self.buttons = []
            self.description = ""
            self.location = None
            self.people = None

            stringvar.trace("w", lambda name, index, mode,
                                        sv=self.sv: self.set_string())

        def start_analysis_thread(self):
            print('starting analysis')
            print(self.sv.get())
            t = threading.Thread(target=lambda: self.analyze(self.description))

            t.start()

        def set_string(self):
            print("setting")
            self.description = self.sv.get()
            print(self.description)

        def analyze(self, s):
            for b in self.buttons:
                b.destroy()
            dict = get_unique(s)
            people = dict['people']
            location = dict['location']
            if len(people):
                self.create_name_lbl(people)

            if len(location):
                self.create_location_lbl(location)

        def create_name_lbl(self, l):
            self.name_label.grid(row=0, column=0)
            col = 1
            for i, name in enumerate(l):
                name_btn = ttk.Button(self, text=name, style="EventParam.TButton")
                name_btn.grid(row=0, column=col, ipady=0, ipadx=0, pady=0, padx=0)
                col += 1
                self.buttons.append(name_btn)
                self.people = name

        def create_location_lbl(self, loc):
            self.location_label.grid(row=1, column=0)
            col = 1
            location_btn = ttk.Button(self, text=loc, style="EventParam.TButton")
            location_btn.grid(row=1, column=col, ipady=0, ipadx=0, pady=0, padx=0)
            self.buttons.append(location_btn)
            self.location = loc

        def get_location(self):
            return self.location

        def get_people(self):
            return self.people


class LoadingScreen(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        frameCnt = 12
        print(f'{CWD}/images/src/loading.gif')
        frames = [PhotoImage(file=f'{CWD}/images/src/loading.gif', format='gif -index %i' % (i)) for i in range(frameCnt)]

        def update(ind):
            frame = frames[ind]
            ind += 1
            if ind == frameCnt:
                ind = 0
            label.configure(image=frame)
            self.after(100, update, ind)

        label = tk.Label(self)
        label.pack()
        self.after(0, update, 0)


class ListView(ttk.Frame):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent, style="EventView.TFrame")
        self.parent = parent
        self.table_cols = ["Date:", "Description:", "People:", "Location:", "Files:"]
        self.event_keys = ["date", 'description', 'people', 'location', 'files']
        self.col_width = (WINDOW_WIDTH - parent.parent.sort_menu.width) // len(self.table_cols)
        self.row_height = 0
        self.events_per_page = 8
        self.event_count = 0
        # self.col_height =
        self.widgets = []
        self.row_count = 0
        self.col_count = 0
        self.events = adapter.get_all_events()
        self.nav = ListViewNav(self, parent)
        self.widgets.append(self.nav)
        self.initialize_table()
        self.spare_events = []
        self.event_rows = []  # [ [row widgets], ... ]

        for i, e in enumerate(self.events):
            if i == self.events_per_page:
                self.spare_events = self.events[i:]
                print("spare events")
                break

            self.add_row(e)
            self.row_count += 1

        print(f'num rows: {self.row_count}')

        # Row Sizes
        title_row_height = 40
        self.grid_rowconfigure(1, minsize=title_row_height, weight=1, uniform='row')

        self.row_size = (WINDOW_HEIGHT - title_row_height - 20) / self.events_per_page
        for row in xrange(2, self.row_count):
            self.grid_rowconfigure(row, minsize=15, weight=1)

        # Col Sizes
        self.date_col_width = int(math.floor(self.col_width * 0.25) + 15)
        self.grid_columnconfigure(0, minsize=self.date_col_width, weight=1)  # Date col is smallest
        self.file_col_width = self.col_width + self.date_col_width
        self.grid_columnconfigure(2, minsize=self.file_col_width, weight=1)
        self.descr_col_width = self.date_col_width * 3
        self.grid_columnconfigure(1, minsize=self.descr_col_width, weight=1)
        # widget = self.grid_slaves(row=1, column=1)[0].configure()

        if self.spare_events:
            btnFrame = tk.Frame(self)
            left_btn = tk.Button(btnFrame, text="←")
            right_btn = tk.Button(btnFrame, text="→")
            left_btn.grid(row=0, column=0)
            right_btn.grid(row=0, column=1)
            print(self.grid_size()[0]-1, self.grid_size()[1]-1)
            btnFrame.grid(row=self.row_count, column=3, sticky="n")


    def initialize_table(self):
        for i, col in enumerate(self.table_cols):
            lbl = ttk.Label(self, text=col)
            lbl.grid(row=self.row_count, column=i, sticky="nsew")
            if col == 'Date:':
                lbl.configure(anchor="w")
                lbl.grid(padx=(5, 0))
            elif col == 'Description:':
                lbl.configure(anchor="w", justify=tk.LEFT)
                lbl.grid(padx=(5, 0))
            else:
                lbl.configure(anchor="w")
                lbl.grid(padx=(5, 0))
        self.row_count += 1
        for col in xrange(len(self.table_cols)):
            self.grid_columnconfigure(col, minsize=self.col_width, weight=1)


    def refresh(self):
        ''' When Refreshing listview, delete all rows and redisplay them by creation date '''
        self.events = adapter.get_all_events()
        event_rows = self.event_rows.copy() # copy event row widgets
        self.event_rows = []  # reset event row widgets to add new ones
        for widget_list in event_rows:
            for w in widget_list:
                w.destroy()
            self.row_count -= 2

        for i, e in enumerate(self.events):
            self.add_row(e)
            self.row_count += 1


    def add_row(self, event):
        row_widgets = []
        for i, k in enumerate(self.event_keys):
            try:
                v = event[k]
                if 'null' in v:
                    v = 'n/a'
            except AttributeError:
                v = "n/a"
            except TypeError:
                v = "n/a"

            if k == 'files':
                widget = self.FileList(self, event['files'])
                widget.grid(row=self.row_count, column=i, padx=(5, 10), sticky="nsew")
            elif k != 'date':
                widget = tk.Label(self, text=f'  {v}')
                widget.grid(row=self.row_count, column=i, sticky="nsew")
            else:
                widget = tk.Label(self, text=f'{v}')
                widget.grid(row=self.row_count, column=i, sticky="nsew")

            if k != 'files':
                widget.configure(anchor="w")
                widget.grid(padx=(5,0))
                
            row_widgets.append(widget)
            self.widgets.append(widget)

        self.row_count += 1
        self.event_rows.append(row_widgets)

        '''
            for i, person in enumerate(people):
                if len(people) == 1:
                    people_str += person
                else:
                    if i != len(people) - 1:  # if not end of list
                        people_str += f'{person},'
                    else:
                        people_str += f'{person}'
        '''


    def divide_event_list(self):
        for j in range(0, len(self.events), self.events_per_page):
            yield self.events[j:j + self.events_per_page]

    class EventRow(ttk.Frame):
        def __init__(self, parent, event):
            ttk.Frame.__init__(self, parent)

            for i, k in enumerate(parent.event_keys):
                try:
                    v = event[k]
                    if 'null' in v:
                        v = 'n/a'
                except AttributeError:
                    v = "n/a"
                except TypeError:
                    v = "n/a"

                if k == 'files':
                    widget = parent.FileList(self, event['files'])
                    widget.grid(row=0, column=i, padx=(5, 10), sticky="nsew")
                elif k != 'date':
                    widget = tk.Label(self, text=f'  {v}')
                    widget.grid(row=0, column=i, sticky="nsew")
                else:
                    widget = tk.Label(self, text=f'{v}')
                    widget.grid(row=0, column=i, sticky="nsew")

                if k != 'files':
                    widget.configure(anchor="w")
                    widget.grid(padx=(5, 0))


    class FileList(ttk.Frame):
        def __init__(self, parent, paths):
            ttk.Frame.__init__(self, parent)

            self.listbox = tk.Listbox(self, height=5,
                                      width=45,
                                      bg="white",
                                      activestyle='dotbox',
                                      font="Helvetica",
                                      fg="black")
            for i, path in enumerate(paths):
                self.listbox.insert(i, path)

            self.listbox.bind('<Return>', lambda event: self.open_file())

            self.listbox.pack()

        def open_file(self):
            path = self.listbox.get(tk.ACTIVE)
            if platform.system() == 'Darwin':  # macOS
                subprocess.call(('open', path))
            elif platform.system() == 'Windows':  # Windows
                os. startfile(path)
            else:  # linux variants
                subprocess.call(('xdg-open', path))

    class SortMenu(ttk.Frame):
        def __init__(self, parent):
            ttk.Frame.__init__(self, parent)
            self.val = tk.StringVar()
            self.val.set("Date: Old to New")
            lbl = tk.Label(self, text="Sort By:").grid(row=0, column=0)
            menu = tk.OptionMenu(self, self.val, "Date: Old to New", "Date: New to Old").grid(row=0, column=1)



class ListViewNav(ttk.Frame):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.event_name_lbl = ttk.Label(text="Event Name:")

    def build(self):
        self.event_name_lbl.pack()


class Calendar(ttk.Frame):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.parent = parent
        self.curr_date = date.today()
        calendar_grid = CalendarGrid(self, parent, self.curr_date)
        self.calendar_nav = CalendarNav(self, parent, self.curr_date, calendar_grid)
        self.calendar_nav.build()
        calendar_grid.build_grid()
        self.calendar_nav.pack()
        calendar_grid.pack()


class CalendarNav(tk.Frame):
    def __init__(self, parent, controller, today, calendar_grid):
        self.calendar_grid = calendar_grid
        self.month_dict = {
            1: "January",
            2: "February",
            3: "March",
            4: "April",
            5: "May",
            6: "June",
            7: "July",
            8: "August",
            9: "September",
            10: "October",
            11: "November",
            12: "December"
        }
        tk.Frame.__init__(self, parent, width=CALENDAR_CELL_WIDTH*7, height=15)
        self.curr_date = today
        self.parent = parent
        self.month = self.curr_date.month
        self.year = self.curr_date.year
        self.month_label = ttk.Label(self, text=f'{self.month_dict[self.month]}, {self.year}',
                                     style="CalendarHeaderMonth.TLabel")
        self.left_button = tk.Button(self, text="←", command=lambda: self.previous())
        self.right_button = tk.Button(self, text="→", command=lambda: self.next())

    def build(self):
        self.month_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        self.left_button.place(in_=self.month_label, relx=0, x=-25, rely=0)
        self.right_button.place(in_=self.month_label, relx=1, rely=0)

    def next(self):
        self.curr_date = self.curr_date + relativedelta(months=1)
        self.month = self.curr_date.month
        self.year = self.curr_date.year
        self.month_label.config(text=f'{self.month_dict[self.month]}, {self.year}')
        self.calendar_grid.refresh(self.curr_date)

    def previous(self):
        self.curr_date = self.curr_date - relativedelta(months=1)
        self.month = self.curr_date.month
        self.year = self.curr_date.year
        self.month_label.config(text=f'{self.month_dict[self.month]}, {self.year}')
        self.calendar_grid.refresh(self.curr_date)

    def set_month(self, datestring):
        self.curr_date = datetime.datetime.strptime(datestring, '%m/%d/%Y').date()
        self.month = self.curr_date.month
        self.year = self.curr_date.year
        self.month_label.config(text=f'{self.month_dict[self.month]}, {self.year}')
        self.calendar_grid.refresh(self.curr_date)

class CalendarGrid(ttk.Frame):
    def __init__(self, parent, controller, today):
        ttk.Frame.__init__(self, parent)
        self.parent = parent
        self.curr_date = today
        self.days_in_month = monthrange(self.curr_date.year, self.curr_date.month)
        self.tiles = []
        self.build_grid()

    def refresh(self, date):
        self.curr_date = date
        self.days_in_month = monthrange(self.curr_date.year, self.curr_date.month)
        for tile in self.tiles:
            tile.destroy()
        self.build_grid()

    def build_grid(self):
        first_of_month = self.curr_date.replace(day=1)
        num_tiles = 0

        day_range = range(1, self.days_in_month[1] + 1)
        # day of week headers
        for i, day in enumerate(['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']):
            day_header = CalendarTileWeekday(self, self.parent, day)
            day_header.grid(column=i, row=0, sticky='news')

        # handle first date
        first_calender_tile = CalendarTile(self, self.parent, self.curr_date.year, self.curr_date.month, day_range[0])
        first_calender_tile.grid(column=first_calender_tile.col, row=num_tiles // 7 + 1, sticky='news')

        # Create grid spaces for empty spaces at beginning of calendar
        for i in range(first_calender_tile.col, 0, -1):
            tile = CalendarTileEmpty(self, self.parent)
            tile.grid(column=i - 1, row=1, sticky='news')
            self.tiles.append(tile)
            num_tiles += 1

        if num_tiles > 0:
            blackout_lbl = tk.Label(self, text="", bg="#525150")
            blackout_lbl.grid(row=1, column=0, sticky='news', columnspan=num_tiles)
            blackout_lbl.configure(highlightbackground='black', highlightthickness=20)
            self.tiles.append(blackout_lbl)

        for day in range(1, self.days_in_month[1] + 1):
            row = num_tiles // 7
            calendar_tile = CalendarTile(self, self.parent, self.curr_date.year, self.curr_date.month, day)
            calendar_tile.grid(column=calendar_tile.col, row=row + 1, sticky='news')
            self.tiles.append(calendar_tile)
            num_tiles += 1

        col_count, row_count = self.grid_size()

        for col in xrange(col_count):
            self.grid_columnconfigure(col, minsize=CALENDAR_CELL_WIDTH)

        for row in xrange(1, row_count):
            self.grid_rowconfigure(row, minsize=CALENDAR_CELL_HEIGHT)


class CalendarTile(ttk.Frame):
    def __init__(self, parent, controller, year, month, day):
        self.date = datetime.datetime(year, month, day)
        date_string = self.date.strftime("%m/%d/%Y")
        self.events = adapter.get_events(date_string)
        if self.events: # If there are events
            ttk.Frame.__init__(self, parent, width=CALENDAR_CELL_WIDTH, height=CALENDAR_CELL_HEIGHT,
                               style='CalendarTileYesEvent.TFrame')
            self.date_lbl = ttk.Label(self, text=day, style="CalendarTileYesEvent.TLabel")
            self.events_lbl = ttk.Label(self, text=f"{len(self.events)} event(s)", style="CalendarTileYesEvent.TLabel")

        else:
            ttk.Frame.__init__(self, parent, width=CALENDAR_CELL_WIDTH, height=CALENDAR_CELL_HEIGHT,
                               style='CalendarTileNoEvent.TFrame')
            #self.bind("<Enter>", self.config(style='CalendarTileNoEventHOVER.TFrame'))
            #self.bind("<Leave>", self.config(style='CalendarTileNoEvent.TFrame'))
            self.date_lbl = ttk.Label(self, text=day, style="CalendarTileNoEvent.TLabel")
            self.events_lbl = ttk.Label(self, text="No events", style="CalendarTileNoEvent.TLabel")


        w = self.date.weekday()

        if w == 6:  # sunday
            self.col = 0  # the column the tile will be placed in based on
        else:
            self.col = w + 1

        self.date_lbl.pack(side=tk.LEFT, anchor='nw')
        self.events_lbl.place(relx=0.5, rely=0.5, anchor=tk.CENTER)


class CalendarTileEmpty(ttk.Frame):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.border_frame = tk.Frame(self, background="black", width=CALENDAR_CELL_WIDTH, height=CALENDAR_CELL_HEIGHT)
        self.date_lbl = tk.Label(self.border_frame,
                                 background='grey', borderwidth=0, bd=0, anchor="center")
        self.date_lbl.pack(padx=1, pady=1)
        self.border_frame.pack()


class CalendarTileWeekday(ttk.Frame):
    def __init__(self, parent, controller, day):
        ttk.Frame.__init__(self, parent, style='Weekday.TFrame')
        self.border_frame = tk.Frame(self, background="black", width=CALENDAR_CELL_WIDTH)

        self.date_lbl = tk.Label(self, text=day, background='white', borderwidth=0, bd=0, anchor="center")

        self.date_lbl.pack(padx=10, pady=2)
        self.border_frame.pack()


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
            self.after(self.delay, self.next_frame)
