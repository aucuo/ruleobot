from telebot.types import Message
from api.controllers.group_controller import GroupController
from api.models import Group
from bot import bot
import logging

logger = logging.getLogger(__name__)

def update_command(message: Message):
    chat_id = str(message.chat.id)

    try:
        chat = bot.get_chat(chat_id)

        group_controller = GroupController(chat_id)
        group_result = group_controller.get()

        if not group_result["success"]:
            logger.warning(f"Не удалось получить информацию о группе {chat_id}: {group_result['error']}")
            return

        group = group_result["group"]

        updated_group = Group.from_telegram_chat(chat, group.settings)

        update_result = group_controller.post(updated_group)

        if update_result["success"]:
            bot.send_message(chat_id, "✅ Информация о группе успешно обновлена в базе данных.")
            logger.info(f"Информация о группе {chat_id} успешно обновлена в базе данных.")
        else:
            bot.send_message(chat_id, f"❌ Не удалось обновить информацию о группе: {update_result['error']}")
            logger.warning(f"Не удалось обновить информацию о группе {chat_id}: {update_result['error']}")
    except Exception as e:
        logger.error(f"Ошибка обновления информации о группе {chat_id}: {e}")
        bot.send_message(chat_id, "❌ Произошла ошибка при обновлении информации о группе.")
