import logging
from telebot.types import Message
from api.controllers.group_controller import GroupController

from bot import bot
from utils import admin_required

logger = logging.getLogger(__name__)

@admin_required
def hello_command(message: Message):
    chat_id = str(message.chat.id)

    # Извлекаем новое сообщение из команды
    command_parts = message.text.split(maxsplit=1)

    # Проверяем, указано ли новое приветственное сообщение
    new_hello_message = command_parts[1].strip() if len(command_parts) > 1 else None

    # Если сообщение пустое или не указано, приветственное сообщение отключается
    if not new_hello_message:
        new_hello_message = None  # Устанавливаем приветственное сообщение в None

    try:
        # Обновляем информацию в базе данных
        group_controller = GroupController(chat_id)
        group_result = group_controller.get()

        if not group_result["success"]:
            bot.send_message(chat_id, f"❌ Не удалось получить информацию о группе: {group_result['error']}")
            return

        group = group_result["group"]
        group.hello_message = new_hello_message

        update_result = group_controller.post(group)

        if update_result["success"]:
            if new_hello_message:
                bot.send_message(chat_id, f"✅ Приветственное сообщение обновлено на: \"{new_hello_message}\"")
                logger.info(f"Приветственное сообщение группы {chat_id} обновлено на \"{new_hello_message}\".")
            else:
                bot.send_message(chat_id, "✅ Приветственное сообщение успешно отключено.")
                logger.info(f"Приветственное сообщение группы {chat_id} отключено.")
        else:
            bot.send_message(chat_id, f"❌ Ошибка обновления приветственного сообщения: {update_result['error']}")
    except Exception as e:
        logger.error(f"Ошибка изменения приветственного сообщения в группе {chat_id}: {e}")
        bot.send_message(chat_id, "❌ Произошла ошибка при изменении приветственного сообщения.")
