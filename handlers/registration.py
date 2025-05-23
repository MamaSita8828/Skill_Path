from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from utils.states import RegistrationStates
from utils.messages import get_message, normalize_lang, get_user_lang, BUTTONS
from utils.keyboards import get_main_keyboard
from database import UserManager
from handlers.test_utils import start_test_flow

router = Router()

LANG_INLINE_KB = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Русский", callback_data="lang_ru"),
         InlineKeyboardButton(text="Кыргызский", callback_data="lang_ky")]
    ]
)

GENDER_KB = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Мальчик"), KeyboardButton(text="Девочка")]],
    resize_keyboard=True
)

# Старт регистрации (например, по команде /register)
@router.message(F.text == "/register")
async def start_registration(message: Message, state: FSMContext):
    lang = await get_user_lang(message.from_user.id)
    await state.clear()
    await state.set_state(RegistrationStates.waiting_for_fio)
    await state.update_data(user_lang=lang)
    await message.answer(get_message("registration_fio", lang))

@router.message(RegistrationStates.waiting_for_fio)
async def reg_fio(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get('user_lang')
    if not lang:
        lang = await get_user_lang(message.from_user.id)
    lang = normalize_lang(lang)
    await state.update_data(fio=message.text.strip(), user_lang=lang)
    msg = get_message("registration_school", lang) or "Кайсы мектепте окуйсуң? (Мектептин атын толук жаз)\n\nСенин мектебиң — бул сенин экинчи үйүң. Ал жерден сен көп нерсеге үйрөнөсүң. Мектептин атын толук жазып койчу!"
    await message.answer(msg)
    await state.set_state(RegistrationStates.waiting_for_school)

@router.message(RegistrationStates.waiting_for_school)
async def reg_school(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get('user_lang')
    if not lang:
        lang = await get_user_lang(message.from_user.id)
    lang = normalize_lang(lang)
    await state.update_data(school=message.text.strip(), user_lang=lang)
    msg = get_message("registration_class", lang) or "Кайсы класста окуйсуң? (Мисалы: 8)\n\nАр бир класс — бул жаңы достор жана жаңы мүмкүнчүлүктөр. Кайсы класста окуйсуң? (Сан менен жазычы)"
    await message.answer(msg)
    await state.set_state(RegistrationStates.waiting_for_class_number)

@router.message(RegistrationStates.waiting_for_class_number)
async def reg_class_number(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get('user_lang')
    if not lang:
        lang = await get_user_lang(message.from_user.id)
    lang = normalize_lang(lang)
    if not message.text.isdigit():
        msg = get_message("registration_invalid_class", lang) or "Классты туура сан менен жазычы (мисалы: 8)"
        await message.answer(msg)
        return
    await state.update_data(class_number=int(message.text), user_lang=lang)
    msg = get_message("registration_letter", lang) or "Классыңдын тамгасын жаз (мисалы: А, Б, В...)\n\nАр бир тамга — бул сенин класстын өзгөчөлүгү!"
    await message.answer(msg)
    await state.set_state(RegistrationStates.waiting_for_class_letter)

@router.message(RegistrationStates.waiting_for_class_letter)
async def reg_class_letter(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get('user_lang')
    if not lang:
        lang = await get_user_lang(message.from_user.id)
    lang = normalize_lang(lang)
    await state.update_data(class_letter=message.text.strip(), user_lang=lang)
    b = BUTTONS[lang]
    gender_kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=b["boy"]), KeyboardButton(text=b["girl"])]] ,
        resize_keyboard=True
    )
    msg = get_message("registration_gender", lang) or "Жынысыңды танда:\nЭркекпи же кызбы?\n\nАр бир адам өзгөчө! Өзүңдү туура тааны!"
    await message.answer(msg, reply_markup=gender_kb)
    await state.set_state(RegistrationStates.waiting_for_gender)

@router.message(RegistrationStates.waiting_for_gender)
async def reg_gender(message: Message, state: FSMContext):
    gender = message.text.strip().lower()
    data = await state.get_data()
    lang = data.get('user_lang')
    if not lang:
        lang = await get_user_lang(message.from_user.id)
    lang = normalize_lang(lang)
    b = BUTTONS[lang]
    valid_genders = [b["boy"].lower(), b["girl"].lower(), "мальчик", "девочка", "эркек", "кыз"]
    if gender not in valid_genders:
        gender_kb = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text=b["boy"]), KeyboardButton(text=b["girl"])]] ,
            resize_keyboard=True
        )
        msg = get_message("registration_invalid_gender", lang) or "Туура жынысты тандачы: Эркек же Кыз"
        await message.answer(msg, reply_markup=gender_kb)
        return
    await state.update_data(gender=gender, user_lang=lang)
    msg = get_message("registration_birth_year", lang) or "Кайсы жылы төрөлгөнсүң? (Мисалы: 2008)\n\nАр бир жыл — жаңы мүмкүнчүлүктөр!"
    await message.answer(msg, reply_markup=get_main_keyboard(lang))
    await state.set_state(RegistrationStates.waiting_for_birth_year)

@router.message(RegistrationStates.waiting_for_birth_year)
async def reg_birth_year(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get('user_lang')
    if not lang:
        lang = await get_user_lang(message.from_user.id)
    lang = normalize_lang(lang)
    if not message.text.isdigit() or not (1900 < int(message.text) < 2025):
        msg = get_message("registration_invalid_year", lang) or "Туулган жылыңды туура форматта жазычы (мисалы: 2008)"
        await message.answer(msg)
        return
    await state.update_data(birth_year=int(message.text), user_lang=lang)
    msg = get_message("registration_city", lang) or "Кайсы шаарда же айылда жашайсың?\n\nАр бир шаар же айыл — бул сенин тарыхыңдын бир бөлүгү!"
    await message.answer(msg)
    await state.set_state(RegistrationStates.waiting_for_city)

@router.message(RegistrationStates.waiting_for_city)
async def reg_city(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get('user_lang')
    if not lang:
        lang = await get_user_lang(message.from_user.id)
    lang = normalize_lang(lang)
    await state.update_data(city=message.text.strip(), user_lang=lang)
    data = await state.get_data()
    data['telegram_id'] = message.from_user.id
    # Сохраняем пользователя в БД
    success = await UserManager.create_user(
        telegram_id=message.from_user.id,
        fio=data.get('fio', ''),
        school=data.get('school', ''),
        class_number=data.get('class_number', None),
        class_letter=data.get('class_letter', ''),
        gender=data.get('gender', ''),
        birth_year=data.get('birth_year', None),
        city=data.get('city', ''),
        language=lang
    )
    if success:
        msg = get_message("registration_done", lang) or get_message("registration_done", "ru")
                await message.answer(msg, reply_markup=None)
                await start_test_flow(message, state)
            else:
        msg = get_message("registration_error", lang) or get_message("registration_error", "ru")
                await message.answer(msg, reply_markup=None)
    await state.clear()

def register_registration_handlers(dispatcher):
    dispatcher.include_router(router) 