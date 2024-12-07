import firebase_admin
from firebase_admin import credentials, db
import logging

from config import FIREBASE_URL, SERVICE_ACCOUNT_FILE

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация Firebase SDK
try:
    cred = credentials.Certificate(SERVICE_ACCOUNT_FILE)
    firebase_admin.initialize_app(cred, {
        'databaseURL': FIREBASE_URL
    })
    logger.info("Firebase успешно инициализирован.")
except Exception as e:
    logger.error(f"Ошибка инициализации Firebase: {e}")
    raise e

# Получение ссылки на корень базы данных
firebase_db = db.reference('/')