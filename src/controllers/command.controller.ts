import { Context } from "telegraf";
import { User } from "../models/user.model";
import { MainMenu } from "../views/mainMenu";
import { subscriptions } from "../models/subscription.model";

export async function handleStartCommand(ctx: Context) {
    const user = ctx.from;

    if (user) {
        try {
            // Создаем или обновляем пользователя
            const existingUser = await User.getById(user.id);

            if (!existingUser) {
                const newUser = new User(
                    user.id,
                    "user", // Роль по умолчанию
                    subscriptions.lite // Подписка по умолчанию
                );
                await newUser.save();
            } else {
                // Обновляем информацию, если пользователь уже существует
                existingUser.firstName = user.first_name || "Неизвестно";
                existingUser.lastName = user.last_name || "Неизвестно";
                existingUser.username = user.username || "Не задан";
                await existingUser.save();
            }

            // Удаляем все сообщения от бота
            if (ctx.message?.message_id) {
                const messageId = ctx.message?.message_id;
                for (let id = messageId; id >= messageId - 10; id--) {
                    try {
                        await ctx.deleteMessage(id);
                    } catch {
                        // Игнорируем ошибки удаления
                    }
                }
            }

            // Приветственное сообщение и главное меню
            await ctx.reply("Добро пожаловать в @ruleobot");
            await new MainMenu(ctx).show();
        } catch (error) {
            console.error("Ошибка обработки команды /start:", error);
            await ctx.reply("Произошла ошибка при обработке команды.");
        }
    } else {
        await ctx.reply("Не удалось определить информацию о вас.");
    }
}