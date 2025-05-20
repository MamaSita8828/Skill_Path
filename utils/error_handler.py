import logging
from functools import wraps
from aiogram.exceptions import TelegramAPIError
from config import settings

logger = logging.getLogger(__name__)

def handle_errors(func):
    """Декоратор для обработки ошибок в асинхронных функциях."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except TelegramAPIError as e:
            logger.error(f"Ошибка Telegram API: {e}")
            # Здесь можно добавить уведомление администраторов
            if settings.DEBUG:
                raise
        except Exception as e:
            logger.error(f"Неожиданная ошибка в {func.__name__}: {e}")
            if settings.DEBUG:
                raise
    return wrapper

async def notify_admins(bot, message: str):
    """Отправка уведомления администраторам."""
    for admin_id in settings.ADMIN_IDS:
        try:
            await bot.send_message(admin_id, f"⚠️ Уведомление: {message}")
        except Exception as e:
            logger.error(f"Не удалось отправить уведомление администратору {admin_id}: {e}")

def log_error(error: Exception, context: str = ""):
    """Логирование ошибок с контекстом."""
    logger.error(f"Ошибка в {context}: {str(error)}", exc_info=True)
    if settings.DEBUG:
        raise error 