import os
import logging
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv()

# Переменные окружения для бота
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    logger.error("Не найден BOT_TOKEN в переменных окружения.")
    raise ValueError("Не найден BOT_TOKEN в переменных окружения.")

# Переменные окружения для Firebase
SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE")
FIREBASE_URL = os.getenv("FIREBASE_URL")

if not SERVICE_ACCOUNT_FILE:
    logger.error("Не найден SERVICE_ACCOUNT_FILE в переменных окружения.")
    raise ValueError("Не найден SERVICE_ACCOUNT_FILE в переменных окружения.")

if not FIREBASE_URL:
    logger.error("Не найден FIREBASE_URL в переменных окружения.")
    raise ValueError("Не найден FIREBASE_URL в переменных окружения.")

