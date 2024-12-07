from .base_model import BaseModel

class Group(BaseModel):
    def __init__(self, group_id, title=None, description=None, owner_id=None, owner_username=None, settings=None, hello_message=None):
        from . import Settings
        self.group_id = group_id
        self.title = title
        self.description = description
        self.owner_id = owner_id
        self.owner_username = owner_username
        self.hello_message = hello_message
        self.settings = settings if settings else Settings()

    @classmethod
    def from_telegram_chat(cls, chat, settings=None):
        from . import Settings
        from bot import bot

        owner_id = "Неизвестен"
        owner_username = None

        try:
            admins = bot.get_chat_administrators(chat.id)

            for admin in admins:
                if admin.status == 'creator':
                    owner_id = admin.user.id
                    owner_username = admin.user.username
                    break
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Ошибка получения создателя группы {chat.id}: {e}")

        # Возвращаем объект группы
        return cls(
            group_id=chat.id,
            title=chat.title,
            description=chat.description or "Нет описания",
            owner_id=owner_id,
            owner_username=owner_username,
            settings=settings or Settings()
        )