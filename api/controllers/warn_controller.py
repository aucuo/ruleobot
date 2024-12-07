from firebase_config import firebase_db
from api.models import Warn
import logging

logger = logging.getLogger(__name__)

class WarnController:
    def __init__(self, group_id, user_id):
        self.user_id = user_id
        self.db = firebase_db.child("groups").child(group_id).child("members").child(user_id).child("warns")

    def post(self, warn: Warn):
        warn_data = warn.to_dict()

        try:
            warn_ref = self.db.push()
            warn_ref.set(warn_data)
            return {"success": True, "message": f"Предупреждение успешно добавлено для '{self.user_id}'."}
        except Exception as e:
            logger.error(f"Ошибка добавления предупреждения для '{self.user_id}': {e}")
            return {"success": False, "error": str(e)}

    def get(self):
        try:
            warns_data = self.db.get()

            if not warns_data:
                return {"success": True, "warns": []}

            warns = [Warn.from_dict({"warn_id": key, **value}) for key, value in warns_data.items()]
            return {"success": True, "warns": warns}
        except Exception as e:
            logger.error(f"Ошибка получения предупреждений для '{self.user_id}': {e}")
            return {"success": False, "error": str(e)}
