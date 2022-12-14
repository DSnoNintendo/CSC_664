from app.constants import DOCUMENT_DIR
import os
import numpy as np
from pathlib import Path
import PyPDF2
from PIL import Image
from pytesseract import pytesseract


class TextDocument:
    def __init__(self):
        self.file_list = []
        self.list_chunks = []
        self.acceptable_filetypes = ['.pdf', 'txt', '.jpg', '.png']
        self.event_files = []

        for dirpath, dirs, files in os.walk(DOCUMENT_DIR, topdown=False):
            for file in files:
                path = os.path.join(dirpath, file)
                if Path(file).suffix in self.acceptable_filetypes:
                    self.file_list.append(path)

    def start(self, query):
        for path in self.file_list:
            extension = Path(path).suffix

            if extension == '.pdf':
                pdfReader = PyPDF2.PdfFileReader(open(path, 'rb'), strict=False)
                for i in range(pdfReader.numPages):
                    pageObj = pdfReader.getPage(i)
                    page_txt = pageObj.extractText().upper()
                    if all(substring in page_txt for substring in query['required']):
                        self.event_files.append(path)

            elif extension == '.txt':
                page_txt = open("demofile.txt", "r").read()
                if all(substring in page_txt for substring in query['required']):
                    self.event_files.append(path)

            elif extension == '.jpg' or extension == '.png':
                img = Image.open(path)
                text = pytesseract.image_to_string(img)
                if all(substring in text for substring in query['required']):
                    self.event_files.append(path)


        return self.event_files