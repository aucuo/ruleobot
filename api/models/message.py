from .base_model import BaseModel

class Message(BaseModel):
    def __init__(self, message_id, text, date=None):
        self.message_id = message_id
        self.text = text
        self.date = date
