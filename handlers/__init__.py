from telebot import types
from bot import bot
from handlers.commands import (
    update_command, info_command, hello_command, mute_command, unmute_command,
    settings_command, warn_command, unwarn_command, ask_command,
    memberstats_command, messagestats_command, gem_command
)
from handlers.commands.gem_command import gem_command
from handlers.message_validator import message_validator
from handlers.observers import observe_group_info, observe_member_update, message_observer, notify


def register_commands():
    commands_list = {
        'ask': (ask_command, "Отправить вопрос создателю группы"),
        'gem': (gem_command, "Спросить у Gemini вопрос"),
        'hello': (hello_command, "Установить приветственное сообщение (только для админа)"),
        'info': (info_command, "Получить информацию о группе или пользователе"),  
        'memberstats': (memberstats_command, "Посмотреть статистику новых участников"),  
        'messagestats': (messagestats_command, "Получить статистику сообщений"),  
        'mute': (mute_command, "Заглушить участника: /mute @username <минуты> <причина> (только для админа)"),  
        'settings': (settings_command, "Просмотреть или изменить настройки группы: /settings <параметр> <on|off> (только для админа)"),  
        'start': (update_command, "Запустить бота (только для админа)"),
        'unmute': (unmute_command, "Снять мут с участника: /unmute @username (только для админа)"),
        'unwarn': (unwarn_command, "Снять предупреждение у участника: /unwarn @username [-all] (только для админа)"),  
        'update': (update_command, "Обновить данные группы (только для админа)"),  
        'warn': (warn_command, "Выдать предупреждение участнику: /warn @username <причина> (только для админа)")  
    }

    for command, (handler, _) in commands_list.items():
        bot.message_handler(commands=[command])(handler)

    bot.set_my_commands([types.BotCommand(cmd, desc) for cmd, (_, desc) in commands_list.items()])

def register_observers():
    observers_list = {
        'new_chat_title': observe_group_info,
        'new_chat_description': observe_group_info,
        'new_chat_members': observe_member_update,
        'text': message_observer
    }

    for content_type, handler in observers_list.items():
        bot.message_handler(content_types=[content_type])(handler)

    notify()
