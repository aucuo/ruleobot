from .base_model import BaseModel

class Mute(BaseModel):
    def __init__(self, mute_id, reason, mute_until, issued_by='system'):
        self.mute_id = mute_id
        self.reason = reason
        self.mute_until = mute_until
        self.issued_by = issued_by
