import logging
from api.controllers.group_controller import GroupController
from bot import bot

logger = logging.getLogger(__name__)

def observe_member_update(message):
    chat_id = str(message.chat.id)
    user = message.new_chat_member  # Обрабатываем только новые добавления

    # Получаем информацию о группе из базы данных
    group_controller = GroupController(chat_id)
    group_result = group_controller.get()
    group = group_result["group"]
    hello_message = group.hello_message

    if not hello_message:
        return

    if not user:
        bot.send_message(chat_id, f"{hello_message}")
        return

    try:
        logger.debug(
            f"Обработка нового участника в группе {chat_id}. Пользователь: {user.id if user else 'Неизвестен'}")

        if not group_result["success"]:
            logger.warning(f"Не удалось получить информацию о группе {chat_id}: {group_result['error']}")

        # Отправляем приветственное сообщение для нового участника
        bot.send_message(chat_id, f"{hello_message}, {user.username or user.first_name or 'друг'}!")
        logger.info(
            f"Приветственное сообщение отправлено для {user.username or user.first_name or 'Неизвестного'} в группе {chat_id}.")
    except Exception as e:
        logger.error(f"Ошибка обработки нового участника в группе {chat_id}: {e}")
