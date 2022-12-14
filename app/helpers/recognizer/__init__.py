import threading
from app.helpers.recognizer import FaceFinder


def start_facefinder(parent, controller, root):
    print('starting')
    face_finder = FaceFinder.FaceFinder(parent, controller)
    t1 = threading.Thread(target=face_finder.start())
    t1.start()

