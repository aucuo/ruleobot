from .base_model import BaseModel

class Member(BaseModel):
    def __init__(self, user_id, username=None, first_name=None, last_name=None, message_count=0):
        self.user_id = user_id
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.message_count = message_count
