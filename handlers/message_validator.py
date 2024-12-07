import re
import uuid
from datetime import datetime, timedelta, timezone
from bot import bot
from api.controllers.group_controller import GroupController
from api.models import Warn, Mute
import logging

logger = logging.getLogger(__name__)

# Загружаем триггеры для спама
try:
    with open('spam_list.txt', 'r', encoding='utf-8') as file:
        SPAM_TRIGGERS = file.read().splitlines()
except FileNotFoundError:
    SPAM_TRIGGERS = []

# Загружаем список слов для проверки на маты
try:
    with open('profanity_list.txt', 'r', encoding='utf-8') as file:
        PROFANITY_LIST = file.read().splitlines()
except FileNotFoundError:
    PROFANITY_LIST = []

# Словарь для отслеживания сообщений (по группам и пользователям)
GROUP_MESSAGE_TRACKER = {}


def normalize_text(text):
    """Приводит текст к нормализованной форме для точной проверки."""
    return re.sub(r'[^\w\s]', '', text.lower())


def contains_profanity(text):
    normalized_text = normalize_text(text)
    return any(word in normalized_text.split() for word in PROFANITY_LIST)


def contains_caps(text):
    return text.isupper() and any(c.isalpha() for c in text) and len(text) > 4


def contains_spam(text):
    normalized_text = normalize_text(text)
    return any(trigger in normalized_text.split() for trigger in SPAM_TRIGGERS)


def contains_links(text):
    return bool(re.search(r"(https?://[^\s]+)|(www\.[^\s]+)", text))


def is_message_limit_exceeded(group_id, user_id, max_messages=6, interval_seconds=60):
    now = datetime.now()

    # Инициализация структуры для группы и пользователя
    if group_id not in GROUP_MESSAGE_TRACKER:
        GROUP_MESSAGE_TRACKER[group_id] = {}
    if user_id not in GROUP_MESSAGE_TRACKER[group_id]:
        GROUP_MESSAGE_TRACKER[group_id][user_id] = []

    # Добавляем текущее время в список
    GROUP_MESSAGE_TRACKER[group_id][user_id].append(now)

    # Удаляем сообщения, которые были за пределами интервала
    GROUP_MESSAGE_TRACKER[group_id][user_id] = [
        timestamp for timestamp in GROUP_MESSAGE_TRACKER[group_id][user_id]
        if now - timestamp <= timedelta(seconds=interval_seconds)
    ]

    return len(GROUP_MESSAGE_TRACKER[group_id][user_id]) > max_messages


def validate_message(text, settings, group_id, user_id):
    violations = []

    if settings.spam_filter and contains_spam(text):
        violations.append("Спам")

    if settings.caps_filter and contains_caps(text):
        violations.append("Капс")

    if settings.links_filter and contains_links(text):
        violations.append("Ссылки")

    if settings.profanity_filter and contains_profanity(text):
        violations.append("Маты")

    if is_message_limit_exceeded(group_id, user_id):
        violations.append("Превышено количество сообщений в минуту")

    return violations


def message_validator(message):
    chat_id = str(message.chat.id)
    user_id = str(message.from_user.id)
    text = message.text or ""

    # Получаем настройки группы
    group_controller = GroupController(chat_id)
    group_result = group_controller.get()

    if not group_result["success"]:
        logger.error(f"Ошибка получения настроек группы {chat_id}: {group_result['error']}")
        return

    group = group_result["group"]
    settings = group.settings

    # Валидируем сообщение
    violations = validate_message(text, settings, chat_id, user_id)

    if violations:
        # Логируем нарушения
        logger.warning(f"Нарушения от пользователя {user_id} в группе {chat_id}: {', '.join(violations)}")

        # Работаем с контроллерами участника и варнов
        member_controller = group_controller.members(user_id)
        warn_controller = member_controller.warns()
        mute_controller = member_controller.mutes()

        # Получаем все текущие предупреждения
        warns_result = warn_controller.get()
        current_warns = warns_result["warns"] if warns_result["success"] else []
        warn_count = len(current_warns)

        # Выдаём предупреждение за каждое нарушение
        for violation in violations:
            warn_id = str(uuid.uuid4())
            warn = Warn(
                warn_id=warn_id,
                reason=violation,
                date=datetime.now().isoformat(),
                issued_by="bot"
            )
            warn_result = warn_controller.post(warn)
            if warn_result["success"]:
                warn_count += 1
                bot.reply_to(
                    message,
                    f"❌ Нарушение: {violation}. Вам выдано предупреждение. Всего предупреждений: {warn_count} из 5."
                )
                logger.info(f"Выдано предупреждение за '{violation}' для пользователя {user_id} в группе {chat_id}.")
            else:
                logger.error(f"Ошибка выдачи предупреждения для пользователя {user_id} в группе {chat_id}: {warn_result['error']}")

        # Проверяем, нужно ли выдать мут
        if warn_count >= 5:
            mute_id = str(uuid.uuid4())
            mute_until = datetime.now(timezone.utc) + timedelta(days=1)
            mute = Mute(
                mute_id=mute_id,
                reason="Достигнуто 5 предупреждений",
                mute_until=mute_until.isoformat(),
                issued_by="ruleobot"
            )
            mute_result = mute_controller.post(mute)
            if mute_result["success"]:
                # Удаляем все предупреждения
                warn_controller.clear()
                bot.reply_to(
                    message,
                    f"❌ Достигнуто 5 предупреждений. Вы замьючены на 24 часа."
                )
                logger.info(f"Выдан мут на 24 часа для пользователя {user_id} в группе {chat_id}.")
            else:
                logger.error(f"Ошибка выдачи мута для пользователя {user_id} в группе {chat_id}: {mute_result['error']}")

        # Удаляем сообщение при нарушениях
        bot.delete_message(chat_id, message.message_id)
        logger.info(f"Удалено сообщение пользователя {user_id} в группе {chat_id} из-за нарушений: {', '.join(violations)}")
