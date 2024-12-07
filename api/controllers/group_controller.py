from api.controllers.member_controller import MemberController
from api.controllers.settings_controller import SettingsController
from firebase_config import firebase_db
from api.models import Group, Settings
import logging

logger = logging.getLogger(__name__)

class GroupController:
    def __init__(self, group_id):
        self.group_id = str(group_id)
        self.db = firebase_db.child("groups").child(str(group_id))

    def settings(self):
        return SettingsController(self.group_id)

    def members(self, user_id):
        return MemberController(self.group_id, user_id)

    def post(self, group: Group):
        group_data = group.to_dict()

        try:
            group_ref = self.db
            group_ref.update(group_data)
            group_ref.child("settings").set(group.settings.to_dict())

            return {"success": True, "message": f"Группа '{group.title}' успешно добавлена!"}
        except Exception as e:
            logger.error(f"Ошибка добавления группы: {e}")
            return {"success": False, "error": str(e)}

    def get(self):
        try:
            group_data = self.db.get()

            if not group_data:
                return {"success": False, "error": f"Группа с ID '{self.group_id}' не найдена."}

            settings_data = self.db.child("settings").get()
            group = Group.from_dict({
                "group_id": self.group_id,
                **group_data,
                "settings": Settings.from_dict(settings_data) if settings_data else Settings()
            })

            return {"success": True, "group": group}
        except Exception as e:
            logger.error(f"Ошибка получения группы: {e}")
            return {"success": False, "error": str(e)}

    @staticmethod
    def get_all():
        try:
            groups_ref = firebase_db.child("groups")
            groups_data = groups_ref.get()

            if not groups_data:
                return {"success": True, "groups": []}

            groups = []
            for group_id, group_details in groups_data.items():
                settings_data = group_details.pop("settings", {})
                group = Group.from_dict({
                    "group_id": group_id,
                    **group_details,
                    "settings": Settings.from_dict(settings_data) if settings_data else Settings()
                })
                groups.append(group)

            return {"success": True, "groups": groups}
        except Exception as e:
            logger.error(f"Ошибка получения списка групп: {e}")
            return {"success": False, "error": str(e)}
