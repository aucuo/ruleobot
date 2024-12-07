import re
from bot import bot
import logging

from functools import wraps
from telebot.types import Message

logger = logging.getLogger(__name__)

def admin_required(func):
    @wraps(func)
    def wrapper(message: Message):
        chat_id = message.chat.id
        user_id = message.from_user.id
        if not is_admin(chat_id, user_id):
            bot.send_message(chat_id, "❌ У вас нет прав для выполнения этой команды.")
            return
        return func(message)
    return wrapper

def is_admin(chat_id, user_id):
    """
    Проверяет, является ли пользователь администратором группы.
    """
    try:
        admins = bot.get_chat_administrators(chat_id)
        return any(admin.user.id == user_id for admin in admins)
    except Exception as e:
        logger.error(f"Ошибка при проверке прав администратора: {e}")
        return False

def escape_markdown(text):
    """
    Экранирует специальные символы для Markdown.
    """
    return re.sub(r'([_\[\]()~`>#+\-=|{}.!])', r'\\\1', text)

def is_caps(message_text):
    """
    Проверка на капс (все буквы в сообщении заглавные и длина сообщения больше 4 символов).
    """
    return message_text.isupper() and any(c.isalpha() for c in message_text) and len(message_text) > 4


def split_message(text, max_length):
    """
    Разделяет длинное сообщение на несколько частей, если оно превышает max_length.
    """
    lines = text.split('\n')
    chunks = []
    current_chunk = ""
    for line in lines:
        if len(current_chunk) + len(line) + 1 > max_length:
            chunks.append(current_chunk)
            current_chunk = ""
        current_chunk += line + "\n"
    if current_chunk:
        chunks.append(current_chunk)
    return chunks


def rus_endings(number, singular, few, many):
    if 11 <= number % 100 <= 19:
        return many
    last_digit = number % 10
    if last_digit == 1:
        return singular
    if 2 <= last_digit <= 4:
        return few
    return many