from app.frontend.constants import CALENDAR_CELL_WIDTH

def configure_style(frame):
    frame.style.configure('EventView.TFrame', background="#add8e6")
    frame.style.configure('Weekday.TLabel', background='white', borderwidth=7)
    frame.style.configure('Weekday.TFrame', background='white')

    frame.style.configure('Nav.TFrame',
                         background="white")
    frame.style.map('CalendarTileNoEvent.TFrame',
                   background=[('!active', 'grey'), ('active', '#b4e3fb')])
    frame.style.map('CalendarTileNoEventHOVER.TFrame',
                   background=[('!active', '#b4e3fb'), ('active', '#b4e3fb')])
    frame.style.configure('CalendarTileNoEvent.TLabel',
                         background='grey')
    frame.style.configure('CalendarTileYesEvent.TFrame',
                         background='#65a1c2')
    frame.style.configure('CalendarTileYesEvent.TLabel',
                         background='#65a1c2')
    frame.style.configure('CalendarHeaderMonth.TLabel',
                         background='white',
                         font=('Helvetica', 16))
    frame.style.configure("CalendarHeader.TFrame",
                         width=CALENDAR_CELL_WIDTH * 10)
    frame.style.configure("EventParam.TButton",
                         relief='flat', padding=(0, 0, 0, 0), height=0, width=0)