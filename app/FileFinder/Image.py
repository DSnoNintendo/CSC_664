import io

from app.constants import GALLERY_DIR
from pathlib import Path
from GPSPhoto import gpsphoto
from geopy.geocoders import Nominatim
from datetime import datetime
from app.FaceFinder import FaceFinder
from app.frontend.windows import FaceFoundWindow
import tkinter as tk
from pillow_heif import register_heif_opener
import PIL.Image
import exifread
import os
import PIL.ExifTags
import pyheif
import cv2


class Image:
    def __init__(self, gui):
        self.gui = gui
        self.file_list = []
        self.list_chunks = []
        self.acceptable_filetypes = ['.jpg', '.jpeg', '.heic']
        self.event_images = set()
        self.geolocator = Nominatim(user_agent="geoapiExercises")
        self.face_finder = FaceFinder()
        #self.face_finder =

    def isolate_files_by_date(self, date):
        for dirpath, dirs, files in os.walk(GALLERY_DIR, topdown=False):
            for file in files:
                path = os.path.join(dirpath, file)
                if Path(file).suffix in self.acceptable_filetypes and self.created_on(path, date):
                    self.file_list.append(path)
        print(self.file_list)

    def start(self, query):
        location = None
        people = []
        if query['location']:
            location = query['location']
            print(location)
        if len(query['people']):
            people = query['people']

        for path in self.file_list:
            if len(location):
                print('geodata')
                geodata = self.get_geodata(path)
                if location in str(geodata):
                    self.event_images.add(path)

            if people:
                # open image
                self.face_finder.open_img(path)
                # if image has a face
                if self.face_finder.face_in_photo():
                    for encoding in self.face_finder.face_encodings:
                        if self.face_finder.face_in_db(encoding):
                            self.event_images.add(path)  # if face in database add image to filedict
                        else: # if face not in database
                            face_images = self.face_finder.crop_faces()
                            for face in face_images:
                                # display face in gui
                                print('displating face')
                                pop_up = FaceFoundWindow(self.gui, face)
                                # ask user if face is present, or if face is user
                                result = pop_up.show()
                                if result:
                                    # If present, add encoding, and add file
                                    self.face_finder.add_face_to_db(encoding=encoding, name=result)
                    self.event_images.add(path)

        return list(self.event_images)


    def created_on(self, path, date):
        # get exif

        try:
            exif = self.get_exif(path)
            date_obj = datetime.strptime(exif['DateTimeOriginal'], '%Y:%m:%d %H:%M:%S').date().strftime('%m/%d/%Y')
            if date_obj == date:
                return True
        except Exception as e:
            print(e)
            return False

        return False

    def get_geodata(self, path):

        def decimal_coords(coords, ref):
            decimal_degrees = coords[0] + coords[1] / 60 + coords[2] / 3600
            if ref == 'S' or ref == 'W':
                decimal_degrees = -decimal_degrees
            return decimal_degrees

        def parse_exif(exif):
            gps_latitude = exif['GPS GPSLatitude'].strip('][').split(', ')
            gps_latitude = [eval(i) for i in gps_latitude]
            gps_longitude = exif['GPS GPSLongitude'].strip('][').split(', ')
            gps_longitude = [eval(i) for i in gps_longitude]
            coords = decimal_coords(gps_latitude, exif['GPS GPSLatitudeRef']), \
                     decimal_coords(gps_longitude, exif['GPS GPSLongitudeRef'])
            return coords

        try:
            if Path(path).suffix == '.jpeg' or Path(path).suffix == '.jpg':
                location = gpsphoto.getGPSData(path)
                latitude, longitude = (location['Latitude'], location['Longitude'])
                geodata = self.geolocator.reverse(f"{latitude}, {longitude}")
                return geodata

            elif Path(path).suffix == '.heic':
                exif = self.get_exif(path)
                latitude, longitude = parse_exif(exif)
                geodata = self.geolocator.reverse(f"{latitude}, {longitude}")
                return geodata

        except Exception as e:
            print('geodata error', e)
            pass

    def get_exif(self, path):
        if Path(path).suffix != '.heic':
            f = open(path, 'rb')
            exif_data = dict()

            # Return Exif tags
            tags = exifread.process_file(f)
            for k, v in tags.items():
                k = str(k)
                k = k.replace('EXIF ', '')
                exif_data[k] = str(v)
            f.close()
            return exif_data
        else:
            f = pyheif.read(path)
            exif_data = dict()
            for metadata in f.metadata:
                filestream = io.BytesIO(metadata['data'][6:])
                tags = exifread.process_file(filestream, details=False)
                for k, v in tags.items():
                    k = str(k)
                    k = k.replace('EXIF ', '')
                    exif_data[k] = str(v)

            f.close()
            return exif_data
