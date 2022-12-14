# CSC664 Final Project

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



## Run Program
```shell
foo@bar:CSC_664$ python3 main.py
```

## Using the Program
### Configuration
Set the directory configurations to the subdirectories in the dataset folder.
 [![image alt text](https://i.imgur.com/yF2TKy1.png)](anchor link)
 If they are set already in from the root/.config file, the main screen will pop up automatically

## The UI
# Creating an event
 [![image alt text](https://i.imgur.com/3pFehXK.png)](anchor link)
This is where events are created. After typing your event description and entering the date, Click confirm and wait for string analysis.
If you are satisfied with the analysis, click Create Event. 

 &nbsp;
 &nbsp; 
 &nbsp;
&nbsp;



 [![image alt text](https://i.imgur.com/DRIQ9S7.png)](anchor link)
If a face is detected in an image that may be associated with your event, you can either enter the person's name or skip it. 

This feature is helpful for finding this person in images later. A feature to see all occurences of the people in saved events was being built, but wasn't completed in time

 &nbsp;
 &nbsp; 
 &nbsp;
&nbsp;

 [![image alt text](https://imgur.com/A0Tmy6Q.png)](anchor link)
Once file analysis is complete, you can see the files that program scraped. 
For image files, clicking them will remove them from being logged in the event creation. 

For other files, clicking them
and pressing the backspace key, will remove them. You can also open them by double-clicking.

 &nbsp;
 &nbsp; 
 &nbsp;
&nbsp;

 [![image alt text](https://imgur.com/0pb99xK.png)](anchor link)
Once the event is created, you can view it in the events tab (you may need to restart the program). The entries in the 'Files'
column can be navigated by using the arrow keys. The right arrow will let you see the overflow keys. Press enter or double click the file path to open the file


   
## Work Left to Do
