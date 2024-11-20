import { ChatSettingsRepository } from "../infrastructure/repositories/ChatSettingsRepository";
import { MessageRepository } from "../infrastructure/repositories/MessageRepository";
import { UserRepository } from "../infrastructure/repositories/UserRepository";
import { Message } from "../domain/entities/Message";
import { User } from "../domain/entities/User";
import TelegramBot from "node-telegram-bot-api";
import {ChatSettings} from "../domain/entities/ChatSettings";

const settingsRepo = new ChatSettingsRepository();
const messageRepo = new MessageRepository();
const userRepo = new UserRepository();

export const messageHandler = async (bot: TelegramBot, msg: TelegramBot.Message) => {
    const chatId = msg.chat.id;

    // Получить настройки чата
    const settings = await settingsRepo.findByChatId(chatId) || new ChatSettings(chatId);

    // Логирование сообщений
    if (settings.logMessages && msg.text) {
        const message = new Message(
            msg.message_id.toString(),
            chatId,
            msg.from?.id || 0,
            msg.text,
            new Date()
        );
        await messageRepo.save(message);
        console.log(`Сообщение сохранено: ${message.content}`);
    }

    // Логирование пользователей
    if (settings.logUsers && msg.from) {
        const user = new User(
            msg.from.id,
            msg.from.username || null,
            msg.from.first_name || "unknown",
            msg.from.last_name || null,
            new Date()
        );
        await userRepo.save(user, chatId);
        console.log(`Пользователь сохранён: ${user.getDisplayName()}`);
    }
};
