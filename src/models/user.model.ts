import {db} from "../utils/firebase";

export interface User {
    firstName: string;
    lastName: string;
    username: string;
    telegramId: number;
    timestamp: string;
}

// Сохранение пользователя в базу данных
export async function saveUser(user: User): Promise<void> {
    await db.collection("users").doc(`${user.telegramId}`).set(user, { merge: true });
}

// Получение информации о пользователе
export async function getUser(telegramId: number): Promise<User | null> {
    const doc = await db.collection("users").doc(`${telegramId}`).get();
    return doc.exists ? (doc.data() as User) : null;
}
