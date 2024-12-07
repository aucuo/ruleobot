from telebot.types import Message
from api.controllers.group_controller import GroupController
from api.models import Mute
from datetime import datetime, timezone
from bot import bot
from utils import admin_required
import logging

logger = logging.getLogger(__name__)

@admin_required
def unmute_command(message: Message):
    chat_id = str(message.chat.id)

    # Разбираем параметры команды
    command_parts = message.text.split(maxsplit=1)
    if len(command_parts) < 2:
        bot.send_message(chat_id, "❌ Формат команды: /unmute @username")
        return

    target_username = command_parts[1].strip('@')

    try:
        # Получаем контроллер группы
        group_controller = GroupController(chat_id)
        member_controller = group_controller.members(None)

        # Ищем участника через username
        member_result = member_controller.get_by_username(target_username)
        if not member_result["success"]:
            bot.send_message(chat_id, f"❌ {member_result['error']}")
            return

        target_user_id = member_result["user_id"]

        # Проверяем наличие активного мута
        mute_controller = group_controller.members(target_user_id).mutes()
        mute_status = mute_controller.has_active_mute()

        if not mute_status["is_muted"]:
            bot.send_message(chat_id, f"❌ У пользователя @{target_username} нет активного мута.")
            logger.info(f"Попытка снять мут с пользователя {target_user_id}, у которого нет активного мута.")
            return

        # Завершаем активный мут
        now = datetime.now(timezone.utc).isoformat()
        mute = Mute(
            mute_id=mute_status["mute_id"],
            reason=mute_status["reason"],
            mute_until=now,  # Завершаем мут немедленно
            issued_by=mute_status["issued_by"]
        )
        result = mute_controller.post(mute)

        if result["success"]:
            bot.send_message(chat_id, f"✅ Мут для пользователя @{target_username} успешно снят.")
            logger.info(f"Мут для пользователя {target_user_id} успешно снят.")
        else:
            bot.send_message(chat_id, f"❌ Ошибка при снятии мута: {result['error']}")
            logger.error(f"Ошибка снятия мута для {target_user_id}: {result['error']}")
    except Exception as e:
        logger.error(f"Ошибка выполнения команды /unmute: {e}")
        bot.send_message(chat_id, f"❌ Произошла ошибка при снятии мута.")
