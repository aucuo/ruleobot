import { db } from "../../firebase";
import { Message } from "../../domain/entities/Message";

export class MessageRepository {
    private getMessagesRef(chatId: number) {
        return db.collection("chats").doc(chatId.toString()).collection("messages");
    }

    async save(message: Message): Promise<void> {
        const ref = this.getMessagesRef(message.chatId).doc(message.id);
        await ref.set({
            userId: message.userId,
            content: message.content,
            timestamp: message.timestamp,
        });
    }

    async findById(chatId: number, messageId: string): Promise<Message | null> {
        const doc = await this.getMessagesRef(chatId).doc(messageId).get();
        if (!doc.exists) return null;
        const data = doc.data()!;
        return new Message(messageId, chatId, data.userId, data.content, data.timestamp.toDate());
    }

    async findAllByChat(chatId: number): Promise<Message[]> {
        const snapshot = await this.getMessagesRef(chatId).get();
        return snapshot.docs.map((doc) => {
            const data = doc.data();
            return new Message(doc.id, chatId, data.userId, data.content, data.timestamp.toDate());
        });
    }
}