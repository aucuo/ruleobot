export class Message {
    constructor(
        public id: string, // Уникальный идентификатор сообщения
        public chatId: number, // ID чата, где отправлено сообщение
        public userId: number, // ID пользователя, который отправил сообщение
        public content: string, // Текст сообщения
        public timestamp: Date // Время отправки сообщения
    ) {}

    // Проверка, является ли сообщение пустым
    isEmpty(): boolean {
        return this.content.trim() === "";
    }

    // Получение сокращённого текста сообщения
    getPreview(length: number = 20): string {
        return this.content.length > length
            ? this.content.substring(0, length) + "..."
            : this.content;
    }
}
