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
from app.frontend.frames import SortMenu
from urllib3.connectionpool import xrange
from dateutil.relativedelta import relativedelta
from app.helpers import get_unique
from app.frontend.helpers import configure_style
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
        self.rowconfigure(0, minsize=WINDOW_HEIGHT*0.03)  # Set nav to 3% of window
        self.event_view.grid(row=1, column=1)
        self.sort_menu.grid(row=1, column=0, sticky='nwe')

        # self.style.configure('TButton', font=('Helvetica', 12))
        configure_style(self)

    def menubar(self, root):
        return "f"


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
