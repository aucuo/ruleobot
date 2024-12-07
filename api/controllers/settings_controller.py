from firebase_config import firebase_db
from api.models import Settings
import logging

logger = logging.getLogger(__name__)

class SettingsController:
    def __init__(self, group_id):
        self.group_id = group_id
        self.db = firebase_db.child("groups").child(group_id).child("settings")

    def get(self):
        try:
            settings_data = self.db.get()

            if not settings_data:
                return {"success": False, "error": f"Настройки для группы '{self.group_id}' не найдены."}

            settings = Settings.from_dict(settings_data)
            return {"success": True, "settings": settings}
        except Exception as e:
            logger.error(f"Ошибка получения настроек для группы '{self.group_id}': {e}")
            return {"success": False, "error": str(e)}

    def update(self, settings: Settings):
        settings_data = settings.to_dict()

        try:
            self.db.set(settings_data)
            return {"success": True, "message": f"Настройки для группы '{self.group_id}' успешно обновлены."}
        except Exception as e:
            logger.error(f"Ошибка обновления настроек для группы '{self.group_id}': {e}")
            return {"success": False, "error": str(e)}
