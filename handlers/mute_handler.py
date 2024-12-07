# handlers/mute_handler.py

import logging
import datetime
from telebot.types import Message
from bot import bot
from managers.member_manager import UserManager
from utils import is_admin

logger = logging.getLogger(__name__)

def mute_handler(message: Message):
    if message.chat.type in ['group', 'supergroup']:
        chat_id = message.chat.id
        user_id = message.from_user.id

        # Проверка прав администратора или создателя группы
        if not is_admin(chat_id, user_id):
            bot.reply_to(message, "❌ У вас нет прав на использование этой команды.")
            return

        # Проверка аргументов команды
        args = message.text.split(' ', 3)
        if len(args) < 4:
            bot.reply_to(message, "⚠️ Команда используется следующим образом: /mute @username <количество минут> <причина>")
            return

        username = args[1].replace("@", "")
        try:
            mute_duration = int(args[2])
        except ValueError:
            bot.reply_to(message, "⚠️ Количество минут должно быть числом.")
            return

        reason = args[3]

        user = UserManager.get_user_by_username(chat_id, username)
        if user:
            mute_until = datetime.datetime.now() + datetime.timedelta(minutes=mute_duration)
            mute_entry = {
                "reason": reason,
                "mute_until": mute_until.isoformat()
            }
            UserManager.mute_user(chat_id, user.user_id, mute_entry)

            bot.reply_to(message, f"✅ Пользователь @{username} был отключен на {mute_duration} минут по причине: {reason}.")
            logger.info(f"Пользователь @{username} (user_id={user.user_id}) был отключен на {mute_duration} минут в группе chat_id={chat_id}.")
        else:
            bot.reply_to(message, f"⚠️ Пользователь @{username} не найден.")
