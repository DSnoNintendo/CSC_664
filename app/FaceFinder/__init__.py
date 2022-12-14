import os
import cv2
import face_recognition
from app.backend import db_adapter
from PIL import Image
import numpy as np
from pathlib import Path
from app.utils.image import decode_heic


class FaceFinder:
    # I used your code to create a class called FaceFinder.
    # Learn about Python classes: https://www.w3schools.com/python/python_classes.asp
    # The start function will be run in the background to find faces
    def __init__(self):
        # gallery_as path list function simplified
        self.model = cv2.CascadeClassifier(cv2.data.haarcascades + "./haarcascade_frontalface_default.xml")
        self.db = db_adapter.Adapter()
        self.db_encodings = self.db.get_all_encodings()
        self.image = None
        self.face_encodings = None

    def open_img(self, path):
        print(path)
        if Path(path).suffix != '.heic':

            self.image = face_recognition.load_image_file(path, mode='RGB')

        else:
            self.image = decode_heic(path).convert('RGB')
            self.image = np.asarray(self.image)

    def face_in_photo(self):
        self.face_encodings = face_recognition.face_encodings(self.image)
        if len(self.face_encodings):
            return True
        return False

    def face_in_db(self, new_encoding):
        for db_encoding in self.db_encodings:  # encoding from database
            # face encoding stored in a single key json. get first key in set of keys (there is only one)
            db_face_name = next(iter(db_encoding.keys()))
            db_face_encoding = np.array(db_encoding[db_face_name])
            result = face_recognition.compare_faces([db_face_encoding], new_encoding)
            if result[0]:
                return True
        return False

    def add_face_to_db(self, encoding, name):
        self.db.add_face_encoding(encoding=encoding, name=name)

    def crop_faces(self):  # renamed to crop_face
        faces = face_recognition.face_locations(self.image)
        faces_list = []
        for i in range(len(faces)):
            top, right, bottom, left = faces[i]
            faceImage = self.image[top:bottom, left:right]
            final = Image.fromarray(faceImage)
            faces_list.append(final)
        return faces_list
