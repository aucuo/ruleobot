# handlers/settings_handler.py

import logging
from telebot.types import Message
from bot import bot
from managers.settings_manager import SettingsManager
from managers.group_manager import GroupManager

logger = logging.getLogger(__name__)

def settings_handler(message: Message):
    if message.chat.type in ['group', 'supergroup']:
        chat_id = message.chat.id
        settings = SettingsManager.get_settings(chat_id)

        settings_info = (
            f"⚙️ **Настройки бота**\n"
            f"spam: {'✅ Включена' if settings.get('spam') else '❌ Отключена'}\n"
            f"profanity: {'✅ Включена' if settings.get('profanity') else '❌ Отключена'}\n"
            f"caps: {'✅ Включена' if settings.get('caps') else '❌ Отключена'}"
        )

        bot.reply_to(message, settings_info, parse_mode="Markdown")
    else:
        bot.reply_to(message, "Эта команда работает только в группах или супергруппах.")

def set_handler(message: Message):
    if message.chat.type in ['group', 'supergroup']:
        chat_id = message.chat.id
        user_id = message.from_user.id

        # Проверка прав: только создатель группы может редактировать настройки
        group_data = GroupManager.get_group_data(chat_id)
        if not group_data or group_data.get('ownerId') != user_id:
            bot.reply_to(message, "❌ Только создатель группы может изменять настройки бота.")
            return

        # Проверка аргументов команды
        args = message.text.split(' ', 2)
        if len(args) < 3:
            bot.reply_to(message, "⚠️ Команда используется следующим образом: /set <настройка> <значение>\n"
                                  "Пример: /set spam off")
            return

        setting_name = args[1].lower()
        setting_value = args[2].lower()

        # Обработка изменения настроек
        current_settings = SettingsManager.get_settings(chat_id)

        if setting_name in current_settings:
            if setting_value in ['on', 'off']:
                new_value = True if setting_value == 'on' else False
                current_settings[setting_name] = new_value
                SettingsManager.save_settings(chat_id, current_settings)
                bot.reply_to(message, f"Настройка '{setting_name}' успешно изменена на {'✅ включена' if new_value else '❌ отключена'}.")
            else:
                bot.reply_to(message, "⚠️ Значение настройки должно быть 'on' или 'off'.")
        else:
            bot.reply_to(message, f"⚠️ Настройка '{setting_name}' не найдена. Доступные настройки: spam, profanity, caps.")
    else:
        bot.reply_to(message, "Эта команда работает только в группах или супергруппах.")
