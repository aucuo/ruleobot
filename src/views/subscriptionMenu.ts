import { MenuBase } from "./menuBase";
import { User } from "../models/user.model";
import { subscriptions } from "../models/subscription.model";

export class SubscriptionMenu extends MenuBase {
    protected title = "Управление подпиской 📦";
    protected text = "🌟 *Выберите новый тип подписки:*";

    private generateKeyboard(currentSubscription: string) {
        const types = ["lite", "extended", "pro"];
        return {
            inline_keyboard: [
                ...types.map(type => [
                    {
                        text: `${type === currentSubscription ? "✅ " : ""}${type}`,
                        callback_data: `subscription:${type}`,
                    },
                ]),
                [{ text: "Назад", callback_data: "subscription:back" }],
            ],
        };
    }

    async handleAction(action: string): Promise<void> {
        const user = await User.getById(this.ctx.from!.id);
        if (!user) {
            this.text = "❌ *Пользователь не найден.*";
            await super.show();
            return;
        }

        if (["lite", "extended", "pro"].includes(action)) {
            user.subscription = subscriptions[action];
            await user.save();
            await this.ctx.reply(`🎉 Подписка обновлена на *${action}*!`);
        } else if (action === "back") {
            await this.goTo(require("./mainMenu").MainMenu);
            return;
        } else {
            await this.handleUnknownAction();
            return;
        }

        this.keyboard = this.generateKeyboard(user.subscription.type);
        await this.show();
    }

    async show() {
        const user = await User.getById(this.ctx.from!.id);
        this.keyboard = user
            ? this.generateKeyboard(user.subscription.type)
            : { inline_keyboard: [[{ text: "Назад", callback_data: "subscription:back" }]] };
        await super.show();
    }
}
