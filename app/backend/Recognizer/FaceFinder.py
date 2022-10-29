import cv2
import os
import uuid
import face_recognition
from app.backend.utils import randomize_mtime, gallery_as_path_list

# The directory for storing faces,
#                   the image detection file,
#                   and the gallery directory path
#                   were moved to app.constants package. go check it out
from app.constants import FACES_DIR, FACE_DETECTOR, GALLERY_DIR

class FaceFinder:
    # I used your code to create a class called FaceFinder.
    # Learn about Python classes: https://www.w3schools.com/python/python_classes.asp
    # The start function will be run in the background to find faces
    def __init__(self):
        # gallery_as path list function simplified
        self.image_paths = [os.path.join(GALLERY_DIR, f) for f in os.listdir(GALLERY_DIR)]
        self.model = cv2.CascadeClassifier("./haarcascade_frontalface_default.xml")

    def crop_face(self, img, x, y, w, h): # renamed to crop_face
        cropped_image = img[y:y + h, x:x + w]
        return cropped_image

    '''
    def save_image(img):
        cv2.imwrite(f'{self.name}{uuid.uuid4()}.jpg', img)
    '''


    def start(self):
        # since we are loading every path in image_paths, name conventions were changed
        # when running for loops make the first variable singular, since we're looping one by one.
        # ex: for path in self.image_paths instead of for paths
        # it makes reading your code later easier
        for path in self.image_paths:
            # Reads faces
            img = cv2.imread(path)
            faces = self.model.detectMultiScale(img)
            for x, y, width, height in faces:
                # creates rectangle around fouce
                cv2.rectangle(img, (x, y), (x + width, y + height), (0, 255, 255), 2)
                # cropping face image
                face = self.crop_face(img, x, y, width, height)


                '''
                instead of showing the face in a new window we will send a trigger for the gui to display the
                image 
                
                '''


                '''
                # shows face found in new window
                cv2.imshow("Faces Found", face)
                cv2.waitKey(0)
                
                # If face save the image
                if input("Is this a face? Y/N: ").upper() == "Y":
                    save_image(face)
                break
                '''