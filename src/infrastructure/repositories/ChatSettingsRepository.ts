import { db } from "../../firebase";
import { ChatSettings } from "../../domain/entities/ChatSettings";

export class ChatSettingsRepository {
    private getSettingsRef(chatId: number) {
        return db.collection("chats").doc(chatId.toString()).collection("settings").doc("default");
    }

    async findByChatId(chatId: number): Promise<ChatSettings | null> {
        const doc = await this.getSettingsRef(chatId).get();
        if (!doc.exists) return null;
        const data = doc.data()!;
        return new ChatSettings(chatId, data.logMessages, data.logUsers);
    }

    async save(chatSettings: ChatSettings): Promise<void> {
        const ref = this.getSettingsRef(chatSettings.chatId);
        await ref.set({
            logMessages: chatSettings.logMessages,
            logUsers: chatSettings.logUsers,
        }, { merge: true });
    }
}
