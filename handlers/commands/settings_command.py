import logging
from telebot.types import Message
from api.controllers.group_controller import GroupController
from bot import bot
from utils import admin_required

logger = logging.getLogger(__name__)

@admin_required
def settings_command(message: Message):
    chat_id = str(message.chat.id)

    # Разбираем команду
    command_parts = message.text.split(maxsplit=2)

    # Если команда вызвана без параметров, выводим текущие настройки
    if len(command_parts) == 1:
        try:
            group_controller = GroupController(chat_id)
            group_result = group_controller.get()

            if not group_result["success"]:
                bot.send_message(chat_id, f"❌ Не удалось получить информацию о группе: {group_result['error']}")
                return

            group = group_result["group"]

            settings_text = (
                f"⚙️ Текущие настройки группы:\n"
                f"- Фильтр спама (spam): {'✅' if group.settings.spam_filter else '❌'}\n"
                f"- Фильтр нецензурной лексики (profanity): {'✅' if group.settings.profanity_filter else '❌'}\n"
                f"- Фильтр капслока (caps): {'✅' if group.settings.caps_filter else '❌'}\n"
                f"- Блокировка ссылок (links): {'✅' if group.settings.links_filter else '❌'}\n"
                f"- ИИ фильтр (ai): {'✅' if group.settings.ai_filter else '❌'}\n"
                f"- Small talk (talk): {'✅' if group.settings.small_talk else '❌'}"
            )
            bot.send_message(chat_id, settings_text)
        except Exception as e:
            logger.error(f"Ошибка получения настроек группы {chat_id}: {e}")
            bot.send_message(chat_id, "❌ Произошла ошибка при получении настроек группы.")
        return

    # Обновление настройки
    if len(command_parts) == 3:
        setting_name = command_parts[1].lower()
        setting_value = command_parts[2].lower()

        if setting_value not in ["on", "off"]:
            bot.send_message(chat_id, "❌ Используйте on или off для изменения настройки.")
            return

        try:
            group_controller = GroupController(chat_id)
            group_result = group_controller.get()

            if not group_result["success"]:
                bot.send_message(chat_id, f"❌ Не удалось получить информацию о группе: {group_result['error']}")
                return

            group = group_result["group"]

            # Обновляем указанную настройку
            if setting_name == "spam":
                group.settings.spam_filter = (setting_value == "on")
            elif setting_name == "profanity":
                group.settings.profanity_filter = (setting_value == "on")
            elif setting_name == "caps":
                group.settings.caps_filter = (setting_value == "on")
            elif setting_name == "links":
                group.settings.links_filter = (setting_value == "on")
            elif setting_name == "ai":
                group.settings.ai_filter = (setting_value == "on")
            elif setting_name == "talk":
                group.settings.small_talk = (setting_value == "on")
            else:
                bot.send_message(chat_id, "❌ Указанная настройка не существует.")
                return

            # Сохраняем изменения
            update_result = group_controller.post(group)

            if update_result["success"]:
                bot.send_message(chat_id, f"✅ Настройка '{setting_name}' успешно изменена на {'Включен' if setting_value == 'on' else 'Выключен'}.")
                logger.info(f"Настройка '{setting_name}' группы {chat_id} изменена на {setting_value}.")
            else:
                bot.send_message(chat_id, f"❌ Ошибка обновления настройки: {update_result['error']}")
        except Exception as e:
            logger.error(f"Ошибка обновления настройки '{setting_name}' группы {chat_id}: {e}")
            bot.send_message(chat_id, "❌ Произошла ошибка при обновлении настройки.")
