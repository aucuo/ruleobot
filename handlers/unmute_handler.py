# handlers/unmute_handler.py

import logging
from telebot.types import Message
from bot import bot
from managers.member_manager import UserManager
from utils import is_admin

logger = logging.getLogger(__name__)

def unmute_handler(message: Message):
    if message.chat.type in ['group', 'supergroup']:
        chat_id = message.chat.id
        user_id = message.from_user.id

        # Проверка прав администратора или создателя группы
        if not is_admin(chat_id, user_id):
            bot.reply_to(message, "❌ У вас нет прав на использование этой команды.")
            return

        # Проверка аргументов команды
        args = message.text.split(' ')
        if len(args) < 2:
            bot.reply_to(message, "⚠️ Команда используется следующим образом: /unmute @username")
            return

        username = args[1].replace("@", "")
        user = UserManager.get_user_by_username(chat_id, username)
        if user:
            # Снять мьют с пользователя
            UserManager.unmute_user(chat_id, user.user_id)
            bot.reply_to(message, f"✅ Пользователь @{username} был успешно разблокирован.")
            logger.info(f"Пользователь @{username} (user_id={user.user_id}) был разблокирован в группе chat_id={chat_id}.")
        else:
            bot.reply_to(message, f"⚠️ Пользователь @{username} не найден.")
