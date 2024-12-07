from api.controllers.message_controller import MessageController
from api.controllers.mute_controller import MuteController
from api.controllers.warn_controller import WarnController
from firebase_config import firebase_db
from api.models import Member
import logging

logger = logging.getLogger(__name__)

class MemberController:
    def __init__(self, group_id, user_id=None):
        self.group_id = str(group_id)
        self.user_id = str(user_id)
        self.db = firebase_db.child("groups").child(self.group_id).child("members")

    def messages(self):
        return MessageController(self.group_id, self.user_id)

    def warns(self):
        return WarnController(self.group_id, self.user_id)

    def mutes(self):
        return MuteController(self.group_id, self.user_id)

    def post(self, member: Member):
        member_data = member.to_dict()

        try:
            member_ref = self.db.child(self.user_id)
            member_ref.update(member_data)

            return {"success": True, "message": f"Участник '{member.username}' успешно добавлен или обновлен!"}
        except Exception as e:
            logger.error(f"Ошибка добавления/обновления участника '{self.user_id}' в группе '{self.group_id}': {e}")
            return {"success": False, "error": str(e)}

    def get(self):
        try:
            member_ref = self.db.child(self.user_id)
            member_data = member_ref.get()

            if not member_data:
                return {"success": False, "error": f"Участник с ID '{self.user_id}' не найден в группе '{self.group_id}'."}

            member = Member.from_dict({
                "user_id": self.user_id,
                **member_data
            })

            return {"success": True, "member": member}
        except Exception as e:
            logger.error(f"Ошибка получения участника '{self.user_id}' в группе '{self.group_id}': {e}")
            return {"success": False, "error": str(e)}

    def get_by_username(self, username):
        try:
            members_ref = firebase_db.child("groups").child(self.group_id).child("members")

            query_result = members_ref.order_by_child("username").equal_to(username).get()

            if not query_result:
                return {"success": False, "error": f"Пользователь с username '{username}' не найден."}

            for user_id, user_data in query_result.items():
                return {"success": True, "user_id": user_id, "user_data": user_data}

        except Exception as e:
            logger.error(f"Ошибка поиска пользователя с username '{username}': {e}")
            return {"success": False, "error": str(e)}

    def get_all(self):
        """
        Возвращает список всех участников группы.
        """
        try:
            members_data = self.db.get()
            if not members_data:
                return {"success": True, "members": []}

            members = [
                Member.from_dict({"user_id": user_id, **user_data})
                for user_id, user_data in members_data.items()
            ]
            return {"success": True, "members": members}
        except Exception as e:
            logger.error(f"Ошибка получения участников для группы '{self.group_id}': {e}")
            return {"success": False, "error": str(e)}
