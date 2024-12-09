from datetime import datetime, timezone, timedelta

from api.controllers import MuteController, MemberController
from api.models import Message, Member
from bot import bot
from config import logger
from handlers import message_validator


def message_observer(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    username = message.from_user.username or "Неизвестный"
    first_name = message.from_user.first_name or ""
    last_name = message.from_user.last_name or ""
    text = message.text or ""

    try:
        # Логирование сообщения
        logger.info(f"[{chat_id}] {username} ({user_id}): {text}")

        # Проверяем мут через MuteController
        mute_controller = MuteController(chat_id, user_id)
        mute_status = mute_controller.has_active_mute()

        if mute_status["is_muted"]:
            time_remaining = str(timedelta(seconds=int(mute_status["time_remaining"].total_seconds())))
            bot.reply_to(
                message,
                f"❌ Вы замьючены до {mute_status['mute_until'].strftime('%Y-%m-%d %H:%M:%S UTC')}.\n"
                f"Осталось времени: {time_remaining}.\n"
                f"Причина: {mute_status['reason']}.\n"
                f"Мут выдан: @{mute_status['issued_by']}."
            )
            bot.delete_message(chat_id, message.message_id)
            logger.info(f"Удалено сообщение пользователя {user_id} в группе {chat_id} из-за активного мута.")
            return  # Сообщение удалено, больше ничего не выполняем

        # Создаём или обновляем информацию о пользователе в БД
        member_controller = MemberController(chat_id, user_id)
        member = Member(
            user_id=user_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            message_count=1,
            entry_date=datetime.now()
        )

        # Проверяем, есть ли пользователь в базе
        member_result = member_controller.get()
        if member_result["success"]:
            # Если пользователь существует, увеличиваем счётчик сообщений
            existing_member = member_result["member"]
            member.message_count = existing_member.message_count + 1 if hasattr(existing_member, "message_count") else 1

        # Добавляем или обновляем пользователя в базе данных
        member_controller.post(member)

        # Сохранение сообщения в БД (если не удалено)
        user_message = Message(
            message_id=message.message_id,
            text=text,
            date=datetime.now(timezone.utc).isoformat()
        )
        member_controller.messages().post(user_message)

        message_validator(message)

    except Exception as e:
        logger.error(f"Ошибка обработки сообщения от пользователя {user_id} в группе {chat_id}: {e}")
