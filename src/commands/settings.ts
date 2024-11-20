import TelegramBot from "node-telegram-bot-api";
import { ChatSettingsService } from "../domain/services/ChatSettingsService";
import { ChatSettingsRepository } from "../infrastructure/repositories/ChatSettingsRepository";

const repository = new ChatSettingsRepository();
const settingsService = new ChatSettingsService(repository);

export const registerSettingsCommands = (bot: TelegramBot) => {
    bot.onText(/\/log_messages_on/, async (msg) => {
        const chatId = msg.chat.id;
        const settings = await settingsService.getOrCreateSettings(chatId);
        settings.enableLogMessages();
        await settingsService.updateSettings(settings);
        bot.sendMessage(chatId, "Логирование сообщений включено.");
    });

    bot.onText(/\/log_messages_off/, async (msg) => {
        const chatId = msg.chat.id;
        const settings = await settingsService.getOrCreateSettings(chatId);
        settings.disableLogMessages();
        await settingsService.updateSettings(settings);
        bot.sendMessage(chatId, "Логирование сообщений выключено.");
    });

    bot.onText(/\/log_users_on/, async (msg) => {
        const chatId = msg.chat.id;
        const settings = await settingsService.getOrCreateSettings(chatId);
        settings.enableLogUsers();
        await settingsService.updateSettings(settings);
        bot.sendMessage(chatId, "Логирование пользователей включено.");
    });

    bot.onText(/\/log_users_off/, async (msg) => {
        const chatId = msg.chat.id;
        const settings = await settingsService.getOrCreateSettings(chatId);
        settings.disableLogUsers();
        await settingsService.updateSettings(settings);
        bot.sendMessage(chatId, "Логирование пользователей выключено.");
    });
};
