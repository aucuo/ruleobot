from telebot.types import Message
from api.controllers.group_controller import GroupController
import logging

from bot import bot

logger = logging.getLogger(__name__)

def info_command(message: Message):
    chat_id = str(message.chat.id)

    # Получение контроллера группы
    group_controller = GroupController(chat_id)
    group_result = group_controller.get()

    if not group_result["success"]:
        error_message = f"Ошибка: {group_result['error']}"
        logger.error(error_message)
        bot.send_message(chat_id, error_message)
        return

    group = group_result["group"]

    # Получение списка участников
    member_controller = group_controller.members(None)
    members_result = member_controller.get_all()

    if not members_result["success"]:
        member_count = "не удалось определить"
        logger.error(f"Ошибка получения участников: {members_result['error']}")
    else:
        members = members_result["members"]
        member_count = len(members)

    # Формирование текста ответа
    info_text = (
        f"📋 Информация о группе:\n"
        f"ID: {group.group_id}\n"
        f"Название: {group.title}\n"
        f"Описание: {group.description or 'Нет описания'}\n"
        f"Создатель: @{group.owner_username or 'Неизвестно'}\n"
        f"Участников: {member_count}\n\n"
        f"Приветственное сообщение: {group.hello_message or 'Нету'}\n\n"
        f"⚙️ Настройки:\n"
        f"Фильтр спама: {'✅' if group.settings.spam_filter else '❌'}\n"
        f"Фильтр нецензурной лексики: {'✅' if group.settings.profanity_filter else '❌'}\n"
        f"Фильтр капслока: {'✅' if group.settings.caps_filter else '❌'}\n"
        f"Фильтр ссылок: {'✅' if group.settings.links_filter else '❌'}"
    )

    # Отправка информации
    bot.send_message(chat_id, info_text)
