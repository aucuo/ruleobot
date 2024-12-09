from .base_model import BaseModel
from datetime import datetime

class Member(BaseModel):
    def __init__(self, user_id, username=None, first_name=None, last_name=None, message_count=0, entry_date=None):
        self.user_id = user_id
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.message_count = message_count
        self.entry_date = str(entry_date) or str(datetime.now())
