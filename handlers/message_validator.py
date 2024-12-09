import os
import re
import uuid
from datetime import datetime, timedelta, timezone
from bot import bot
from api.controllers.group_controller import GroupController
from api.models import Warn, Mute
import logging
import google.generativeai as genai

from utils import escape_markdown

# Настройка логгера
logger = logging.getLogger(__name__)

# Настройка нейронки
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Загружаем списки для стандартных фильтров
try:
    with open('spam_list.txt', 'r', encoding='utf-8') as file:
        SPAM_TRIGGERS = file.read().splitlines()
except FileNotFoundError:
    SPAM_TRIGGERS = []

try:
    with open('profanity_list.txt', 'r', encoding='utf-8') as file:
        PROFANITY_LIST = file.read().splitlines()
except FileNotFoundError:
    PROFANITY_LIST = []

GROUP_MESSAGE_TRACKER = {}

# Настройка нейронки
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Хранение контекста общения
CHAT_CONTEXTS = {}

PROMPT_FILE_PATH = "small_talk_prompt.txt"
try:
    with open(PROMPT_FILE_PATH, "r", encoding="utf-8") as file:
        base_system_prompt = file.read()
except FileNotFoundError:
    base_system_prompt = "Вы - Ruleobot, помощник по технологиям. Пожалуйста, задайте мне вопрос."

# Функция для обработки small_talk с контекстом
def handle_small_talk_with_context(chat_id, user_name, message_text):
    try:
        model = genai.GenerativeModel(model_name="gemini-1.5-flash")

        # Инициализация контекста чата
        if chat_id not in CHAT_CONTEXTS:
            CHAT_CONTEXTS[chat_id] = []

        # Добавляем текущее сообщение пользователя в контекст
        CHAT_CONTEXTS[chat_id].append(f"{user_name}: {message_text}")

        # Ограничиваем длину контекста
        if len(CHAT_CONTEXTS[chat_id]) > 10:  # Храним только последние 10 сообщений
            CHAT_CONTEXTS[chat_id] = CHAT_CONTEXTS[chat_id][-10:]

        # Формируем системное сообщение и объединяем контекст
        system_prompt = (
            f"{base_system_prompt}. Вы - Ruleobot, дружелюбный виртуальный помощник."
            "Отвечайте на сообщения весело, дружелюбно и поддерживайте непринуждённый тон общения. "
            "Учитывайте предыдущие сообщения в этом чате для построения осмысленных ответов.\n\n"
            f"Сейчас с вами общается пользователь {user_name}"
        )
        combined_context = system_prompt + "\n".join(CHAT_CONTEXTS[chat_id])

        # Получаем ответ от нейронки
        response = model.generate_content(
            contents={"text": combined_context},
            generation_config={"max_output_tokens": 150}
        )

        # Добавляем ответ нейронки в контекст
        CHAT_CONTEXTS[chat_id].append(f"Ruleobot: {response.text.strip()}")

        return response.text.strip()
    except Exception as e:
        logger.error(f"Ошибка обработки small_talk нейронкой: {e}")
        return "Извините, сейчас я не могу ответить."

# Вспомогательные функции для стандартных фильтров
def normalize_text(text):
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
    if group_id not in GROUP_MESSAGE_TRACKER:
        GROUP_MESSAGE_TRACKER[group_id] = {}
    if user_id not in GROUP_MESSAGE_TRACKER[group_id]:
        GROUP_MESSAGE_TRACKER[group_id][user_id] = []
    GROUP_MESSAGE_TRACKER[group_id][user_id].append(now)
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

# Функция анализа сообщения нейронной сетью
def analyze_message_with_ai(user_name, message_text):
    try:
        model = genai.GenerativeModel(model_name="gemini-1.5-flash")
        system_prompt = (
            "Вы - Ruleobot, нейронная сеть для анализа сообщений. "
            "Ваша задача - определять, является ли сообщение плохим (спам, оскорбления, маты, капс). "
            "Если сообщение плохое, объясните причину (в конце добавьте проверил ИИ) в одной строке. Если сообщение хорошее, напишите 'Сообщение допустимо'."
        )
        response = model.generate_content(
            contents={"text": f"{system_prompt}\n\nПользователь: {user_name}\nСообщение: {message_text}"},
            generation_config={"max_output_tokens": 50}
        )
        return response.text.strip()
    except Exception as e:
        logger.error(f"Ошибка анализа сообщения нейронкой: {e}")
        return "Ошибка анализа нейронкой"

# Основная функция валидации сообщений
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

    # Используем стандартные фильтры
    violations = validate_message(text, settings, chat_id, user_id)

    # Если стандартные фильтры ничего не нашли, используем AI
    if not violations and settings.ai_filter:
        user_name = message.from_user.username or f"{message.from_user.first_name} {message.from_user.last_name or ''}"
        ai_result = analyze_message_with_ai(user_name, text)
        if "Сообщение допустимо" not in ai_result:
            violations.append(ai_result)
        # Обработка small_talk с контекстом
        elif settings.small_talk:
                response = handle_small_talk_with_context(chat_id, user_name, text)
                bot.reply_to(message, f"🤖 {escape_markdown(response)}", parse_mode="MarkdownV2")
                return

    # Если есть нарушения, обрабатываем их
    if violations:
        logger.warning(f"Нарушения от пользователя {user_id} в группе {chat_id}: {', '.join(violations)}")
        member_controller = group_controller.members(user_id)
        warn_controller = member_controller.warns()
        mute_controller = member_controller.mutes()
        warns_result = warn_controller.get()
        current_warns = warns_result["warns"] if warns_result["success"] else []
        warn_count = len(current_warns)

        # Выдаём предупреждения
        for violation in violations:
            warn_id = str(uuid.uuid4())
            warn = Warn(
                warn_id=warn_id,
                reason=violation,
                date=datetime.now().isoformat(),
                issued_by="ruleobot"
            )
            warn_result = warn_controller.post(warn)
            if warn_result["success"]:
                warn_count += 1
                bot.reply_to(
                    message,
                    f"❌ Нарушение: {violation}. Вам выдано предупреждение. Всего предупреждений: {warn_count} из 5."
                )
            else:
                logger.error(f"Ошибка выдачи предупреждения для пользователя {user_id}: {warn_result['error']}")

        # Если 5 предупреждений, выдаём мут
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
                warn_controller.clear()
                bot.reply_to(
                    message,
                    "❌ Достигнуто 5 предупреждений. Вы замьючены на 24 часа."
                )
        bot.delete_message(chat_id, message.message_id)
