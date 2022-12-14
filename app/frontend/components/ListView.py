import math
import subprocess, os, platform
import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from app.constants import WINDOW_WIDTH, WINDOW_HEIGHT
import app.frontend.constants as const
from app.backend.db_adapter import Adapter

adapter = Adapter()

class ListView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        ctk.CTkFrame.__init__(self, parent)
        self.parent = parent
        self.table_cols = ["Date:", "Description:", "People:", "Location:", "Files:"]
        self.event_keys = ["date", 'description', 'people', 'location', 'files']

        # self.col_height =
        self.widgets = []

        self.events = adapter.get_all_events()
        self.event_rows = []  # [ [row widgets], ... ]
        self.row_height = const.LISTVIEW_DATE_COL_WIDTH // 2
        #self.table_header = TableHeader(self, self.table_cols)

        #self.initialize_table()

        #ctk_textbox_scrollbar = ctk.CTkScrollbar(self, command=self.canvas.yview)
        #ctk_textbox_scrollbar.grid(row=1, column=1, sticky='wns')

        self.row_container = RowContainer(self, parent)
        self.row_container.grid(row=1, column=0)
        '''
        self.canvas.grid(row=1, column=0, sticky='w')
        self.canvas.create_window((0, 75), window=self.row_container, anchor="w")
        self.canvas.configure(yscrollcommand=ctk_textbox_scrollbar.set)
        self.row_container.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        '''
        #self.table_header.grid(row=0, column=0, columnspan=5, sticky="nsw")


        # Row Sizes
        title_row_height = 40
        self.grid_rowconfigure(1, minsize=title_row_height, weight=1, uniform='row')


        # Col Sizes
        # widget = self.grid_slaves(row=1, column=1)[0].configure()

        for i, e in enumerate(self.events):
            row = EventRow(self.row_container.container, self, e, i)
            self.row_container.insert_row(row, i)

            #self.add_row(e)

        self.row_container.build_scrollbar()
        self.placeholder = ctk.CTkLabel(self, text='').grid(row=2, column=0)


    def refresh(self):
        ''' When Refreshing listview, delete all rows and redisplay them by creation date '''
        self.events = adapter.get_all_events()
        event_rows = self.event_rows.copy()  # copy event row widgets
        self.event_rows = []  # reset event row widgets to add new ones
        for widget_list in event_rows:
            for w in widget_list:
                w.destroy()
            #self.row_count -= 2

        for i, e in enumerate(self.events):
            print('g')
            #self.add_row(e)
            #self.row_count += 1

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


class RowContainer(ctk.CTkFrame):
    def insert_row(self, row, row_idx):
        row.grid(row=row_idx, column=0)
        self.num_rows += 1

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def build_scrollbar(self):
        ctk_textbox_scrollbar = ctk.CTkScrollbar(self, command=self.canvas.yview)
        ctk_textbox_scrollbar.grid(row=0, column=1, sticky='ens')

        self.canvas.grid(row=0, column=0)
        self.canvas.create_window((0, 0), window=self.container)
        self.canvas.configure(yscrollcommand=ctk_textbox_scrollbar.set)
        self.container.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

    def __init__(self, parent, controller):
        ctk.CTkFrame.__init__(self, parent)
        self.parent = parent
        self.container = Container(parent)
        self.container.grid(row=0, column=0)
        self.canvas = tk.Canvas(self, width=const.LISTVIEW_ROW_WIDTH - 65, height=self.parent.row_height * 10,
                                highlightthickness=0, bg='#2B2B2B')
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.num_rows = 0


class Container(ctk.CTkFrame):
    def __init__(self, parent):
        ctk.CTkFrame.__init__(self, parent)


class TableHeader(ctk.CTkFrame):
    def __init__(self, parent):
        self.columns = const.LISTVIEW_COLS
        ctk.CTkFrame.__init__(self, parent)
        padx = (0,5)
        for i, col in enumerate(self.columns):
            if col == 'Date:':
                lbl = ctk.CTkLabel(self, text=col, width=const.LISTVIEW_DATE_COL_WIDTH, height=75, corner_radius=10)
                padx = (0,5)
            elif col == 'Description:':
                lbl = ctk.CTkLabel(self, text=col, width=const.LISTVIEW_DESCR_COL_WIDTH, height=75, corner_radius=10)
                lbl.configure()
            elif col == 'People:':
                lbl = ctk.CTkLabel(self, text=col, width=const.LISTVIEW_PEOPLE_COL_WIDTH, height=75, corner_radius=10)
                lbl.configure()
            elif col == 'Location:':
                lbl = ctk.CTkLabel(self, text=col, width=const.LISTVIEW_LOCATION_COL_WIDTH, height=75, corner_radius=10)
            else:
                lbl = ctk.CTkLabel(self, text=col, width=const.LISTVIEW_FILE_COL_WIDTH - 67, height=75, corner_radius=10)
                lbl.configure(anchor='w')
            lbl.configure(fg_color=const.LISTVIEW_HEADER_BG_COLOR)
            lbl.grid(row=0, column=i, padx=padx)


class EventRow(ctk.CTkFrame):
    def __init__(self, parent, controller, event, row_num):
        ctk.CTkFrame.__init__(self, parent)
        row_widgets = []
        if row_num == 0 or row_num % 2 == 0:
            bg_color = const.LISTVIEW_TABLE_BG_COLOR
            font_color = const.LISTVIEW_TABLE_FONT_COLOR
        else:
            bg_color = const.LISTVIEW_TABLE_BG_COLOR2
            font_color = const.LISTVIEW_TABLE_FONT_COLOR

        for i, k in enumerate(controller.event_keys):
            try:
                v = event[k]
                if 'null' in v:
                    v = 'n/a'
            except AttributeError:
                v = "n/a"
            except TypeError:
                v = "n/a"

            if k == 'files':
                widget = FileList(self, event['files'])
                widget.grid(row=0, column=i, padx=(5,0), pady=(5, 0), sticky="e")
            elif k == 'description':
                widget = ctk.CTkLabel(self, text=f'     {v}',
                                      font=('helvetica', 13),
                                      height=const.LISTVIEW_ROW_HEIGHT // 2,
                                      width=const.LISTVIEW_DESCR_COL_WIDTH,
                                      text_color=font_color,
                                      fg_color=bg_color)
                widget.grid(row=0, column=i, pady=(5, 0))
            elif k == 'people':

                if v != 'n/a' and isinstance(v, list):
                    people = ''
                    for j, person in enumerate(v):
                        people += person
                        if len(v) > 1 and j < len(v) - 1:
                            people += ', '
                    v = people

                widget = ctk.CTkLabel(self, text=f'    {v}',
                                      font=('helvetica', 13),
                                      height=const.LISTVIEW_ROW_HEIGHT // 2,
                                      width=const.LISTVIEW_PEOPLE_COL_WIDTH,
                                      text_color=font_color,
                                      fg_color=bg_color)
                widget.grid(row=0, column=i, pady=(5, 0))
            elif k == 'location':
                widget = ctk.CTkLabel(self, text=f'    {v}',
                                      font=('helvetica', 13),
                                      height=const.LISTVIEW_ROW_HEIGHT // 2,
                                      width=const.LISTVIEW_ROW_HEIGHT,
                                      text_color=font_color,
                                      fg_color=bg_color)
                widget.grid(row=0, column=i, pady=(5, 0))
            else: # Date
                widget = ctk.CTkLabel(self, text=f'{v}',
                                      height=const.LISTVIEW_ROW_HEIGHT // 2,
                                      width=const.LISTVIEW_DATE_COL_WIDTH,
                                      font=('helvetica', 13),
                                      text_color=font_color,
                                      fg_color=bg_color)
                widget.grid(row=0, column=i, pady=(5, 0))

            if k != 'files' and k != 'date':
                widget.configure(anchor="w")
                widget.grid(padx=(5, 0))

            row_widgets.append(widget)
            controller.widgets.append(widget)

        controller.event_rows.append(row_widgets)
        # Col Sizes


class FileList(tk.Listbox):
    def __init__(self, parent, paths):
        super().__init__(parent, height=2,
                         width=20,
                         bg="white",
                         activestyle='dotbox',
                         font="Helvetica",
                         fg="black")

        for i, path in enumerate(paths):
            self.insert(i, path)

        self.bind('<Return>', lambda event: self.open_file())
        self.bind('<Double-Button-1>', lambda e: self.open_file())

    def open_file(self):
        path = self.get(tk.ACTIVE)
        if platform.system() == 'Darwin':  # macOS
            subprocess.call(('open', path))
        elif platform.system() == 'Windows':  # Windows
            os.startfile(path)
        else:  # linux variants
            subprocess.call(('xdg-open', path))


