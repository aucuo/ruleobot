import TelegramBot from "node-telegram-bot-api";
import * as dotenv from "dotenv";
import { startCommand } from "./commands/start";
import { messageHandler } from "./handlers/messageHandler";
import {registerSettingsCommands} from "./commands/settings";

dotenv.config();

const botToken = process.env.TELEGRAM_API_TOKEN || "";
const adminChatId = process.env.ADMIN_CHAT_ID || ""; // Ваш личный Telegram chat ID

if (!botToken || !adminChatId) {
    console.error("Необходимо указать TELEGRAM_API_TOKEN и ADMIN_CHAT_ID в файле .env");
    process.exit(1);
}

const bot = new TelegramBot(botToken, { polling: true });

// Функция для отправки сообщений об ошибках
const sendErrorToAdmin = async (error: Error | string) => {
    const message = typeof error === "string"
        ? error
        : `⚠️ Ошибка:\n\n${error.name}: ${error.message}\n\nStack Trace:\n${error.stack}`;

    try {
        await bot.sendMessage(adminChatId, message);
    } catch (err) {
        console.error("Не удалось отправить сообщение об ошибке в Telegram:", err);
    }
};

// Глобальный обработчик необработанных исключений
process.on("uncaughtException", async (err) => {
    console.error("Необработанное исключение:", err);
    await sendErrorToAdmin(err);
    process.exit(1); // Завершение процесса для предотвращения непредсказуемого состояния
});

// Глобальный обработчик необработанных промисов
process.on("unhandledRejection", async (reason) => {
    console.error("Необработанный отказ промиса:", reason);
    await sendErrorToAdmin(reason as Error);
});

// Подключение обработчиков
bot.on("message", (msg) => messageHandler(bot, msg));
startCommand(bot);
registerSettingsCommands(bot);

export { bot };
