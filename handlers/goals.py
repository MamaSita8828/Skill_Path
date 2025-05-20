from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from datetime import datetime

from utils.states import GoalStates
from utils.messages import format_goal, format_progress, get_message, get_user_lang
from utils.keyboards import get_goals_keyboard
from utils.error_handler import handle_errors
from utils.database import db

router = Router()

@router.callback_query(F.data == "add_goal")
@handle_errors
async def add_goal_start(callback: CallbackQuery, state: FSMContext):
    """Начать процесс добавления цели."""
    lang = await get_user_lang(callback.from_user.id)
    await state.set_state(GoalStates.waiting_for_title)
    await callback.message.answer(get_message("goal_enter_title", lang))
    await callback.answer()

@router.message(GoalStates.waiting_for_title)
@handle_errors
async def process_goal_title(message: Message, state: FSMContext):
    """Обработка названия цели."""
    lang = await get_user_lang(message.from_user.id)
    if not message.text or not message.text.strip():
        await message.answer(get_message("goal_title_empty", lang))
        return
    await state.update_data(title=message.text.strip())
    await state.set_state(GoalStates.waiting_for_description)
    await message.answer(get_message("goal_enter_description", lang))

@router.message(GoalStates.waiting_for_description)
@handle_errors
async def process_goal_description(message: Message, state: FSMContext):
    """Обработка описания цели."""
    lang = await get_user_lang(message.from_user.id)
    if not message.text or not message.text.strip():
        await message.answer(get_message("goal_description_empty", lang))
        return
    await state.update_data(description=message.text.strip())
    await state.set_state(GoalStates.waiting_for_deadline)
    await message.answer(get_message("goal_enter_deadline", lang))

@router.message(GoalStates.waiting_for_deadline)
@handle_errors
async def process_goal_deadline(message: Message, state: FSMContext):
    """Обработка срока цели."""
    lang = await get_user_lang(message.from_user.id)
    try:
        deadline = datetime.strptime(message.text, "%d.%m.%Y")
        if deadline < datetime.now():
            await message.answer(get_message("goal_deadline_past", lang))
            return
    except ValueError:
        await message.answer(get_message("goal_deadline_invalid", lang))
        return

    await state.update_data(deadline=deadline.strftime("%d.%m.%Y"))
    await state.set_state(GoalStates.waiting_for_priority)
    await message.answer(get_message("goal_enter_priority", lang))

@router.message(GoalStates.waiting_for_priority)
@handle_errors
async def process_goal_priority(message: Message, state: FSMContext):
    """Обработка приоритета цели."""
    lang = await get_user_lang(message.from_user.id)
    try:
        priority = int(message.text)
        if not 1 <= priority <= 5:
            raise ValueError
    except ValueError:
        await message.answer(get_message("goal_priority_invalid", lang))
        return

    await state.update_data(priority=priority)
    data = await state.get_data()
    
    # Форматируем информацию о цели
    goal_info = format_goal({
        'title': data['title'],
        'description': data['description'],
        'deadline': data['deadline'],
        'priority': data['priority'],
        'progress': 0
    }, lang)
    
    await state.set_state(GoalStates.waiting_for_confirmation)
    await message.answer(
        get_message("goal_check_info", lang) + f"\n{goal_info}\n" + get_message("goal_confirm", lang)
    )

@router.message(GoalStates.waiting_for_confirmation)
@handle_errors
async def process_goal_confirmation(message: Message, state: FSMContext):
    """Обработка подтверждения создания цели."""
    lang = await get_user_lang(message.from_user.id)
    if message.text.lower() in ['да', 'yes', 'y', 'ооба']:
        data = await state.get_data()
        # Сохраняем цель в базу данных
        goal_id = db.add_goal(message.from_user.id, data)
        await message.answer(get_message("goal_created", lang), reply_markup=get_goals_keyboard(lang))
    else:
        await message.answer(get_message("goal_cancelled", lang), reply_markup=get_goals_keyboard(lang))
    await state.clear()

@router.callback_query(F.data == "list_goals")
@handle_errors
async def show_goals_list(callback: CallbackQuery):
    """Показать список целей."""
    lang = await get_user_lang(callback.from_user.id)
    goals = db.get_user_goals(callback.from_user.id)
    
    if not goals:
        await callback.message.answer(get_message("goal_none", lang))
    else:
        for goal in goals:
            await callback.message.answer(format_goal(goal, lang))
    
    await callback.answer()

@router.callback_query(F.data == "goals_stats")
@handle_errors
async def show_goals_stats(callback: CallbackQuery):
    """Показать статистику по целям."""
    lang = await get_user_lang(callback.from_user.id)
    stats = db.get_goal_stats(callback.from_user.id)
    await callback.message.answer(format_progress(stats, lang))
    await callback.answer()

def register_handlers(dispatcher):
    dispatcher.include_router(router) 