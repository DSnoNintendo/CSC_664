from app.constants import MUSIC_DIR
from pathlib import Path
import numpy as np
import eyed3
import os


class MP3:
    def __init__(self):
        self.file_list = []
        self.list_chunks = []
        self.acceptable_filetypes = ['.mp3']
        self.event_files = []

        for dirpath, dirs, files in os.walk(MUSIC_DIR, topdown=False):
            for file in files:
                path = os.path.join(dirpath, file)
                if Path(file).suffix in self.acceptable_filetypes:
                    self.file_list.append(path)

    def start(self, query, file_dict):
        for path in self.list_chunks:
            if Path(path).suffix == '.mp3':
                mp3 = eyed3.load(path)
                if mp3.tag.artist in query['people']:
                    file_dict['MP3'].append(path)

    def split_files(self, n):
        try:
            lists = np.split(np.array(self.file_list), n)
            for l in lists:
                self.list_chunks.append(np.array(l).tolist())
        except:
            lists = np.split(np.array(self.file_list), 1)
            for l in lists:
                self.list_chunks.append(np.array(l).tolist())
