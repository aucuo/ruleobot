export class User {
    constructor(
        public id: number, // Уникальный ID пользователя
        public username: string | null, // Имя пользователя
        public firstName: string, // Имя
        public lastName: string | null, // Фамилия
        public lastActive: Date // Последняя активность
    ) {}

    // Возвращает отображаемое имя пользователя
    getDisplayName(): string {
        return this.username || `${this.firstName} ${this.lastName || ""}`.trim();
    }

    // Обновляет время последней активности
    updateLastActive(): void {
        this.lastActive = new Date();
    }
}