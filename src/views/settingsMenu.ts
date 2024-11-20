import { MenuBase } from "./menuBase";
import { MainMenu } from "./mainMenu";

export class SettingsMenu extends MenuBase {
    protected title = "Настройки";
    protected text = "Настройки вашего приложения:";
    protected keyboard = {
        inline_keyboard: [
            [{ text: "Логирование сообщений", callback_data: "settings:toggle_logging" }],
            [{ text: "Назад", callback_data: "settings:main" }],
        ],
    };

    async handleAction(action: string): Promise<void> {
        switch (action) {
            case "toggle_logging":
                await this.ctx.reply("Функция логирования сообщений переключена.");
                break;
            case "main":
                await new MainMenu(this.ctx).show();
                break;
            default:
                await this.ctx.reply("Неизвестное действие.");
        }
    }
}
