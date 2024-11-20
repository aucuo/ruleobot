import { db } from "../../firebase";
import { User } from "../../domain/entities/User";

export class UserRepository {
    private getUsersRef(chatId: number) {
        return db.collection("chats").doc(chatId.toString()).collection("users");
    }

    async save(user: User, chatId: number): Promise<void> {
        const ref = this.getUsersRef(chatId).doc(user.id.toString());
        await ref.set({
            username: user.username,
            firstName: user.firstName,
            lastName: user.lastName,
            lastActive: user.lastActive,
        }, { merge: true });
    }

    async findById(chatId: number, userId: number): Promise<User | null> {
        const doc = await this.getUsersRef(chatId).doc(userId.toString()).get();
        if (!doc.exists) return null;
        const data = doc.data()!;
        return new User(userId, data.username, data.firstName, data.lastName, data.lastActive.toDate());
    }
}