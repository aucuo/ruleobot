import { Context } from "telegraf";
import { MainMenu } from "../views/mainMenu";
import { SettingsMenu } from "../views/settingsMenu";
import { InfoMenu } from "../views/infoMenu";

export async function handleMenuAction(ctx: Context) {
    const callbackData = (ctx.callbackQuery as ICallbackQuery).data;
    if (!callbackData) return;

    const menus = {
        main: new MainMenu(ctx),
        settings: new SettingsMenu(ctx),
        info: new InfoMenu(ctx),
    };

    const [menu, action] = callbackData.split(":");
    const menuInstance = menus[menu as keyof typeof menus];

    if (menuInstance) {
        await menuInstance.handleAction(action || menu);
    } else {
        await ctx.reply("Неизвестное меню.");
    }

    await ctx.answerCbQuery();
}
interface ICallbackQuery {
    data: string;
}