import { Context } from "telegraf";
import { saveUser } from "../models/user.model";
import { MainMenu } from "../views/mainMenu";

export async function handleStartCommand(ctx: Context) {
    const user = ctx.from;
    if (user) {
        const userData = {
            firstName: user.first_name || "Неизвестно",
            lastName: user.last_name || "Неизвестно",
            username: user.username || "Не задан",
            telegramId: user.id,
            timestamp: new Date().toISOString(),
        };

        try {
            // Удаляем все сообщения от бота
            let messageId = ctx.message?.message_id;
            while (messageId) {
                try {
                    await ctx.deleteMessage(messageId);
                } catch (error) {
                    console.warn("Не удалось удалить сообщение:", error);
                    break;
                }
                messageId--;
            }

            // Сохраняем информацию о пользователе
            await saveUser(userData);

            // Отправляем новое приветственное сообщение
            await ctx.reply("Добро пожаловать в @ruleobot");
            await new MainMenu(ctx).show();
        } catch (error) {
            console.error("Ошибка сохранения пользователя:", error);
            await ctx.reply("Произошла ошибка при сохранении данных пользователя.");
        }
    } else {
        await ctx.reply("Не удалось получить информацию о пользователе.");
    }
}
