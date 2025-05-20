from aiogram.fsm.state import State, StatesGroup

class GoalStates(StatesGroup):
    """Состояния для работы с целями."""
    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_deadline = State()
    waiting_for_priority = State()
    waiting_for_confirmation = State()

class MaterialStates(StatesGroup):
    """Состояния для работы с материалами."""
    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_link = State()
    waiting_for_category = State()
    waiting_for_confirmation = State()

class NoteStates(StatesGroup):
    """Состояния для работы с заметками."""
    waiting_for_title = State()
    waiting_for_content = State()
    waiting_for_tags = State()
    waiting_for_confirmation = State()

class ProfileStates(StatesGroup):
    """Состояния для работы с профилем."""
    waiting_for_name = State()
    waiting_for_bio = State()
    waiting_for_goals = State()
    waiting_for_interests = State()

class SettingsStates(StatesGroup):
    """Состояния для работы с настройками."""
    waiting_for_notification_time = State()
    waiting_for_language = State()
    waiting_for_theme = State()
    waiting_for_confirmation = State()

class TestStates(StatesGroup):
    """Состояния для теста по сценам."""
    main_scene = State()         # Основные 7 сцен
    personal_scene = State()     # Персональные 8 сцен
    finish = State()            # Завершение теста

class RegistrationStates(StatesGroup):
    """Состояния для креативной регистрации пользователя."""
    waiting_for_fio = State()
    waiting_for_school = State()
    waiting_for_class_number = State()
    waiting_for_class_letter = State()
    waiting_for_gender = State()
    waiting_for_birth_year = State()
    waiting_for_city = State() 