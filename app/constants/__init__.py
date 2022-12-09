import os
from app.helpers import Config
from pathlib import Path
from screeninfo import get_monitors

# DIRECTORY CONSTANTS
CWD = os.path.abspath(Path(os.getcwd())) # current working directory
CONFIG_FILENAME = '.config'
CONFIG_PATH = f"{CWD}/{CONFIG_FILENAME}"
CONFIG_FILE = Config.Config(CONFIG_PATH)

# WINDOW CONSTANTS
WINDOW_WIDTH = get_monitors()[0].width
WINDOW_HEIGHT = get_monitors()[0].height

# Config settings required for program to run correctly
REQUIRED_CONFIGS = ['gallery_dir',  # IMAGE GALLERY DIRECTORY
                    'document_dir' # Directory for Documents
                    #
                    ]

GALLERY_DIR = CONFIG_FILE.get_config('gallery_dir')
GALLERY_CARD_SIZE = 150
GALLERY_ROWS = 3
GALLERY_COL = 3
GALLERY_IMG_SIZE = (100,100)

DOCUMENT_DIR = CONFIG_FILE.get_config('document_dir')
MUSIC_DIR = CONFIG_FILE.get_config('music_dir')

IMG_PROP_DIR = f"{GALLERY_DIR}/.props"
if not os.path.exists(IMG_PROP_DIR):
    os.makedirs(IMG_PROP_DIR)

FACES_DIR = f'{CWD}/images/.faces/'  # store faces in hidden folder
if not os.path.exists(FACES_DIR):
    os.makedirs(FACES_DIR)
FACE_DETECTOR = f'{FACES_DIR}/haarcascade-frontalface_default.xml'

MONTH_DICT = {
    1: "January",
    2: "February",
    3: "March",
    4: "April",
    5: "May",
    6: "June",
    7: "July",
    8: "August",
    9: "September",
    10: "October",
    11: "November",
    12: "December"
}
