from firebase_config import firebase_db
from api.models import Message
import logging

logger = logging.getLogger(__name__)

class MessageController:
    def __init__(self, group_id, user_id):
        self.group_id = str(group_id)
        self.user_id = str(user_id)
        self.db = firebase_db.child("groups").child(self.group_id).child("members").child(self.user_id ).child("messages")

    def post(self, message: Message):
        message_data = message.to_dict()

        try:
            # Устанавливаем message_id как ключ
            message_ref = self.db.child(str(message_data["message_id"]))
            message_ref.set(message_data)  # Используем set для сохранения новых данных
            return {"success": True,
                    "message": f"Сообщение '{message_data['message_id']}' успешно добавлено для участника '{self.user_id}'."}
        except Exception as e:
            logger.error(f"Ошибка добавления сообщения для '{self.user_id}': {e}")
            return {"success": False, "error": str(e)}

    def get(self):
        try:
            messages_data = self.db.get()

            if not messages_data:
                return {"success": True, "messages": []}

            messages = [Message.from_dict({"message_id": key, **value}) for key, value in messages_data.items()]
            return {"success": True, "messages": messages}
        except Exception as e:
            logger.error(f"Ошибка получения сообщений для '{self.user_id}': {e}")
            return {"success": False, "error": str(e)}
