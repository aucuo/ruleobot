import {db} from "../utils/firebase";
import {Subscription, subscriptions} from "./subscription.model";

export class User {
    telegramId: number;
    role: "admin" | "user"; // Роль пользователя
    subscription: Subscription; // Подписка пользователя
    groups: string[]; // Список ID групп
    firstName: string; // Имя пользователя
    lastName: string; // Фамилия пользователя
    username: string; // Username пользователя

    constructor(
        telegramId: number,
        role: "admin" | "user" = "user",
        subscription: Subscription = subscriptions.lite,
        groups: string[] = [],
        firstName = "Неизвестно",
        lastName = "Неизвестно",
        username = "Не задан"
    ) {
        this.telegramId = telegramId;
        this.role = role;
        this.subscription = subscription;
        this.groups = groups;
        this.firstName = firstName;
        this.lastName = lastName;
        this.username = username;
    }

    static async getById(telegramId: number): Promise<User | null> {
        const doc = await db.collection("users").doc(`${telegramId}`).get();
        if (!doc.exists) return null;

        const data = doc.data()!;

        // Проверяем наличие поля subscription
        const subscriptionData = data.subscription || { type: "lite", maxGroups: 1 };

        return new User(
            data.telegramId,
            data.role,
            new Subscription(subscriptionData.type, subscriptionData.maxGroups),
            data.groups || [],
            data.firstName || "Неизвестно",
            data.lastName || "Неизвестно",
            data.username || "Не задан"
        );
    }

    async save(): Promise<void> {
        // Преобразуем объект в чистый JavaScript-объект
        const data = this.toPlainObject();
        await db.collection("users").doc(`${this.telegramId}`).set(data, { merge: true });
    }

    // Метод преобразования объекта в чистый объект
    toPlainObject(): Record<string, any> {
        return {
            telegramId: this.telegramId,
            role: this.role,
            subscription: this.subscription.toPlainObject(), // Преобразуем подписку
            groups: this.groups,
            firstName: this.firstName,
            lastName: this.lastName,
            username: this.username,
        };
    }
}
