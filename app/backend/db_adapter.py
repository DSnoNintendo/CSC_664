from tinydb import TinyDB, Query
from app.constants import CWD

class Adapter:
    def __init__(self):
        self.face_db = TinyDB(f'{CWD}/app/backend/face_encodings.json')
        self.event_db = TinyDB(f'{CWD}/app/backend/events.json')

    def add_face_encoding(self, name, encoding):
        encoding = encoding.tolist()
        self.face_db.insert({name: encoding})

    def get_all_encodings(self):
        print(self.face_db.all())
        return self.face_db.all()

    def get_events(self, date):
        event = Query()
        return self.event_db.search(event['date'] == date)

    def get_all_events(self):
        events = self.event_db.all()
        return events

    def commit_event(self, event_dict):
        self.event_db.insert(event_dict)
        self.refresh()
        return True

    def refresh(self):
        self.event_db = TinyDB(f'{CWD}/app/backend/events.json')


'''
{ 'date' : [{'event name' : files}]}
'''
