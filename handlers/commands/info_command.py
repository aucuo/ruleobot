from datetime import datetime, timezone, timedelta
from telebot.types import Message
from api.controllers.group_controller import GroupController
from api.models import Member
from bot import bot
import logging

logger = logging.getLogger(__name__)

def info_command(message: Message):
    chat_id, group_controller = str(message.chat.id), GroupController(str(message.chat.id))
    group_result = group_controller.get()

    if not group_result["success"]:
        send_error(chat_id, group_result["error"])
        return

    command_parts = message.text.split(maxsplit=1)
    if len(command_parts) == 1:
        print_group_info(chat_id, group_result["group"], group_controller)
    else:
        print_user_info(chat_id, command_parts[1].strip('@'), group_controller)


def send_error(chat_id, error):
    logger.error(error)
    bot.send_message(chat_id, f"Ошибка: {error}")


def print_group_info(chat_id, group, group_controller):
    members_result = group_controller.members(None).get_all()
    if not members_result["success"]:
        send_error(chat_id, members_result["error"])
        return

    members = members_result["members"]
    group_info = (
        f"📋 Информация о группе:\n"
        f"ID: {group.group_id}\n"
        f"Название: {group.title}\n"
        f"Описание: {group.description or 'Нет описания'}\n"
        f"Создатель: @{group.owner_username or 'Неизвестно'}\n"
        f"Участников: {len(members)}"
    )
    bot.send_message(chat_id, group_info)


def print_user_info(chat_id, username, group_controller):
    member_result = group_controller.members(None).get_by_username(username)
    if not member_result["success"]:
        send_error(chat_id, member_result["error"])
        return

    member = Member.from_dict({"user_id": member_result["user_id"], **member_result["user_data"]})
    warns = fetch_data(group_controller, member.user_id, "warns", "⚠️ Варны", format_warns)
    mutes = fetch_data(group_controller, member.user_id, "mutes", "🔇 Муты", format_mutes)

    user_info = (
        f"👤 Информация об участнике @{username}:\n"
        f"ID: {member.user_id}\n"
        f"Имя: {member.first_name or 'Неизвестно'} {member.last_name or ''}"
    )
    bot.send_message(chat_id, "\n\n".join(filter(None, [user_info, warns, mutes])))


def fetch_data(group_controller, user_id, data_type, title, formatter):
    result = getattr(group_controller.members(user_id), data_type)().get()
    return f"{title}:\n{formatter(result[data_type])}" if result["success"] and result.get(data_type) else None


def format_warns(warns):
    return "\n".join(f"- Причина: {warn.reason}, Дата: {warn.date}" for warn in warns)


def format_mutes(mutes):
    return "\n".join(f"- Причина: {mute.reason}, До: {mute.mute_until}" for mute in mutes)