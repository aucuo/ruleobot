from datetime import datetime, timezone

from firebase_config import firebase_db
from api.models import Mute
import logging

logger = logging.getLogger(__name__)

class MuteController:
    def __init__(self, group_id, user_id):
        self.group_id = str(group_id)
        self.user_id = str(user_id)
        self.db = firebase_db.child("groups").child(self.group_id).child("members").child(self.user_id).child("mutes")

    def post(self, mute: Mute):
        mute_data = mute.to_dict()

        try:
            if mute.mute_id:
                # Перезаписываем существующий мут
                mute_ref = self.db.child(mute.mute_id)
                mute_ref.update(mute_data)
            else:
                # Создаём новый мут
                mute_ref = self.db.push()
                mute_data["mute_id"] = mute_ref.key  # Добавляем mute_id в данные
                mute_ref.set(mute_data)

            return {"success": True, "message": f"Мут успешно добавлен/обновлён для '{self.user_id}'."}
        except Exception as e:
            logger.error(f"Ошибка добавления/обновления мута для '{self.user_id}': {e}")
            return {"success": False, "error": str(e)}

    def get(self):
        try:
            mutes_data = self.db.get()

            if not mutes_data:
                return {"success": True, "mutes": []}

            mutes = [Mute.from_dict({"mute_id": key, **value}) for key, value in mutes_data.items()]
            return {"success": True, "mutes": mutes}
        except Exception as e:
            logger.error(f"Ошибка получения мутов для '{self.user_id}': {e}")
            return {"success": False, "error": str(e)}

    def has_active_mute(self):
        try:
            mutes_result = self.get()
            if not mutes_result["success"]:
                return {"is_muted": False, "error": mutes_result["error"]}

            active_mutes = [
                mute for mute in mutes_result["mutes"]
                if datetime.fromisoformat(mute.mute_until) > datetime.now(timezone.utc)  # Только активные
            ]

            if active_mutes:
                # Находим самый ранний активный мут
                earliest_mute = min(active_mutes, key=lambda m: datetime.fromisoformat(m.mute_until))
                mute_until = datetime.fromisoformat(earliest_mute.mute_until)
                time_remaining = mute_until - datetime.now(timezone.utc)

                return {
                    "is_muted": True,
                    "mute_id": earliest_mute.mute_id,
                    "mute_until": mute_until,
                    "time_remaining": time_remaining,
                    "reason": earliest_mute.reason,
                    "issued_by": earliest_mute.issued_by,
                }

            return {"is_muted": False}
        except Exception as e:
            logger.error(f"Ошибка проверки активного мута для '{self.user_id}' в группе '{self.group_id}': {e}")
            return {"is_muted": False, "error": str(e)}
