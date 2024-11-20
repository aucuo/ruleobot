import { ChatSettings } from "../entities/ChatSettings";
import { ChatSettingsRepository } from "../../infrastructure/repositories/ChatSettingsRepository";

export class ChatSettingsService {
    constructor(private repository: ChatSettingsRepository) {}

    // Получить настройки чата, если их нет — создать с настройками по умолчанию
    async getOrCreateSettings(chatId: number): Promise<ChatSettings> {
        let settings = await this.repository.findByChatId(chatId);
        if (!settings) {
            settings = new ChatSettings(chatId); // Настройки по умолчанию
            await this.repository.save(settings);
        }
        return settings;
    }

    // Обновить настройки чата
    async updateSettings(chatSettings: ChatSettings): Promise<void> {
        await this.repository.save(chatSettings);
    }
}
