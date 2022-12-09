from . import Config
import tkinter as tk
import nltk
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
from nltk.tag.stanford import StanfordNERTagger


def make_label(master, x, y, h, w, *args, **kwargs):
    f = tk.Frame(master, height=h, width=w)
    f.pack_propagate(0) # don't shrink
    f.place(x=x, y=y)
    label = tk.Label(f, *args, **kwargs)
    label.pack(fill=tk.BOTH, expand=1)
    return label


def get_unique(s):
    from app.constants import CWD

    st = StanfordNERTagger(f'{CWD}/dependencies/all.3class.distsim.crf.ser.gz', f'{CWD}/dependencies/stanford-ner.jar')
    dict = {
        'people': [],
        'location': "",
    }

    for sent in nltk.sent_tokenize(s):
        tokens = nltk.tokenize.word_tokenize(sent)
        tags = st.tag(tokens)
        print(tags)
        for tag in tags:
            if tag[1] == 'PERSON':
                dict['people'].append(tag[0])
            elif tag[1] == 'LOCATION':
                dict['location'] = tag[0]

    return dict