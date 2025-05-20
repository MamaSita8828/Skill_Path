import pytest
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from bot import register_handlers

@pytest.fixture
async def bot():
    """Фикстура для создания тестового бота."""
    bot = Bot(token="test_token")
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    register_handlers(dp)
    return bot, dp

@pytest.mark.asyncio
async def test_bot_initialization(bot):
    """Тест инициализации бота."""
    bot_instance, dp = bot
    assert bot_instance is not None
    assert dp is not None

@pytest.mark.asyncio
async def test_handlers_registration(bot):
    """Тест регистрации обработчиков."""
    _, dp = bot
    # Проверяем, что диспетчер содержит зарегистрированные обработчики
    assert len(dp.message.handlers) > 0 or len(dp.callback_query.handlers) > 0 