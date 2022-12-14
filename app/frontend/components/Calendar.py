import tkinter as tk
import datetime
from tkinter import ttk
from datetime import date
from app.frontend.constants import CALENDAR_CELL_WIDTH, CALENDAR_CELL_HEIGHT
from dateutil.relativedelta import relativedelta
from calendar import monthrange
from urllib3.connectionpool import xrange
from app.backend.db_adapter import Adapter

adapter = Adapter()
adapter.get_all_encodings()

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
        tk.Frame.__init__(self, parent, width=CALENDAR_CELL_WIDTH * 7, height=15)
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
        if self.events:  # If there are events
            ttk.Frame.__init__(self, parent, width=CALENDAR_CELL_WIDTH, height=CALENDAR_CELL_HEIGHT,
                               style='CalendarTileYesEvent.TFrame')
            self.date_lbl = ttk.Label(self, text=day, style="CalendarTileYesEvent.TLabel")
            self.events_lbl = ttk.Label(self, text=f"{len(self.events)} event(s)", style="CalendarTileYesEvent.TLabel")

        else:
            ttk.Frame.__init__(self, parent, width=CALENDAR_CELL_WIDTH, height=CALENDAR_CELL_HEIGHT,
                               style='CalendarTileNoEvent.TFrame')
            # self.bind("<Enter>", self.config(style='CalendarTileNoEventHOVER.TFrame'))
            # self.bind("<Leave>", self.config(style='CalendarTileNoEvent.TFrame'))
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