import logging
from api.controllers.group_controller import GroupController
from api.models import Group
from bot import bot

logger = logging.getLogger(__name__)

def observe_group_info(message):
    chat_id = message.chat.id
    try:
        chat = bot.get_chat(chat_id)
        group = Group.from_telegram_chat(chat)

        updated_group = Group.from_telegram_chat(chat, group.settings)

        group_controller = GroupController(group.group_id)
        update_result = group_controller.post(updated_group)

        if update_result["success"]:
            logger.info(f"Информация о группе {chat.id} успешно обновлена.")
        else:
            logger.warning(f"Не удалось обновить информацию о группе {chat.id}: {update_result['error']}")

    except Exception as e:
        logger.error(f"Ошибка обновления информации о группе {chat_id}: {e}")
