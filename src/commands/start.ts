import TelegramBot from "node-telegram-bot-api";

export const startCommand = (bot: TelegramBot) => {
    bot.onText(/\/start/, (msg) => {
        const chatId = msg.chat.id;
        bot.sendMessage(chatId, "Бот запущен! Чем могу помочь?");
    });
};