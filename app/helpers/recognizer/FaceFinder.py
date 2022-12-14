import cv2
import os
import tkinter as tk
from PIL import ImageTk, Image
import face_recognition
from app.helpers import Config
from app.backend import db_adapter
import numpy as np
# The directory for storing faces,
#                   the image detection file,
#                   and the gallery directory path
#                   were moved to app.constants package. go check it out
from app.constants import GALLERY_ROWS, GALLERY_COL, GALLERY_DIR, GALLERY_CARD_SIZE, IMG_PROP_DIR


class FaceViewImage:
    def __init__(self, img):
        self.img = img
        self.height = self.img.height
        self.width = self.img.width
        self.format = self.img.format


class FaceView:
    def __init__(self, parent, face_img):
        img_obj = FaceViewImage(face_img)
        self.top = tk.Toplevel(parent)
        self.top.geometry(f"{img_obj.width}x{img_obj.height}")
        img = ImageTk.PhotoImage(img_obj.img)
        lbl = tk.Label(self.top, image=img)
        lbl.image = img
        lbl.pack()
        self.top.title('Face detected')

    def destroy(self):
        self.top.destroy()
        self.top.update()


class UnknownFaceView:
    def __init__(self, parent, controller, img_paths, face_encoding=None):
        self.img_paths = img_paths
        self.top = tk.Toplevel(parent)
        if not len(self.img_paths):
            self.top.title("No Faces Detected")
            self.lbl = tk.Label(self.top, text='No New Faces Detected')
            self.lbl.pack()
        else:
            self.top.title("Faces Detected")
            self.canvas = tk.Canvas(self.top, width=GALLERY_COL * GALLERY_CARD_SIZE, height=GALLERY_ROWS * GALLERY_CARD_SIZE)
            self.grid = Grid(self.top, controller, img_paths)
            self.scrollbar = tk.Scrollbar(self.top, orient="vertical", command=self.canvas.yview)
            self.canvas.configure(yscrollcommand=self.scrollbar.set)
            self.grid.bind(
                "<Configure>",
                lambda e: self.canvas.configure(
                    scrollregion=self.canvas.bbox("all")
                )
            )
            self.faceDialog = FaceDialog(self.top, controller, img_paths, face_encoding)
            self.grid.build()
            self.grid.pack()
            self.faceDialog.pack(side=tk.LEFT, fill='y')
            self.canvas.pack(side=tk.LEFT, padx=(0, 50))
            self.scrollbar.pack(side=tk.RIGHT, fill='y')
            self.canvas.create_window((0, 0), window=self.grid, anchor="nw")

    def destroy(self):
        self.top.destroy()
        self.top.update()


class KnownFaceView:
    def __init__(self, parent, controller, dictionary):
        self.top = tk.Toplevel(parent)
        labels = []
        for key in dictionary.keys():
            self.top.title('Known Faces Detected')
            lbl = tk.Label(self.top, text=f"{dictionary[key]} image(s) found matching face: {key}")
            labels.append(lbl)
        for label in labels:
            label.pack()

    def destroy(self):
        self.top.destroy()
        self.top.update()


class FaceFinder:
    # I used your code to create a class called FaceFinder.
    # Learn about Python classes: https://www.w3schools.com/python/python_classes.asp
    # The start function will be run in the background to find faces
    def __init__(self, parent, controller):
        # gallery_as path list function simplified
        self.image_paths = [os.path.join(GALLERY_DIR, f) for f in os.listdir(GALLERY_DIR)]
        self.model = cv2.CascadeClassifier(cv2.data.haarcascades + "./haarcascade_frontalface_default.xml")
        self.parent = parent
        self.controller = controller
        self.db = db_adapter.Adapter()




    def add_person_to_prop_file(self, path, name):
        prop_file = get_or_create_img_props(path)
        people_detected_list = prop_file.get_config('people_in_photo')
        # find first occurrence of unknown face
        idx = people_detected_list.index('unknown')
        people_detected_list[idx] = name
        prop_file.set_config('people_in_photo', people_detected_list)

    def start(self):
        # since we are loading every path in image_paths, name conventions were changed
        # when running for loops make the first variable singular, since we're looping one by one.
        # ex: for path in self.image_paths instead of for paths
        # it makes reading your code later easier
        #self.get_all_faces()
        # for face
        db_face_encodings = self.db.get_all_encodings()
        face_detected = False
        db_faces_found = dict()

        for i, path in enumerate(self.image_paths):
            prop_file = get_or_create_img_props(path)  # open property file for image
            if os.path.isdir(path) \
                    or (prop_file.config_exists('people_in_photo') and #  if there are knowingly no people in photo
                        'unknown' not in prop_file.get_config('people_in_photo'))\
                    or '.DS_Store' in path or 'props' in path:
                continue

            img_obj = face_recognition.load_image_file(path)
            face_encodings = face_recognition.face_encodings(img_obj)
            num_faces = len(face_encodings)
            prop_file.set_config('num_faces', num_faces)


            # if there is a face in the photo
            if not prop_file.config_exists('people_in_photo'):  # If false, config file already initialized
                prop_file.set_config('people_in_photo', ['unknown' for i in range(num_faces)])

            if not num_faces:
                continue

            for path_encoding in face_encodings:  # in case of multiple faces in one photo
                face_found = False
                checked = set()  # names of people with db encodings that were already checked.
                for db_encoding_json in db_face_encodings:  # encoding from database
                    # face encoding stored in a single key json. get first key in set of keys (there is only one)
                    db_face_name = next(iter(db_encoding_json.keys()))
                    db_face_encoding = np.array(db_encoding_json[db_face_name])
                    # convert stored encoding to multidimensional numpy array again
                    # db_face_encoding = np.argmax(db_face_encoding, axis=0)
                    result = face_recognition.compare_faces([db_face_encoding], path_encoding)
                    if result[0]:  # if faces match
                        # Set properties, save encoding
                        self.add_person_to_prop_file(path, db_face_name)

                        if db_face_name in db_faces_found.keys():  # if key is available, increment.
                            db_faces_found[db_face_name] = db_faces_found.get(db_face_name) + 1
                        else:  # if not, set to one
                            db_faces_found[db_face_name] = 1
                        face_found = True
                        break
                    else:
                        checked.add(db_face_name)

                if face_found:
                    continue

                #  if the face wasn't in the DB, try to group it with other unidentified faces
                face_present_list = [path]

                for j, path2 in enumerate(self.image_paths):
                    if os.path.isdir(path2) or path == path2 or '.DS_Store' in path2 or 'props' in path2:
                        continue
                    prop_file2 = get_or_create_img_props(path2)
                    # check if prop file has list of people in photo
                    if prop_file2.config_exists('people_in_photo'):
                        num_faces2 = prop_file2.get_config('num_faces')  # if peopleinphoto exists, num_faces does
                        people_in_photo = prop_file2.get_config('people_in_photo')
                        for name in checked:
                            # if name is in photo,
                            # we don't need to cross reference the images since we checked the db
                            if name in people_in_photo:
                                continue
                        img2 = face_recognition.load_image_file(path2)
                    else:  # people_in_photo prop doesn't exist
                        print(path2)
                        img2 = face_recognition.load_image_file(path2)
                        img2_encodings = face_recognition.face_encodings(img2)
                        if prop_file2.config_exists('num_faces'):
                            num_faces2 = prop_file2.get_config('num_faces')
                            prop_file2.set_config('people_in_photo', ['unknown' for i in range(num_faces2)])
                        else:
                            num_faces2 = len(img2_encodings)
                            prop_file2.set_config('people_in_photo', ['unknown' for i in range(num_faces2)])

                    if not num_faces2:  # if no faces skip
                        prop_file2.set_config('num_faces', 0)
                        prop_file2.set_config('people_in_photo', [])
                        continue

                    img_encoding2 = face_recognition.face_encodings(img2)[0]
                    results = face_recognition.compare_faces([face_encodings[0]], img_encoding2)

                    if results[0] and path2 not in face_present_list:
                        face_present_list.append(path2)

                if len(face_present_list) > 1:
                    face_detected = True

                face_recognition_view = UnknownFaceView(self.parent, self.controller, face_present_list, face_encodings[0])
                self.controller.wait_window(face_recognition_view.top)

                if not face_detected:
                    face_recognition_view = UnknownFaceView(self.parent, self.controller, [])
                    self.controller.wait_window(face_recognition_view.top)

        if len(db_faces_found):
            known_face_view = KnownFaceView(self.parent, self.controller, db_faces_found)
            self.controller.wait_window(known_face_view.top)


class Grid(tk.Frame):
    # This page displays when users first startup program and/or when configurations aren't set
    def __init__(self, parent, controller, img_paths):
        tk.Frame.__init__(self, parent)
        self.img_paths = img_paths
        self.images = []  # image objects from frontend.components.GalleryImage
        self.thumbnails = []  # label objects created from image objects

    def build(self):
        entries = self.img_paths

        if len(entries):
            img_path = entries[0]
            img = GalleryImage(img_path)
            self.images.append(img)

            for entry in entries[1:]:
                img_path = entry
                img = GalleryImage(img_path)
                self.images.append(img)

        if len(self.images):
            # sort images from newest to oldest
            self.populate_grid()

    def populate_grid(self):
        nc = GALLERY_COL  # number of columns
        idx = 0

        self.thumbnails = []  # photo labels

        while True:
            try:
                img_obj = self.images[idx]
                img = ImageTk.PhotoImage(img_obj.img)
            except IndexError:
                # in case images list empty
                break
            # create label using img obj image
            lbl = tk.Label(self, image=img)
            lbl.img = img
            lbl.grid(row=idx // nc, column=idx % nc, padx=5)  # place image in grid
            # add onclick listeners to each thumbnail to open full image

            self.thumbnails.append(lbl)
            idx += 1

        # Display

    def get_thumbnails(self):
        return self.thumbnails

    def get_images(self):
        return self.images


class GalleryImage:
    def __init__(self, path):
        self.path = path
        self.img = Image.open(self.path)
        self.height = self.img.height
        self.width = self.img.width
        self.format = self.img.format
        self.img.thumbnail((GALLERY_CARD_SIZE, GALLERY_CARD_SIZE))


class FaceDialog(tk.Frame):
    # This page displays when users first startup program and/or when configurations aren't set
    def __init__(self, parent, controller, img_paths, face_encoding):
        tk.Frame.__init__(self, parent)
        self.face_encoding = face_encoding
        self.parent = parent
        self.img_paths = img_paths
        self.persons_name = tk.StringVar()
        self.lbl = tk.Label(self, text=f"{len(img_paths)} images detected with matching faces.")
        self.lbl2 = tk.Label(self, text=f"Enter name of person:")
        self.entry = tk.Entry(self, textvariable=self.persons_name)
        self.confirm_button = tk.Button(self, text=f"Confirm", command=lambda: self.confirm())

        self.lbl.pack()
        self.lbl2.pack()
        self.entry.pack()
        self.confirm_button.pack()
        self.config(width=GALLERY_CARD_SIZE * GALLERY_ROWS * 0.25, bg='grey')

    def confirm(self):
        # push face encoding to db
        persons_name = self.persons_name.get()
        db = db_adapter.Adapter()
        db.add_face_encoding(persons_name, self.face_encoding)
        for path in self.img_paths:

            prop_file = get_or_create_img_props(path)
            people_detected_list = prop_file.get_config('people_in_photo')
            # find first occurrence of unknown face
            idx = people_detected_list.index('unknown')
            people_detected_list[idx] = self.persons_name.get()
            prop_file.set_config('people_in_photo', people_detected_list)
            self.parent.destroy()
            self.parent.update()

def get_or_create_img_props(path):
    # creates a properties file for an image
    img_filename = path.split('/')[-1]
    config_filename = f'.{os.path.splitext(img_filename)[0]}'
    config_path = f'{IMG_PROP_DIR}/{config_filename}'
    config_file = Config.Config(config_path)
    return config_file