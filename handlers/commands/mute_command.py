from telebot.types import Message
from api.controllers.group_controller import GroupController
from api.models import Mute
from bot import bot
from datetime import datetime, timedelta, timezone
from utils import rus_endings
import logging

logger = logging.getLogger(__name__)

def mute_command(message: Message):
    chat_id = str(message.chat.id)
    admin_username = str(message.from_user.username)

    # Разбираем команду
    command_parts = message.text.split(maxsplit=3)
    if len(command_parts) < 3:
        bot.send_message(chat_id, "❌ Формат команды: /mute @username <минуты> <причина>")
        return

    target_username = command_parts[1].strip('@')
    try:
        mute_duration = int(command_parts[2])
    except ValueError:
        bot.send_message(chat_id, "❌ Укажите корректное количество минут.")
        return

    mute_reason = command_parts[3] if len(command_parts) > 3 else "Без причины"

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

        if mute_status["is_muted"]:
            bot.send_message(
                chat_id,
                f"❌ Пользователь @{target_username} уже имеет активный мут до {mute_status['mute_until']}."
            )
            return

        # Создаём запись о муте
        mute_until = datetime.now(timezone.utc) + timedelta(minutes=mute_duration)
        mute = Mute(
            mute_id=None,
            reason=mute_reason,
            mute_until=mute_until.isoformat(),
            issued_by=admin_username,
        )
        mute_controller.post(mute)

        # Формируем правильное окончание
        minute_word = rus_endings(mute_duration, "минута", "минуты", "минут")

        bot.send_message(
            chat_id,
            f"✅ Пользователь @{target_username} был замьючен на {mute_duration} {minute_word}.\nПричина: {mute_reason}"
        )
        logger.info(f"Мут для пользователя {target_user_id} успешно добавлен.")
    except Exception as e:
        bot.send_message(chat_id, "❌ Произошла ошибка при выполнении команды.")
        logger.error(f"Ошибка выполнения команды /mute: {e}")
