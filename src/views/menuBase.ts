import { Context } from "telegraf";

export abstract class MenuBase {
    protected title: string = "";
    protected text: string = "";
    protected keyboard: any;

    constructor(protected ctx: Context) {}

    // Метод для отображения меню
    async show() {
        const options = {
            reply_markup: this.keyboard,
        };
        const content = `${this.title}\n\n${this.text}`;

        const shouldEdit = !!this.ctx.callbackQuery;

        if (shouldEdit) {
            try {
                await this.ctx.editMessageText(content, options);
            } catch (error) {
                console.warn("Не удалось отредактировать сообщение, отправляем новое:", error);
                await this.ctx.reply(content, options);
            }
        } else {
            await this.ctx.reply(content, options);
        }
    }


    // Обработка нажатий (переопределяется в наследниках)
    abstract handleAction(action: string): Promise<void>;
}
