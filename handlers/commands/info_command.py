from datetime import datetime, timedelta, timezone
from telebot.types import Message
from api.controllers.group_controller import GroupController
from api.models import Member
from bot import bot
import logging

logger = logging.getLogger(__name__)

def info_command(message: Message):
    chat_id = str(message.chat.id)

    # Получение контроллера группы
    group_controller = GroupController(chat_id)
    group_result = group_controller.get()

    if not group_result["success"]:
        error_message = f"Ошибка: {group_result['error']}"
        logger.error(error_message)
        bot.send_message(chat_id, error_message)
        return

    group = group_result["group"]

    # Разбираем параметры команды
    command_parts = message.text.split(maxsplit=1)

    if len(command_parts) == 1:
        # Информация о группе
        print_group_info(chat_id, group, group_controller)
    else:
        # Информация о пользователе
        target_username = command_parts[1].strip('@')
        print_user_info(chat_id, target_username, group_controller)


def calculate_message_counts(members, member_controller):
    today = datetime.now(timezone.utc).date()
    yesterday = today - timedelta(days=1)
    today_count = {}
    yesterday_count = {}

    for member in members:
        messages_result = member_controller.messages().get()
        if not messages_result["success"]:
            logger.error(f"Ошибка получения сообщений для участника {member.username}: {messages_result['error']}")
            continue

        for message in messages_result["messages"]:
            message_date = datetime.fromisoformat(message.date).date()
            if message_date == today:
                today_count[member.username] = today_count.get(member.username, 0) + 1
            elif message_date == yesterday:
                yesterday_count[member.username] = yesterday_count.get(member.username, 0) + 1

    return today_count, yesterday_count


def format_top_users(counts, title):
    sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:5]
    return (
        f"📅 {title}:\n" +
        "\n".join([f"{i + 1}. @{username or 'Неизвестно'} — {count} сообщений" for i, (username, count) in enumerate(sorted_counts)])
        if sorted_counts else f"{title}: Нет участников для отображения"
    )


def print_group_info(chat_id, group, group_controller):
    member_controller = group_controller.members(None)
    members_result = member_controller.get_all()

    if not members_result["success"]:
        logger.error(f"Ошибка получения участников: {members_result['error']}")
        bot.send_message(chat_id, f"📋 Информация о группе:\nОшибка получения информации о группе.")
        return

    members = members_result["members"]
    member_count = len(members)

    top_users = sorted(members, key=lambda member: getattr(member, "message_count", 0), reverse=True)[:5]
    top_users_text = "\n".join(
        [f"{i + 1}. @{member.username or 'Неизвестно'} — {member.message_count} сообщений"
         for i, member in enumerate(top_users)]
    ) if top_users else "Нет участников для отображения"

    today_count, yesterday_count = calculate_message_counts(members, member_controller)

    info_text = (
        f"📋 Информация о группе:\n"
        f"ID: {group.group_id}\n"
        f"Название: {group.title}\n"
        f"Описание: {group.description or 'Нет описания'}\n"
        f"Создатель: @{group.owner_username or 'Неизвестно'}\n"
        f"Участников: {member_count}\n\n"
        f"🔥 Топ-5 активных участников (всего времени):\n{top_users_text}\n\n"
        f"{format_top_users(today_count, 'Топ-5 активных участников за сегодня')}\n\n"
        f"{format_top_users(yesterday_count, 'Топ-5 активных участников за вчера')}"
    )
    bot.send_message(chat_id, info_text)


def print_user_info(chat_id, target_username, group_controller):
    member_controller = group_controller.members(None)
    member_result = member_controller.get_by_username(target_username)

    if not member_result["success"]:
        error_message = f"❌ {member_result['error']}"
        logger.error(error_message)
        bot.send_message(chat_id, error_message)
        return

    user_id = member_result["user_id"]
    user_data = member_result["user_data"]
    member = Member.from_dict({"user_id": user_id, **user_data})

    today = datetime.now(timezone.utc).date()
    yesterday = today - timedelta(days=1)
    today_count = 0
    yesterday_count = 0

    messages_result = group_controller.members(member.user_id).messages().get()
    if messages_result["success"]:
        for message in messages_result["messages"]:
            message_date = datetime.fromisoformat(message.date).date()
            if message_date == today:
                today_count += 1
            elif message_date == yesterday:
                yesterday_count += 1

    warns_result = group_controller.members(member.user_id).warns().get()
    warns_text = "\n".join(
        [f"- Причина: {warn.reason}, Дата: {warn.date}" for warn in warns_result.get("warns", [])]
    ) if warns_result["success"] else None

    mutes_result = group_controller.members(member.user_id).mutes().get()
    mutes_text = "\n".join(
        [f"- Причина: {mute.reason}, До: {mute.mute_until}" for mute in mutes_result.get("mutes", [])]
    ) if mutes_result["success"] else None

    info_text = (
        f"👤 Информация об участнике @{target_username}:\n"
        f"ID: {member.user_id}\n"
        f"Имя: {member.first_name or 'Неизвестно'} {member.last_name or ''}\n"
        f"Сообщений всего: {member.message_count}\n"
        f"Сообщений за сегодня: {today_count}\n"
        f"Сообщений за вчера: {yesterday_count}"
    )
    if warns_text:
        info_text += f"\n\n⚠️ Варны:\n{warns_text}"
    if mutes_text:
        info_text += f"\n\n🔇 Муты:\n{mutes_text}"

    bot.send_message(chat_id, info_text)
