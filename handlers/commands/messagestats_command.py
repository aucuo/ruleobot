from datetime import datetime, timedelta, timezone
from telebot.types import Message
from api.controllers.group_controller import GroupController
from bot import bot
import logging

logger = logging.getLogger(__name__)

def messagestats_command(message: Message):
    chat_id, command_parts = str(message.chat.id), message.text.split(maxsplit=1)
    target_username = command_parts[1][1:] if len(command_parts) > 1 and command_parts[1].startswith("@") else None
    group_controller = GroupController(chat_id)

    if not (group := group_controller.get()).get("success"):
        return send_error(chat_id, group["error"])

    member_controller = group_controller.members(None)

    if target_username:
        user_stats(chat_id, target_username, member_controller, group_controller)
    else:
        group_stats(chat_id, member_controller, group_controller)


def group_stats(chat_id, member_controller, group_controller):
    if not (members := member_controller.get_all()).get("success"):
        return send_error(chat_id, members["error"])

    today, yesterday = datetime.now(timezone.utc).date(), datetime.now(timezone.utc).date() - timedelta(days=1)
    total_today, total_yesterday, stats_today, stats_yesterday = 0, 0, {}, {}

    for member in members["members"]:
        messages = group_controller.members(member.user_id).messages().get()
        if not messages.get("success"):
            continue

        today_count = sum(1 for msg in messages["messages"] if datetime.fromisoformat(msg.date).date() == today)
        yesterday_count = sum(1 for msg in messages["messages"] if datetime.fromisoformat(msg.date).date() == yesterday)
        username = member.username or "Неизвестно"

        stats_today[username] = today_count
        stats_yesterday[username] = yesterday_count
        total_today += today_count
        total_yesterday += yesterday_count

    avg_today, avg_yesterday = total_today / max(len(stats_today), 1), total_yesterday / max(len(stats_yesterday), 1)
    top_today = sorted(stats_today.items(), key=lambda x: x[1], reverse=True)[:5]
    top_yesterday = sorted(stats_yesterday.items(), key=lambda x: x[1], reverse=True)[:5]

    response = (
        f"📊 Статистика сообщений:\n\n"
        f"Среднее за сегодня: {avg_today:.2f}\nСреднее за вчера: {avg_yesterday:.2f}\n\n"
        f"👥 Топ 5 за сегодня:\n" +
        "\n".join([f"- @{name}: {count}" for name, count in top_today if count > 0]) +
        f"\n\n👥 Топ 5 за вчера:\n" +
        "\n".join([f"- @{name}: {count}" for name, count in top_yesterday if count > 0])
    )

    bot.send_message(chat_id, response)


def user_stats(chat_id, username, member_controller, group_controller):
    if not (member := member_controller.get_by_username(username)).get("success"):
        return send_error(chat_id, f"Пользователь @{username} не найден")

    messages = group_controller.members(member["user_id"]).messages().get()
    if not messages.get("success"):
        return send_error(chat_id, f"Ошибка получения сообщений для @{username}")

    today, yesterday = datetime.now(timezone.utc).date(), datetime.now(timezone.utc).date() - timedelta(days=1)
    today_count = sum(1 for msg in messages["messages"] if datetime.fromisoformat(msg.date).date() == today)
    yesterday_count = sum(1 for msg in messages["messages"] if datetime.fromisoformat(msg.date).date() == yesterday)

    bot.send_message(
        chat_id,
        f"📊 Статистика сообщений для @{username}:\n\nСообщений за сегодня: {today_count}\nСообщений за вчера: {yesterday_count}"
    )


def send_error(chat_id, error):
    logger.error(error)
    bot.send_message(chat_id, f"❌ Ошибка: {error}")