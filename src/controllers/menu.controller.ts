import { Context } from "telegraf";
import fs from "fs";
import path from "path";

// Функция для динамического импорта классов меню
async function getMenuClass(menuName: string) {
    try {
        const menuPath = path.join(__dirname, `../views/${menuName}Menu.ts`);
        if (fs.existsSync(menuPath)) {
            const importedModule = await import(menuPath);
            return importedModule[`${capitalizeFirstLetter(menuName)}Menu`];
        }
    } catch (error) {
        console.error(`Ошибка импорта меню ${menuName}:`, error);
    }
    return null;
}

// Вспомогательная функция для капитализации первого символа
function capitalizeFirstLetter(string: string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}

export async function handleMenuAction(ctx: Context) {
    if (!ctx.callbackQuery || !("data" in ctx.callbackQuery)) {
        await ctx.reply("Некорректный запрос.");
        return;
    }

    const callbackData = ctx.callbackQuery.data || "";
    const [menu, action] = callbackData.split(":");

    const MenuClass = await getMenuClass(menu);

    if (MenuClass) {
        const menuInstance = new MenuClass(ctx);

        // Удаляем старое сообщение (если возможно)
        const chatId = ctx.chat?.id;
        const callbackMessageId = ctx.callbackQuery.message?.message_id;

        if (chatId && callbackMessageId) {
            try {
                await ctx.telegram.deleteMessage(chatId, callbackMessageId);
            } catch (error) {
                console.warn("Ошибка удаления старого меню:", error);
            }
        }

        await menuInstance.handleAction(action || "");
    } else {
        await ctx.reply("Неизвестное меню.");
    }

    await ctx.answerCbQuery();
}
