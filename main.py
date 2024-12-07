# main.py
from handlers import register_commands, register_observers
from bot import bot

def main():
    # Инициализация бота

    register_commands()
    register_observers()

    # Запуск бота
    print("Бот запущен и работает...")
    bot.infinity_polling()

if __name__ == "__main__":
    main()
