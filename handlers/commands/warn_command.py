import uuid
from datetime import datetime, timedelta
from telebot.types import Message
from api.controllers.group_controller import GroupController
from api.models import Warn, Mute
from bot import bot
from utils import admin_required
import logging

logger = logging.getLogger(__name__)

@admin_required
def warn_command(message: Message):
    chat_id = str(message.chat.id)

    # Разбираем параметры команды
    command_parts = message.text.split(maxsplit=2)
    if len(command_parts) < 3:
        bot.send_message(chat_id, "❌ Формат команды: /warn @username <причина>")
        return

    target_username = command_parts[1].strip('@')
    warn_reason = command_parts[2]

    try:
        # Получаем контроллер группы
        group_controller = GroupController(chat_id)
        member_controller = group_controller.members(None)

        # Ищем участника по username
        member_result = member_controller.get_by_username(target_username)
        if not member_result["success"]:
            bot.send_message(chat_id, f"❌ {member_result['error']}")
            return

        target_user_id = member_result["user_id"]

        # Выдаем предупреждение
        warn_controller = group_controller.members(target_user_id).warns()
        warn_id = str(uuid.uuid4())
        warn = Warn(
            warn_id=warn_id,
            reason=warn_reason,
            date=datetime.now().isoformat(),
            issued_by=str(message.from_user.id)
        )
        warn_result = warn_controller.post(warn)

        if warn_result["success"]:
            # Получение общего количества предупреждений
            all_warns = warn_controller.get()
            if all_warns["success"]:
                warns_count = len(all_warns.get("warns", []))
                bot.send_message(
                    chat_id,
                    f"✅ Пользователь @{target_username} получил предупреждение.\n"
                    f"Причина: {warn_reason}\n"
                    f"Текущее количество предупреждений: {warns_count}"
                )
                logger.info(
                    f"Предупреждение выдано пользователю {target_user_id} в группе {chat_id}. "
                    f"Причина: {warn_reason}. Текущее количество предупреждений: {warns_count}"
                )

                # Если предупреждений >= 5, выдать мут
                if warns_count >= 5:
                    mute_controller = group_controller.members(target_user_id).mutes()
                    mute_id = str(uuid.uuid4())
                    mute = Mute(
                        mute_id=mute_id,
                        reason="Превышено количество предупреждений",
                        mute_until=(datetime.now() + timedelta(days=1)).isoformat(),
                        issued_by=str(message.from_user.username)
                    )
                    mute_result = mute_controller.post(mute)
                    if mute_result["success"]:
                        warn_controller.clear()  # Сбрасываем предупреждения
                        bot.send_message(
                            chat_id,
                            f"🔇 Пользователь @{target_username} был замьючен на 1 сутки за 5 предупреждений."
                        )
                        logger.info(
                            f"Пользователь {target_user_id} получил мут на 1 сутки за 5 предупреждений в группе {chat_id}."
                        )
                    else:
                        logger.error(
                            f"Ошибка выдачи мута для пользователя {target_user_id} в группе {chat_id}: {mute_result['error']}"
                        )
            else:
                logger.error(f"Ошибка получения предупреждений для пользователя {target_user_id}: {all_warns['error']}")
        else:
            bot.send_message(chat_id, f"❌ Ошибка выдачи предупреждения: {warn_result['error']}")
            logger.error(f"Ошибка выдачи предупреждения для {target_user_id}: {warn_result['error']}")

    except Exception as e:
        logger.error(f"Ошибка выполнения команды /warn: {e}")
        bot.send_message(chat_id, "❌ Произошла ошибка при выполнении команды.")