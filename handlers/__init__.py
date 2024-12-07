from bot import bot
from handlers.commands import update_command, info_command, hello_command, mute_command, unmute_command, \
    settings_command
from handlers.message_validator import message_validator
from handlers.observers import observe_group_info, observe_member_update, message_observer, notify


def register_commands():
    bot.message_handler(commands=['update'])(update_command)
    bot.message_handler(commands=['info'])(info_command)
    bot.message_handler(commands=['hello'])(hello_command)
    bot.message_handler(commands=['mute'])(mute_command)
    bot.message_handler(commands=['unmute'])(unmute_command)
    bot.message_handler(commands=['settings'])(settings_command)

def register_observers():
    bot.message_handler(content_types=['new_chat_title', 'new_chat_description'])(
        lambda m: observe_group_info(m))
    bot.message_handler(content_types=['new_chat_members'])(
        lambda m: observe_member_update(m))
    bot.message_handler(content_types=['text'])(message_observer)

    notify()
