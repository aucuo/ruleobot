import logging
from datetime import datetime, timedelta
from telebot.types import Message
from managers import MessageManager, UserManager, SettingsManager, GroupManager
from bot import bot

logger = logging.getLogger(__name__)

# Загрузка списка запрещенных слов на русском языке из текстового файла
with open('profanity_list.txt', 'r', encoding='utf-8') as file:
    PROFANITY_LIST = file.read().splitlines()

def contains_profanity(text):
    """
    Проверяет, содержит ли текст слова из списка запрещенных (для русского языка).
    """
    text_lower = text.lower()
    for word in PROFANITY_LIST:
        if word in text_lower:
            return True
    return False

def message_handler(message: Message):
    if message.chat.type in ['group', 'supergroup']:
        chat_id = message.chat.id
        user = message.from_user
        user_id = user.id

        # Проверка наличия пользователя в базе данных и добавление, если отсутствует
        user_data = UserManager.load_user(chat_id, user_id)
        if not user_data:
            # Если пользователя нет в базе данных, добавляем его
            username = user.username
            first_name = user.first_name
            last_name = user.last_name
            user_data = UserManager.add_member(chat_id, user_id, username, first_name, last_name)
            logger.info(f"Пользователь {user_id} добавлен в базу данных.")

        # Проверка мьюта пользователя
        if user_data and user_data.mutes:
            mute_until_str = user_data.mutes[-1].get('mute_until')
            if mute_until_str:
                mute_until = datetime.fromisoformat(mute_until_str)
                current_time = datetime.now()
                if mute_until > current_time:
                    # Если пользователь все еще в мьюте, удаляем сообщение и отправляем сообщение в группу с упоминанием пользователя
                    remaining_time = mute_until - current_time
                    minutes, seconds = divmod(remaining_time.total_seconds(), 60)
                    remaining_time_str = f"{int(minutes)} минут и {int(seconds)} секунд"

                    bot.send_message(chat_id, f"@{user.username}, вы не можете отправлять сообщения до истечения времени мьюта. Время до разблокировки: {remaining_time_str}", reply_to_message_id=message.message_id)
                    logger.info(f"Сообщение от пользователя user_id={user_id} в группе chat_id={chat_id} было удалено, так как пользователь находится в мьюте.")
                    bot.delete_message(chat_id, message.message_id)
                    return
                else:
                    # Если срок мьюта истек, удаляем запись о мьюте
                    UserManager.unmute_user(chat_id, user_id)
                    logger.info(f"Срок мьюта истек, запись о мьюте удалена для пользователя user_id={user_id} в группе chat_id={chat_id}.")

        # Проверка и установка ownerId, если его нет
        GroupManager.initialize_owner(chat_id, bot)

        # Логирование сообщений и обновление участников
        date = datetime.now().isoformat()

        # Увеличение счетчика сообщений
        MessageManager.increment_message_count(chat_id)

        # Логирование сообщения
        MessageManager.log_message(chat_id, user_id, message.message_id, message.text, date)

        # Проверка на спам
        recent_messages = MessageManager.get_user_recent_messages(chat_id, user_id, minutes=1)
        if len(recent_messages) > 6:
            # Если пользователь отправляет более 6 сообщений за последнюю минуту
            warning_reason = "Спам (большое количество сообщений за короткое время)"
            UserManager.add_warning(chat_id, user_id, warning_reason, date)
            bot.delete_message(chat_id, message.message_id)
            bot.send_message(chat_id, f"⚠️ @{user.username}, вы получили предупреждение за спам. Текущее количество предупреждений: {len(UserManager.load_user(chat_id, user_id).warnings)}")

            logger.info(f"Предупреждение добавлено пользователю {user_id} за спам.")

        # Получение настроек группы
        settings = SettingsManager.get_settings(chat_id)

        # Проверка на капс
        if settings.get("caps") and message.text.isupper():
            bot.delete_message(chat_id, message.message_id)
            # Добавляем предупреждение за капс
            warning_reason = "Использование капса"
            UserManager.add_warning(chat_id, user_id, warning_reason, date)
            bot.send_message(chat_id, f"⚠️ @{user.username}, ваше сообщение было удалено за использование капса. Текущее количество предупреждений: {len(UserManager.load_user(chat_id, user_id).warnings)}")
            logger.info(f"Предупреждение добавлено пользователю {user_id} за использование капса.")

        # Проверка на наличие мата
        elif settings.get("profanity") and contains_profanity(message.text):
            bot.delete_message(chat_id, message.message_id)
            # Добавляем предупреждение за мат
            warning_reason = "Использование ненормативной лексики"
            UserManager.add_warning(chat_id, user_id, warning_reason, date)
            bot.send_message(chat_id, f"⚠️ @{user.username}, ваше сообщение было удалено за использование ненормативной лексики. Текущее количество предупреждений: {len(UserManager.load_user(chat_id, user_id).warnings)}")
            logger.info(f"Предупреждение добавлено пользователю {user_id} за использование ненормативной лексики.")

        # Проверка количества предупреждений и выдача мьюта
        updated_user = UserManager.load_user(chat_id, user_id)
        warning_count = len(updated_user.warnings)
        if warning_count > 3:
            # Рассчитываем дополнительное время мьюта за каждое предупреждение больше трех
            extra_minutes = (warning_count - 3) * 10
            mute_duration = 30 + extra_minutes
            mute_reason = "Превышение допустимого количества предупреждений"

            # Формируем запись о мьюте
            mute_until = datetime.now() + timedelta(minutes=mute_duration)
            mute_entry = {
                "reason": mute_reason,
                "mute_until": mute_until.isoformat()
            }
            UserManager.mute_user(chat_id, user_id, mute_entry)

            # Очищаем все предупреждения после мьюта
            UserManager.clear_warnings(chat_id, user_id)

            bot.send_message(chat_id, f"🔇 @{user.username} был замучен на {mute_duration} минут за превышение допустимого количества предупреждений.")
            logger.info(f"Пользователь @{user.username} (user_id={user_id}) был замучен на {mute_duration} минут в группе chat_id={chat_id}.")
            return
