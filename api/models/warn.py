from .base_model import BaseModel

class Warn(BaseModel):
    def __init__(self, warn_id, reason, date=None, issued_by='system'):
        self.warn_id = warn_id
        self.reason = reason
        self.date = date
        self.issued_by = issued_by
