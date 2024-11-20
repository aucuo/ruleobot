import { MenuBase } from "./menuBase";
import { MainMenu } from "./mainMenu";
import { getUser } from "../models/user.model";

export class InfoMenu extends MenuBase {
    protected title = "Информация";
    protected text = "Информация о вашем аккаунте:";
    protected keyboard = {
        inline_keyboard: [
            [{ text: "Назад", callback_data: "info:main" }],
        ],
    };

    async handleAction(action: string): Promise<void> {
        switch (action) {
            case "main":
                await new MainMenu(this.ctx).show();
                break;
            default:
                await this.ctx.reply("Неизвестное действие.");
        }
    }

    async show() {
        const user = this.ctx.from;
        if (user) {
            const userInfo = await getUser(user.id);
            this.text = userInfo
                ? `Имя: ${userInfo.firstName}\nФамилия: ${userInfo.lastName}\nЮзернейм: ${userInfo.username}\nID: ${userInfo.telegramId}\nДата регистрации: ${new Date(
                    userInfo.timestamp
                ).toLocaleString()}`
                : "Информация о вас отсутствует в базе данных.";
        } else {
            this.text = "Не удалось получить информацию о пользователе.";
        }
        await super.show();
    }
}
