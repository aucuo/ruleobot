from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from api.controllers.group_controller import GroupController
from bot import bot
import logging

logger = logging.getLogger(__name__)

# Хранилище состояний ответов
reply_states = {}

def ask_command(message: Message):
    chat_id = str(message.chat.id)
    command_parts = message.text.split(maxsplit=1)

    if len(command_parts) < 2:
        bot.send_message(chat_id, "❌ Используйте команду в формате: /ask <ваш вопрос>")
        return

    user_message = command_parts[1]
    group_controller = GroupController(chat_id)

    # Получаем информацию о группе
    if not (group := group_controller.get()).get("success"):
        bot.send_message(chat_id, f"❌ Ошибка: {group['error']}")
        return

    group_data = group["group"]
    owner_id = group_data.owner_id

    # Проверяем наличие создателя группы
    if owner_id == "Неизвестен":
        bot.send_message(chat_id, "❌ Ошибка: Создатель группы неизвестен.")
        return

    # Формируем сообщение создателю
    user = message.from_user
    user_info = f"@{user.username}" if user.username else f"{user.first_name} {user.last_name or ''}"
    ask_message = (
        f"📩 Новый вопрос от пользователя {user_info}:\n\n"
        f"{user_message}\n\n"
        f"📢 Отправлено из группы: {group_data.title}"
    )

    # Создаем кнопку для ответа
    reply_markup = InlineKeyboardMarkup()
    reply_markup.add(
        InlineKeyboardButton(
            text="Ответить пользователю",
            callback_data=f"reply_user:{chat_id}:{user.id}"  # Используем callback_data для идентификации пользователя
        )
    )

    try:
        # Отправляем сообщение создателю группы с кнопкой
        bot.send_message(owner_id, ask_message, reply_markup=reply_markup)
        bot.send_message(chat_id, "✅ Ваш вопрос отправлен создателю группы.")
    except Exception as e:
        logger.error(f"Ошибка отправки сообщения создателю группы {owner_id}: {e}")
        bot.send_message(chat_id, "❌ Ошибка отправки вопроса создателю группы.")

# Обработка нажатия на кнопку
@bot.callback_query_handler(func=lambda call: call.data.startswith("reply_user:"))
def handle_reply_callback(call):
    try:
        _, chat_id, user_id = call.data.split(":")
        chat_id, user_id = int(chat_id), int(user_id)

        # Сохраняем состояние для пересылки ответа
        reply_states[call.message.chat.id] = {
            "chat_id": chat_id,
            "user_id": user_id,
            "question_text": call.message.text  # Сохраняем текст вопроса
        }

        bot.send_message(
            call.message.chat.id,
            f"✏️ Напишите ваш ответ пользователю. Ваше сообщение будет переслано в группу.",
            reply_markup=None  # Убираем кнопку после нажатия
        )
    except Exception as e:
        logger.error(f"Ошибка обработки callback: {e}")
        bot.send_message(call.message.chat.id, "❌ Произошла ошибка при обработке ответа.")

# Обработка ответа
@bot.message_handler(func=lambda m: m.chat.id in reply_states)
def collect_reply(reply_message):
    try:
        state = reply_states.pop(reply_message.chat.id)
        chat_id = state["chat_id"]
        question_text = state["question_text"]

        # Формируем сообщение с упоминанием пользователя и текстом вопроса
        response_message = (
            f"{question_text}\n\n"
            f"💬 Ответ: {reply_message.text}"
        )

        # Пересылаем ответ в исходную группу
        bot.send_message(
            chat_id,
            response_message,
            parse_mode="Markdown"
        )

        # Уведомляем администратора об успешной отправке
        bot.send_message(reply_message.chat.id, "✅ Ваш ответ отправлен.")
    except Exception as e:
        logger.error(f"Ошибка при пересылке ответа: {e}")
        bot.send_message(reply_message.chat.id, "❌ Произошла ошибка при пересылке ответа.")
