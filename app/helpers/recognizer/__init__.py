import threading
from app.helpers.recognizer import FaceFinder, FileFinder


def start_facefinder(parent, controller, root):
    print('starting')
    face_finder = FaceFinder.FaceFinder(parent, controller)
    t1 = threading.Thread(target=face_finder.start())
    t1.start()


def start_filefinder(parent, controller, event_props):
    file_finder = FileFinder.FileFinder(parent, controller, event_props)
    t1 = threading.Thread(target=lambda: file_finder.start())
    t1.start()
    print('starting file_finder')
