# handlers/warn_handler.py

import logging
from telebot.types import Message
from managers import UserManager
from bot import bot
import datetime

from utils import is_admin

logger = logging.getLogger(__name__)

def warn_handler(message: Message):
    if message.chat.type in ['group', 'supergroup']:
        # Проверка прав администратора
        if not is_admin(message.chat.id, message.from_user.id):
            bot.reply_to(message, "❌ У вас нет прав на использование этой команды.")
            return

        # Проверка аргументов команды
        args = message.text.split(' ', 2)
        if len(args) < 3:
            bot.reply_to(message, "⚠️ Команда используется следующим образом: /warn @username 'reason'")
            return

        username = args[1].replace("@", "")
        reason = args[2]

        user = UserManager.get_user_by_username(message.chat.id, username)
        if user:
            date = datetime.datetime.now().isoformat()
            UserManager.add_warning(message.chat.id, user.user_id, reason, date)
            updated_user = UserManager.load_user(message.chat.id, user.user_id)
            current_warnings = len(updated_user.warnings)
            bot.reply_to(message, f"✅ Предупреждение для @{username} добавлено: {reason}\n⚠️ Текущее количество предупреждений: {current_warnings}")
        else:
            bot.reply_to(message, f"⚠️ Пользователь @{username} не найден.")

def unwarn_handler(message: Message):
    if message.chat.type in ['group', 'supergroup']:
        # Проверка прав администратора
        if not is_admin(message.chat.id, message.from_user.id):
            bot.reply_to(message, "❌ У вас нет прав на использование этой команды.")
            return

        # Проверка аргументов команды
        args = message.text.split(' ')
        if len(args) < 2:
            bot.reply_to(message, "⚠️ Команда используется следующим образом: /unwarn @username [-all]")
            return

        username = args[1].replace("@", "")
        remove_all = '-all' in args

        user = UserManager.get_user_by_username(message.chat.id, username)
        if user:
            if remove_all:
                # Удаление всех предупреждений
                UserManager.clear_warnings(message.chat.id, user.user_id)
                bot.reply_to(message, f"✅ Все предупреждения для @{username} были сняты.\n⚠️ Текущее количество предупреждений: 0")
            else:
                # Удаление последнего предупреждения
                if user.warnings:
                    UserManager.remove_last_warning(message.chat.id, user.user_id)
                    updated_user = UserManager.load_user(message.chat.id, user.user_id)
                    current_warnings = len(updated_user.warnings)
                    bot.reply_to(message, f"✅ Последнее предупреждение для @{username} было снято.\n⚠️ Текущее количество предупреждений: {current_warnings}")
                else:
                    bot.reply_to(message, f"⚠️ У пользователя @{username} нет предупреждений.")
        else:
            bot.reply_to(message, f"⚠️ Пользователь @{username} не найден.")

def warnlist_handler(message: Message):
    if message.chat.type in ['group', 'supergroup']:
        # Проверка аргументов команды
        args = message.text.split(' ')
        if len(args) < 2:
            bot.reply_to(message, "⚠️ Команда используется следующим образом: /warnlist @username")
            return

        username = args[1].replace("@", "")
        user = UserManager.get_user_by_username(message.chat.id, username)
        if user:
            if user.warnings:
                warn_list = "\n".join([f"Дата: {warn['date']}, Описание: {warn['reason']}" for warn in user.warnings])
                bot.reply_to(message, f"📜 Список предупреждений для @{username}:\n{warn_list}")
            else:
                bot.reply_to(message, f"⚠️ У пользователя @{username} нет предупреждений.")
        else:
            bot.reply_to(message, f"⚠️ Пользователь @{username} не найден.")
