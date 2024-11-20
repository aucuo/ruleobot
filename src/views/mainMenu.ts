import { MenuBase } from "./menuBase";
import { SubscriptionMenu } from "./subscriptionMenu";
import { InfoMenu } from "./infoMenu";
import {ParseMode} from "node-telegram-bot-api";

export class MainMenu extends MenuBase {
    protected title = "Главное меню 🏠";
    protected text = "📋 *Выберите действие:*";
    protected keyboard = {
        inline_keyboard: [
            [{ text: "ℹ️ Информация", callback_data: "main:info" }],
            [{ text: "📦 Подписка", callback_data: "main:subscription" }],
        ],
    };

    async handleAction(action: string): Promise<void> {
        switch (action) {
            case "info":
                await new InfoMenu(this.ctx).show();
                break;
            case "subscription":
                await new SubscriptionMenu(this.ctx).show();
                break;
            default:
                await this.ctx.reply("⚠️ Неизвестное действие.", { parse_mode: "Markdown" as ParseMode });
        }
    }
}
