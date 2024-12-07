# handlers/new_member_handler.py

import logging
from telebot.types import Message
from managers import UserManager
from bot import bot

logger = logging.getLogger(__name__)

def new_member_handler(message: Message):
    if message.chat.type in ['group', 'supergroup']:
        chat_id = message.chat.id
        for member in message.new_chat_members:
            user_id = member.id
            username = member.username
            first_name = member.first_name
            last_name = member.last_name
            UserManager.add_member(chat_id, user_id, username, first_name, last_name)
            welcome_message = f"👋 Добро пожаловать, @{username}!" if username else f"👋 Добро пожаловать, {first_name}!"
            bot.send_message(chat_id, welcome_message)
