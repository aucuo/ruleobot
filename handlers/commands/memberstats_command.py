from datetime import datetime, timedelta, timezone
from telebot.types import Message
from api.controllers.group_controller import GroupController
from bot import bot
import logging

logger = logging.getLogger(__name__)

def memberstats_command(message: Message):
    chat_id = str(message.chat.id)
    group_controller = GroupController(chat_id)

    if not (group := group_controller.get()).get("success"):
        return send_error(chat_id, group["error"])

    member_controller = group_controller.members(None)

    if not (members := member_controller.get_all()).get("success"):
        return send_error(chat_id, members["error"])

    today = datetime.now(timezone.utc).date()
    yesterday = today - timedelta(days=1)

    today_count = 0
    yesterday_count = 0

    for member in members["members"]:
        entry_date = datetime.fromisoformat(member.entry_date).date()
        if entry_date == today:
            today_count += 1
        elif entry_date == yesterday:
            yesterday_count += 1

    response = (
        f"📊 Статистика новых участников:\n\n"
        f"Новых участников сегодня: {today_count}\n"
        f"Новых участников вчера: {yesterday_count}"
    )

    bot.send_message(chat_id, response)

def send_error(chat_id, error):
    logger.error(error)
    bot.send_message(chat_id, f"❌ Ошибка: {error}")
