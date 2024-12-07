from datetime import datetime

from telebot.types import Message
from api.controllers.group_controller import GroupController
from bot import bot
from utils import admin_required
import logging

logger = logging.getLogger(__name__)

@admin_required
def unwarn_command(message: Message):
    chat_id = str(message.chat.id)

    # Разбираем параметры команды
    command_parts = message.text.split(maxsplit=2)
    if len(command_parts) < 2:
        bot.send_message(chat_id, "❌ Формат команды: /unwarn @username [-all]")
        return

    target_username = command_parts[1].strip('@')
    flag_all = len(command_parts) > 2 and command_parts[2] == "-all"

    try:
        group_controller = GroupController(chat_id)
        member_controller = group_controller.members(None)

        # Ищем участника по username
        member_result = member_controller.get_by_username(target_username)
        if not member_result["success"]:
            bot.send_message(chat_id, f"❌ {member_result['error']}")
            return

        target_user_id = member_result["user_id"]

        # Работаем с предупреждениями
        warn_controller = group_controller.members(target_user_id).warns()

        if flag_all:
            clear_result = warn_controller.clear()
            if clear_result["success"]:
                bot.send_message(
                    chat_id,
                    f"✅ Все предупреждения пользователя @{target_username} успешно сняты."
                )
                logger.info(f"Все предупреждения сняты с пользователя {target_user_id} в группе {chat_id}.")
            else:
                bot.send_message(
                    chat_id,
                    f"❌ Ошибка снятия предупреждений: {clear_result['error']}."
                )
                logger.error(f"Ошибка снятия предупреждений для пользователя {target_user_id}: {clear_result['error']}")
        else:
            warns_result = warn_controller.get()
            if not warns_result["success"]:
                bot.send_message(chat_id, f"❌ Не удалось получить предупреждения: {warns_result['error']}")
                return

            warns = warns_result.get("warns", [])
            if not warns:
                bot.send_message(chat_id, f"❌ У пользователя @{target_username} нет активных предупреждений.")
                return

            # Сортируем предупреждения по дате
            sorted_warns = sorted(
                warns,
                key=lambda w: datetime.fromisoformat(w.date) if w.date else datetime.min,
                reverse=True
            )
            last_warn = sorted_warns[0]

            logger.info(last_warn.warn_id)

            delete_result = warn_controller.delete(last_warn.warn_id)
            if delete_result["success"]:
                remaining_warns = len(sorted_warns) - 1
                bot.send_message(
                    chat_id,
                    f"✅ Последнее предупреждение пользователя @{target_username} успешно снято.\n"
                    f"Осталось предупреждений: {remaining_warns}"
                )
                logger.info(f"Последнее предупреждение снято с пользователя {target_user_id} в группе {chat_id}.")
            else:
                bot.send_message(
                    chat_id,
                    f"❌ Ошибка снятия предупреждения: {delete_result['error']}."
                )
                logger.error(f"Ошибка снятия предупреждения для пользователя {target_user_id}: {delete_result['error']}")

    except Exception as e:
        logger.error(f"Ошибка выполнения команды /unwarn: {e}")
        bot.send_message(chat_id, "❌ Произошла ошибка при выполнении команды.")
