# CSC664 Multimedia Gallery

The goal of this project is to create a sandbox UI to group different types of multimedia by events

Ideally, if a photo gallery has pictures and videos of a person named David, all photos with David should be grouped 
together. If a photo with David is selected in the photo gallery text messages between our hypothetical user and David 
should be easily accessible through this UI, as close to the date the photo was taken as possible 

# How to use

## Install requirements
```shell
foo@bar:CSC_664$ pip install -r requirements.txt
```
install NLTK Data
```shell
foo@bar:CSC_664$ python -m nltk.downloader popular
```


This will download a maximum of 10 images to a folder named gallery located in the directory.
(The default directory is ./gallery/ and the default maximum is 10)

You can download pictures of multiple people or groups of people to have more images for facial recognition

## Run Program
```shell
foo@bar:CSC_664$ python3 main.py
```

Select directory containing images you want the UI to display. This filepath will be stored in a hidden file 
   ```.config``` for future refernce. Press confirm and your images will display
   
## Work Left to Do
1. Implement facial recognition
2. Allow users to click photoa to open image in larger view
3. Grouping by photo location
4. Sort by New to Old and Old to New
5. Implement text message integration