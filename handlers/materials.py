from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from datetime import datetime

from utils.states import MaterialStates
from utils.messages import format_material, get_message, get_user_lang
from utils.keyboards import get_materials_keyboard
from utils.error_handler import handle_errors
from utils.database import db

router = Router()

@router.callback_query(F.data == "add_material")
@handle_errors
async def add_material_start(callback: CallbackQuery, state: FSMContext):
    """Начать процесс добавления материала."""
    lang = await get_user_lang(callback.from_user.id)
    await state.set_state(MaterialStates.waiting_for_title)
    await callback.message.answer(get_message("material_enter_title", lang))
    await callback.answer()

@router.message(MaterialStates.waiting_for_title)
@handle_errors
async def process_material_title(message: Message, state: FSMContext):
    """Обработка названия материала."""
    lang = await get_user_lang(message.from_user.id)
    if not message.text or not message.text.strip():
        await message.answer(get_message("material_title_empty", lang))
        return
    await state.update_data(title=message.text.strip())
    await state.set_state(MaterialStates.waiting_for_description)
    await message.answer(get_message("material_enter_description", lang))

@router.message(MaterialStates.waiting_for_description)
@handle_errors
async def process_material_description(message: Message, state: FSMContext):
    """Обработка описания материала."""
    lang = await get_user_lang(message.from_user.id)
    if not message.text or not message.text.strip():
        await message.answer(get_message("material_description_empty", lang))
        return
    await state.update_data(description=message.text.strip())
    await state.set_state(MaterialStates.waiting_for_link)
    await message.answer(get_message("material_enter_link", lang))

@router.message(MaterialStates.waiting_for_link)
@handle_errors
async def process_material_link(message: Message, state: FSMContext):
    """Обработка ссылки на материал."""
    lang = await get_user_lang(message.from_user.id)
    await state.update_data(link=message.text)
    await state.set_state(MaterialStates.waiting_for_category)
    await message.answer(get_message("material_enter_category", lang))

@router.message(MaterialStates.waiting_for_category)
@handle_errors
async def process_material_category(message: Message, state: FSMContext):
    """Обработка категории материала."""
    lang = await get_user_lang(message.from_user.id)
    categories = {
        "1": get_message("material_category_1", lang),
        "2": get_message("material_category_2", lang),
        "3": get_message("material_category_3", lang),
        "4": get_message("material_category_4", lang),
        "5": get_message("material_category_5", lang)
    }
    
    if message.text not in categories:
        await message.answer(get_message("material_category_invalid", lang))
        return
    
    await state.update_data(category=categories[message.text])
    data = await state.get_data()
    
    # Форматируем информацию о материале
    material_info = format_material({
        'title': data['title'],
        'description': data['description'],
        'link': data['link'],
        'created_at': datetime.now().strftime("%d.%m.%Y")
    }, lang)
    
    await state.set_state(MaterialStates.waiting_for_confirmation)
    await message.answer(
        get_message("material_check_info", lang) + f"\n{material_info}\n" + get_message("material_confirm", lang)
    )

@router.message(MaterialStates.waiting_for_confirmation)
@handle_errors
async def process_material_confirmation(message: Message, state: FSMContext):
    """Обработка подтверждения создания материала."""
    lang = await get_user_lang(message.from_user.id)
    if message.text.lower() in ['да', 'yes', 'y', 'ооба']:
        data = await state.get_data()
        # Сохраняем материал в базу данных
        material_id = db.add_material(message.from_user.id, data)
        await message.answer(get_message("material_created", lang), reply_markup=get_materials_keyboard(lang))
    else:
        await message.answer(get_message("material_cancelled", lang), reply_markup=get_materials_keyboard(lang))
    await state.clear()

@router.callback_query(F.data == "my_materials")
@handle_errors
async def show_materials_list(callback: CallbackQuery):
    """Показать список материалов."""
    lang = await get_user_lang(callback.from_user.id)
    materials = db.get_user_materials(callback.from_user.id)
    
    if not materials:
        await callback.message.answer(get_message("material_none", lang))
    else:
        for material in materials:
            await callback.message.answer(format_material(material, lang))
    
    await callback.answer()

@router.callback_query(F.data == "search_materials")
@handle_errors
async def search_materials(callback: CallbackQuery, state: FSMContext):
    """Начать поиск материалов."""
    lang = await get_user_lang(callback.from_user.id)
    await state.set_state(MaterialStates.waiting_for_search)
    await callback.message.answer(get_message("material_enter_search", lang))
    await callback.answer()

def register_handlers(dispatcher):
    dispatcher.include_router(router) 