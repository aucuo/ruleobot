import { Telegraf, Context } from "telegraf";
import * as dotenv from "dotenv";
import { handleStartCommand } from "./controllers/command.controller";
import { handleMenuAction } from "./controllers/menu.controller";

dotenv.config();

const bot = new Telegraf<Context>(process.env.TELEGRAM_API_TOKEN!);

// Команда /start
bot.command("start", handleStartCommand);

// Обработка нажатий на кнопки
bot.on("callback_query", handleMenuAction);

(async () => {
    try {
        await bot.launch();
        console.log("Бот запущен!");
    } catch (error) {
        console.error("Ошибка запуска бота:", error);
    }
})();
