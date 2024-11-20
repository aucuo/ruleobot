import { Message } from "../entities/Message";
import { IMessageRepository } from "../repositories/IMessageRepository";

export class MessageService {
    constructor(private messageRepository: IMessageRepository) {}

    // Сохранение сообщения
    async saveMessage(message: Message): Promise<void> {
        if (message.isEmpty()) {
            throw new Error("Сообщение не может быть пустым");
        }
        await this.messageRepository.save(message);
    }

    // Получение всех сообщений из чата
    async getMessagesByChat(chatId: number): Promise<Message[]> {
        return this.messageRepository.findByChat(chatId);
    }

    // Удаление сообщения
    async deleteMessage(messageId: string): Promise<void> {
        await this.messageRepository.delete(messageId);
    }
}