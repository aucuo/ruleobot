import google.generativeai as genai
import os
from telebot.types import Message, logger
from bot import bot

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

PROMPT_FILE_PATH = "gemini_prompt.txt"
try:
    with open(PROMPT_FILE_PATH, "r", encoding="utf-8") as file:
        base_system_prompt = file.read()
except FileNotFoundError:
    base_system_prompt = "Вы - Ruleobot, помощник по технологиям. Пожалуйста, задайте мне вопрос."


def gem_command(message: Message):
    chat_id = str(message.chat.id)
    command_parts = message.text.split(maxsplit=1)

    if len(command_parts) < 2:
        bot.send_message(chat_id, "❌ Используйте команду в формате: /gem <ваш вопрос>")
        return

    user_message = command_parts[1]

    user = message.from_user
    user_name = user.username or f"{user.first_name} {user.last_name or ''}"

    system_prompt = f"{base_system_prompt}\n\nС тобой общается человек с именем: {user_name}. Поприветствуй в начале его по имени"

    try:
        model = genai.GenerativeModel(model_name="gemini-1.5-flash")

        response = model.generate_content(
            contents={"text": f"{system_prompt}\n\nВопрос пользователя: {user_message}"},
            generation_config={"max_output_tokens": 150}
        )

        logger.info(response.text)

        bot.send_message(chat_id, f"🤖 Ruleobot AI:\n{response.text}")
    except Exception as e:
        logger.error(f"Неизвестная ошибка: {e}")
        bot.send_message(chat_id, "❌ Произошла ошибка. Пожалуйста, попробуйте позже.")
