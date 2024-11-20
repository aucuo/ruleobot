export class ChatSettings {
    constructor(
        public chatId: number, // ID чата
        public logMessages: boolean = true, // Логирование сообщений
        public logUsers: boolean = true // Логирование пользователей
    ) {}

    // Включение логирования сообщений
    enableLogMessages(): void {
        this.logMessages = true;
    }

    // Выключение логирования сообщений
    disableLogMessages(): void {
        this.logMessages = false;
    }

    // Включение логирования пользователей
    enableLogUsers(): void {
        this.logUsers = true;
    }

    // Выключение логирования пользователей
    disableLogUsers(): void {
        this.logUsers = false;
    }
}