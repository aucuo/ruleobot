from firebase_config import firebase_db
from api.models import Warn
import logging

logger = logging.getLogger(__name__)

class WarnController:
    def __init__(self, group_id, user_id):
        self.user_id = user_id
        self.db = firebase_db.child("groups").child(group_id).child("members").child(user_id).child("warns")

    def post(self, warn):
        warn_data = warn.to_dict()

        try:
            warn_ref = self.db.push()  # Генерируем уникальный ID для варна
            warn_ref.set(warn_data)  # Сохраняем данные варна
            return {"success": True, "message": "Предупреждение успешно добавлено"}
        except Exception as e:
            logger.error(f"Ошибка добавления предупреждения для пользователя {self.user_id}: {e}")
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

    def clear(self):
        try:
            self.db.delete()  # Удаляем узел для предупреждений
            return {"success": True, "message": f"Все предупреждения для '{self.user_id}' сброшены."}
        except Exception as e:
            logger.error(f"Ошибка сброса предупреждений для '{self.user_id}': {e}")
            return {"success": False, "error": str(e)}