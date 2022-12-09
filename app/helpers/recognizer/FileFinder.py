import threading
import tkinter as tk
from tkinter import ttk
import PyPDF2
import subprocess, os, platform
import pathlib
from datetime import datetime, timedelta
from functools import partial
from urllib3.connectionpool import xrange
from app.constants import DOCUMENT_DIR, GALLERY_DIR, MUSIC_DIR
from app.backend.db_adapter import Adapter
import nltk
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
from nltk.tag.stanford import StanfordNERTagger
import numpy as np
import PIL.Image
import PIL.ExifTags
from GPSPhoto import gpsphoto
from geopy.geocoders import Nominatim
import eyed3


adapter = Adapter()
geolocator = Nominatim(user_agent="geoapiExercises")

class FileFinder:
    def __init__(self, parent, controller, event_props):
        self.parent = parent
        self.controller = controller
        self.event_props = event_props
        print(event_props)
        self.person = event_props['people']
        self.location = event_props['location']
        self.event_descr = self.event_props['description'].upper()
        self.event_descr_stems = self.stem(self.event_descr)
        self.dt_obj = datetime.strptime(self.event_props['date'], '%m/%d/%Y').date()
        self.date = self.event_props['date']
        self.event_files = []
        self.threads = []


    def start(self):
        # For tax documents (Ex: Filed Taxes on 06/20/2023)
        # Want to look for all tax documents created from Mid-2022 to 06/20/2023
        print(self.event_descr_stems)
        if any(substring in self.event_descr_stems for substring in ["tax"]):
            query = {
                'required': ['TAX', str(self.dt_obj.year - 1)]
                }
            self.start_pdf_search(query)  # Find PDFs containing tax and the previous year

        # if people in image defined
        # if location is found look for images
        print(self.location)
        if self.location:
            query = {
                'person': self.person,
                'location': self.location,
            }
            print('searching images')
            self.start_image_search(query)

        if any(substring in self.event_descr_stems for substring in ["listen", "album"]):
            print('mp3 search')
            query = {
                'person': self.person
                }
            self.start_mp3_search(query)  # Find PDFs containing tax and the previous year
        '''

        if any(substring in self.event_descr_stems for substring in ["BUY"]):
            self.find_pdfs([""])
        if any(substring in self.event_descr_stems for substring in ["SELL"]):
            self.find_pdfs([""])
        if any(substring in self.event_descr_stems for substring in ["READ"]):
            self.find_pdfs([""])
        if any(substring in self.event_descr_stems for substring in ["WATCH"]):
            self.find_videos([""])
            '''

        for t in self.threads:
            t.join()


        self.event_props['files'] = self.event_files
        event_file_view = EventFileView(self.parent, self.controller, self.event_props)

    def start_pdf_search(self, qualifiers):
        file_list = []
        for root, dirs, files in os.walk(DOCUMENT_DIR, topdown=False):
            for file in files:
                file_list.append(os.path.join(file))


        for l in self.split_list(file_list, 4):
            list_chunk = np.array(l).tolist()
            t = threading.Thread(target=lambda: self.find_pdfs(list_chunk, qualifiers))
            self.threads.append(t)
            t.start()

    def start_mp3_search(self, qualifiers):
        file_list = []
        for root, dirs, files in os.walk(MUSIC_DIR, topdown=False):
            for file in files:
                file_list.append(file)


        for l in self.split_list(file_list, 2):
            list_chunk = np.array(l).tolist()
            t = threading.Thread(target=lambda: self.find_mp3s(list_chunk, qualifiers))
            self.threads.append(t)
            t.start()


    def start_image_search(self, qualifiers):
        file_list = []
        for root, dirs, files in os.walk(GALLERY_DIR, topdown=False):
            for file in files:
                file_list.append(file)

        for l in self.split_list(file_list, 1):
            list_chunk = np.array(l).tolist()
            print(list_chunk)
            t = threading.Thread(target=lambda: self.find_images(list_chunk, qualifiers))
            self.threads.append(t)
            t.start()

    def stem(self, s):
        ps = PorterStemmer()
        stems = []
        for w in word_tokenize(s):
            stems.append(ps.stem(w))
        return stems

    def get_file_creation(self, path):
        try:
            ts = os.path.getmtime(path)
        except:
            ts = os.stat(path).st_birthtime

        return datetime.fromtimestamp(ts).date()

    def is_in_daterange(self, path, start_date):
        if start_date <= self.get_file_creation(path) <= self.dt_obj:
            print("True")

    def find_pdfs(self, files, qualifiers):
        # get all paths from document directory

        for path in files:
            full_path = DOCUMENT_DIR + '/' + path
            if pathlib.Path(full_path).suffix == '.pdf':
                pdfReader = PyPDF2.PdfFileReader(open(full_path, 'rb'), strict=False)
                for i in range(pdfReader.numPages):
                    pageObj = pdfReader.getPage(i)
                    page_txt = pageObj.extractText().upper()
                    if all(substring in page_txt for substring in qualifiers['required']):
                        self.event_files.append(full_path)
                        print("found file")
                        break

        print('search complete')

    def find_mp3s(self, files, qualifiers):
        # get all paths from document directory

        for path in files:
            full_path = MUSIC_DIR + '/' + path
            if pathlib.Path(full_path).suffix == '.mp3':
                mp3 = eyed3.load(full_path)
                print(mp3.tag.artist)
                if self.person in mp3.tag.artist:
                    print(mp3.tag.artist)
                    self.event_files.append(full_path)

        print('search complete')


    def find_images(self, files, query):
        def _convert_to_degress(value):
            """
            Helper function to convert the GPS coordinates stored in the EXIF to degress in float format
            :param value:
            :type value: exifread.utils.Ratio
            :rtype: float
            """
            d = float(value.values[0].num) / float(value.values[0].den)
            m = float(value.values[1].num) / float(value.values[1].den)
            s = float(value.values[2].num) / float(value.values[2].den)

            return d + (m / 60.0) + (s / 3600.0)

        def image_coordinates(exif):
            try:
                print(exif)
                gps_info = dict()
                for key in exif['GPSInfo'].keys():
                    decode = PIL.ExifTags.GPSTAGS.get(key, key)
                    gps_info[decode] = exif['GPSInfo'][key]

                gps_longitude = exif['GPSLongitude']
                gps_longitude_ref = exif['GPSLongitudeRef']
                gps_latitude = exif['GPSLatitude']
                gps_latitude_ref = exif['GPSLongitudeRef']

                print(gps_info)

                if gps_latitude:
                    lat_value = _convert_to_degress(gps_latitude)
                    if gps_latitude_ref.values != 'N':
                        lat_value = -lat_value

                    lon_value = _convert_to_degress(gps_longitude)
                    if gps_longitude_ref.values != 'E':
                        lon_value = -lon_value

                    return (lat_value, lon_value)

                return None
            except AttributeError as E:
                print(E)
                return None


        def created_on(date, exif):
            try:
                date_obj = datetime.strptime(exif['DateTimeOriginal'], '%Y:%m:%d %H:%M:%S').date()

                if date_obj == date:
                    return True
            except Exception as e:
                return False

            return False


        for path in files:
            full_path = GALLERY_DIR + '/' + path
            print(full_path)
            if pathlib.Path(full_path).suffix == '.jpg' or pathlib.Path(full_path).suffix == '.jpeg':
                img = PIL.Image.open(full_path)
                try:
                    exif = {
                        PIL.ExifTags.TAGS[k]: v
                        for k, v in img._getexif().items()
                        if k in PIL.ExifTags.TAGS
                    }
                    if created_on(self.dt_obj, exif):
                        print('Hi')
                        location = gpsphoto.getGPSData(full_path)
                        latitude, longitude = (location['Latitude'], location['Longitude'])
                        geodata = geolocator.reverse(f"{latitude}, {longitude}")
                        print(geodata)
                        print(query['location'])
                        print(full_path)
                        if query['location'] in str(geodata):
                            self.event_files.append(full_path)

                except Exception as e:
                    print(full_path, e)
                    continue


    def contains_human_name(self, s):
        st = StanfordNERTagger('stanford-ner/all.3class.distsim.crf.ser.gz', 'stanford-ner/stanford-ner.jar')
        people = []
        for sent in nltk.sent_tokenize(s):
            tokens = nltk.tokenize.word_tokenize(sent)
            tags = st.tag(tokens)
            for tag in tags:
                if tag[1] == 'PERSON':
                    people.append(tag[0])

        return tag

    def split_list(self, l, n):
        try:
            return np.split(np.array(l), n)
        except:
            return np.split(np.array(l), 1)

class EventFileView(ttk.Frame):
    def __init__(self, parent, controller, event_props):
        self.parent = parent
        self.top_win = self.parent.top
        ttk.Frame.__init__(self, parent)
        self.event_props = event_props
        self.event_files = event_props['files']
        self.row_count = 0

        if len(self.event_files) > 0:
            self.initialize_table()
            self.num_files_lbl = tk.Label(self.top_win, text=f"{len(self.event_files)} Files related to you "
                                                             f"event found. Review them below.")
            self.num_files_lbl.grid(row=0, columnspan=2)

            for path in self.event_files:
                filepath_lbl = PathLabel(self.top_win, path)
                filepath_lbl.grid(row=self.row_count, column=0)
                filepath_lbl.add_listeners()
                del_btn = tk.Button(self.top_win, text="❌")
                del_btn.configure(command=self.callback_factory(path, filepath_lbl, del_btn))
                del_btn.grid(row=self.row_count, column=1)
                self.row_count += 1

            conf_button = tk.Button(self.top_win, text="confirm", command=lambda: self.commit_event())
            conf_button.grid(row=self.row_count, column=0)

    def initialize_table(self):
        self.clear_parent()
        table_cols = ["Filepath:", " "]
        for i, col in enumerate(table_cols):
            lbl = tk.Label(self.top_win, text=col)
            lbl.grid(row=1, column=i)
        self.row_count += 1
        for col in xrange(len(table_cols)):
            self.grid_columnconfigure(col, minsize=200)

    def remove_event_file(self, filepath, lbl, btn):
        try:
            print(f"Removing {filepath} from list")
            self.event_files.remove(filepath)
            self.event_props['files'] = self.event_files

        except ValueError:
            print(self.event_files)
            print(filepath)
        lbl.destroy()
        btn.destroy()

    # For dynamic delete buttons
    def callback_factory(self, p, l, b):
        def _callback():
            return self.remove_event_file(p, l, b)

        return _callback

    def clear_parent(self):
        for w in self.parent.widgets:
            w.destroy()

    def commit_event(self):
        # add commit date to self
        if adapter.commit_event(self.event_props):
            print("Event Committed")
            # Close Window AND SHOW NEW EVENT
        self.parent.after_event_creation(self.event_props)



class PathLabel(tk.Label):
    def __init__(self, parent, path):
        self.path = path
        self.parent = parent
        kwargs = {
            'text': path,
            'fg': "black",
            'bg': "white",
        }
        # need to call constructor of inherited class
        super().__init__(parent, **kwargs)

    def add_listeners(self):
        self.bind("<Enter>", partial(self.color_config, self, "blue"))
        self.bind("<Leave>", partial(self.color_config, self, "black"))
        self.bind("<Button-1>", lambda e: self.open_file(self.path))

    def color_config(self, widget, color, event):
        self.configure(foreground=color)

    def open_file(self, path):
        if platform.system() == 'Darwin':  # macOS
            subprocess.call(('open', path))
        elif platform.system() == 'Windows':  # Windows
            os.startfile(path)
        else:  # linux variants
            subprocess.call(('xdg-open', path))
