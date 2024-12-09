from bot import bot
from handlers.commands import update_command, info_command, hello_command, mute_command, unmute_command, \
    settings_command, warn_command, unwarn_command
from handlers.commands.ask_command import ask_command
from handlers.commands.memberstats_command import memberstats_command
from handlers.commands.messagestats_command import messagestats_command
from handlers.message_validator import message_validator
from handlers.observers import observe_group_info, observe_member_update, message_observer, notify


def register_commands():
    bot.message_handler(commands=['update'])(update_command)
    bot.message_handler(commands=['info'])(info_command)
    bot.message_handler(commands=['hello'])(hello_command)
    bot.message_handler(commands=['mute'])(mute_command)
    bot.message_handler(commands=['unmute'])(unmute_command)
    bot.message_handler(commands=['warn'])(warn_command)
    bot.message_handler(commands=['unwarn'])(unwarn_command)
    bot.message_handler(commands=['settings'])(settings_command)
    bot.message_handler(commands=['messagestats'])(messagestats_command)
    bot.message_handler(commands=['memberstats'])(memberstats_command)
    bot.message_handler(commands=['ask'])(ask_command)

def register_observers():
    bot.message_handler(content_types=['new_chat_title', 'new_chat_description'])(
        lambda m: observe_group_info(m))
    bot.message_handler(content_types=['new_chat_members'])(
        lambda m: observe_member_update(m))
    bot.message_handler(content_types=['text'])(message_observer)

    notify()
