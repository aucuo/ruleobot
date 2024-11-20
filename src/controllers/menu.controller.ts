import { Context } from "telegraf";
import { MainMenu } from "../views/mainMenu";
import { InfoMenu } from "../views/infoMenu";
import { SubscriptionMenu } from "../views/subscriptionMenu";

const menuRegistry = {
    main: MainMenu,
    info: InfoMenu,
    subscription: SubscriptionMenu,
};

export async function handleMenuAction(ctx: Context) {
    if (!ctx.callbackQuery || !("data" in ctx.callbackQuery)) {
        await ctx.reply("Некорректный запрос.");
        return;
    }

    const callbackData = ctx.callbackQuery.data || "";
    const [menu, action] = callbackData.split(":");

    const MenuClass = menuRegistry[menu as keyof typeof menuRegistry];

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
