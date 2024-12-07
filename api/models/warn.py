from datetime import datetime
from .base_model import BaseModel

class Warn(BaseModel):
    def __init__(self, warn_id, reason, date=datetime.now().isoformat(), issued_by='ruleobot'):
        self.warn_id = warn_id
        self.reason = reason
        self.date = date
        self.issued_by = issued_by
