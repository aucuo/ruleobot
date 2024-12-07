from bot import bot

from handlers.commands.hello_command import hello_command
from handlers.commands.info_command import info_command
from handlers.commands.mute_command import mute_command
from handlers.commands.settings_command import settings_command
from handlers.commands.unmute_command import unmute_command
from handlers.commands.update_command import update_command
from handlers.observers.group_observer import observe_group_info
from handlers.observers.member_observer import observe_member_update
from handlers.observers.message_observer import message_observer
from handlers.observers.notify_observer import notify

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
