from aiogram import Router, F
from aiogram.types import Message

from utils.error_handler import handle_errors
from utils.messages import get_message, normalize_lang, get_user_lang
from utils.keyboards import get_main_keyboard
import aiohttp

router = Router()

@router.message()
@handle_errors
async def handle_unknown_message(message: Message):
    """Обработка неизвестных сообщений."""
    lang = await get_user_lang(message.from_user.id)
    await message.answer(
        get_message("unknown_command", lang),
        reply_markup=get_main_keyboard(lang)
    )

def register_handlers(dispatcher):
    """Регистрация обработчиков."""
    dispatcher.include_router(router)