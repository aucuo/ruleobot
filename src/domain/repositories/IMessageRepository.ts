import { Message } from "../entities/Message";

export interface IMessageRepository {
    save(message: Message): Promise<void>; // Сохранение сообщения
    findById(messageId: string): Promise<Message | null>; // Поиск сообщения по ID
    findByChat(chatId: number): Promise<Message[]>; // Все сообщения в чате
    delete(messageId: string): Promise<void>; // Удаление сообщения
}
