# handlers/notify_handler.py

import logging
from api.controllers.group_controller import GroupController
from api.models import Group
from bot import bot

logger = logging.getLogger(__name__)

def notify():
    update_message = "⚙️ Бот получил обновление и перезапустился"
    try:
        # Получаем список всех групп из базы данных
        result = GroupController.get_all()

        if not result["success"]:
            logger.error(f"Ошибка получения групп из базы данных: {result['error']}")
            return

        groups = result["groups"]

        if not groups:
            logger.info("Нет доступных групп для уведомления.")
            return

        # Обновление информации о группах и отправка сообщений
        for group in groups:
            try:
                chat = bot.get_chat(group.group_id)

                updated_group = Group.from_telegram_chat(chat, group.settings)

                group_controller = GroupController(group.group_id)
                update_result = group_controller.post(updated_group)

                if update_result["success"]:
                    logger.info(f"Информация о группе {chat.id} успешно обновлена.")
                else:
                    logger.warning(f"Не удалось обновить информацию о группе {chat.id}: {update_result['error']}")

                # Отправляем сообщение в группу
                bot.send_message(chat_id=chat.id, text=update_message)
                logger.info(f"Сообщение успешно отправлено в группу {chat.id}")
            except Exception as e:
                logger.error(f"Ошибка обработки группы {group.group_id}: {e}")

    except Exception as e:
        logger.error(f"Ошибка при выполнении notify_update_to_groups: {e}")
