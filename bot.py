import logging
import os
import asyncio
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

# Импорт обработчиков
from handlers import commands, callbacks, messages, goals, materials, test, registration
from config import settings

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
bot = Bot(token=settings.BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


# Регистрация обработчиков
def register_handlers(dispatcher):
    commands.register_handlers(dispatcher)
    callbacks.register_handlers(dispatcher)
    goals.register_handlers(dispatcher)
    materials.register_handlers(dispatcher)
    test.register_handlers(dispatcher)
    registration.register_registration_handlers(dispatcher)
    messages.register_handlers(dispatcher)


async def on_startup():
    logger.info("Бот запущен")
    # Здесь может быть дополнительная инициализация


async def on_shutdown():
    logger.info("Бот остановлен")
    # Закрытие соединений, очистка ресурсов и т.д.


async def main():
    # Регистрация обработчиков
    register_handlers(dp)

    # Установка хэндлеров для запуска и завершения
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    # Запуск бота
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())  # Заменяет executor.start_polling()