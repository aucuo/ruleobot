from .base_model import BaseModel

class Settings(BaseModel):
    def __init__(self, spam_filter=True, profanity_filter=True, caps_filter=True, links_filter=True, ai_filter=True, small_talk=False):
        self.spam_filter = spam_filter
        self.profanity_filter = profanity_filter
        self.caps_filter = caps_filter
        self.links_filter = links_filter
        self.ai_filter = ai_filter
        self.small_talk = small_talk
