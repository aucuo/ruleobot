import { Context } from "telegraf";
import {ParseMode} from "node-telegram-bot-api";

export abstract class MenuBase {
    protected title: string = "";
    protected text: string = "";
    protected keyboard: any;

    constructor(protected ctx: Context) {}

    async show(forceToBottom = false) {
        const content = `*${this.title}*\n\n${this.text}`;
        const options = {
            reply_markup: this.keyboard,
            parse_mode: "Markdown" as ParseMode, // Добавляем поддержку Markdown
        };

        if (forceToBottom) {
            await this.ctx.reply(content, options);
        } else if (this.ctx.callbackQuery) {
            try {
                await this.ctx.editMessageText(content, options);
            } catch {
                await this.ctx.reply(content, options);
            }
        } else {
            await this.ctx.reply(content, options);
        }
    }

    protected async handleUnknownAction() {
        await this.ctx.reply("⚠️ *Неизвестное действие.*", { parse_mode: "Markdown" as ParseMode});
    }

    protected async goTo(menuClass: any) {
        await new menuClass(this.ctx).show();
    }

    abstract handleAction(action: string): Promise<void>;
}
