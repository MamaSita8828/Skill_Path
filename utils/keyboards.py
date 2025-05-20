from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from utils.messages import BUTTONS

def get_main_keyboard(lang="ru") -> ReplyKeyboardMarkup:
    """Основная клавиатура."""
    b = BUTTONS[lang]
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=b["test"])],
            [KeyboardButton(text=b["stats"])],
            [KeyboardButton(text=b["portals"]), KeyboardButton(text=b["artifact_collection"] )],
            [KeyboardButton(text=b["profile"])],
            [KeyboardButton(text=b["change_language"])],
            [KeyboardButton(text=b["help"])]
        ],
        resize_keyboard=True
    )
    return keyboard

def get_goals_keyboard(lang="ru") -> InlineKeyboardMarkup:
    """Клавиатура для работы с целями."""
    b = BUTTONS[lang]
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="➕ Добавить цель", callback_data="add_goal")],
            [InlineKeyboardButton(text="📋 Список целей", callback_data="list_goals")],
            [InlineKeyboardButton(text="📈 Статистика", callback_data="goals_stats")],
            [InlineKeyboardButton(text=b["back"], callback_data="back_to_main")]
        ]
    )
    return keyboard

def get_progress_keyboard(lang="ru") -> InlineKeyboardMarkup:
    """Клавиатура для отслеживания прогресса."""
    b = BUTTONS[lang]
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📊 Общая статистика", callback_data="general_stats")],
            [InlineKeyboardButton(text="📅 По дням", callback_data="daily_stats")],
            [InlineKeyboardButton(text="📈 По неделям", callback_data="weekly_stats")],
            [InlineKeyboardButton(text=b["back"], callback_data="back_to_main")]
        ]
    )
    return keyboard

def get_materials_keyboard(lang="ru") -> InlineKeyboardMarkup:
    """Клавиатура для работы с материалами."""
    b = BUTTONS[lang]
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📚 Мои материалы", callback_data="my_materials")],
            [InlineKeyboardButton(text="🔍 Поиск", callback_data="search_materials")],
            [InlineKeyboardButton(text="➕ Добавить материал", callback_data="add_material")],
            [InlineKeyboardButton(text=b["back"], callback_data="back_to_main")]
        ]
    )
    return keyboard 