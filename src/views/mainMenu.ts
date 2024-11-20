import { MenuBase } from "./menuBase";
import { SettingsMenu } from "./settingsMenu";
import { InfoMenu } from "./infoMenu";

export class MainMenu extends MenuBase {
    protected title = "Главное меню";
    protected text = "Выберите действие:";
    protected keyboard = {
        inline_keyboard: [
            [{ text: "Настройки", callback_data: "main:settings" }],
            [{ text: "Информация", callback_data: "main:info" }],
        ],
    };

    async handleAction(action: string): Promise<void> {
        switch (action) {
            case "settings":
                await new SettingsMenu(this.ctx).show();
                break;
            case "info":
                await new InfoMenu(this.ctx).show();
                break;
            default:
                await this.ctx.reply("Неизвестное действие.");
        }
    }
}
