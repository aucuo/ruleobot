import { MenuBase } from "./menuBase";
import { User } from "../models/user.model";

export class InfoMenu extends MenuBase {
    protected title = "Ваш аккаунт 🧑‍💻";
    protected text = "Информация о вашем аккаунте:";
    protected keyboard = {
        inline_keyboard: [[{ text: "Назад", callback_data: "info:main" }]],
    };

    async handleAction(action: string): Promise<void> {
        if (action === "main") {
            await this.goTo(require("./mainMenu").MainMenu);
        } else {
            await this.handleUnknownAction();
        }
    }

    async show() {
        try {
            const user = await User.getById(this.ctx.from!.id);
            this.text = user
                ? `👤 *Имя:* ${user.firstName}\n👥 *Фамилия:* ${user.lastName}\n🔗 *Юзернейм:* ${user.username}\n🆔 *ID:* ${user.telegramId}\n📦 *Подписка:* ${user.subscription.type}`
                : "❌ Информация о вас отсутствует в базе данных.";
        } catch {
            this.text = "🚨 Произошла ошибка при загрузке данных.";
        }
        await super.show();
    }
}
