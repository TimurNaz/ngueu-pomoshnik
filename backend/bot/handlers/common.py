from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, StateFilter
from states.consent import ConsentState
from keyboards.client import get_consent_keyboard, get_start_keyboard
from services.user_service import get_or_create_user, get_user
from db.models import UserRole
from aiogram.types import CallbackQuery, InputMediaPhoto
import logging

logger = logging.getLogger(__name__)
router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    from config import ADMIN_IDS
    user_id = message.from_user.id
    user = await get_user(user_id)

    if user:
        # По умолчанию заходим в самый "высокий" доступный режим
        is_admin = user_id in ADMIN_IDS
        is_executor = user.role == UserRole.executor
        
        mode = "admin" if is_admin else ("executor" if is_executor else "client")
        
        await message.answer_photo(
            photo="https://storage.yandexcloud.net/ngueu-bot-images/Welcome.png",
            caption=(
                f"<b>🌟 С возвращением, {user.first_name or user.username or 'друг'}!</b>\n\n"
            ),
            reply_markup=get_start_keyboard(is_admin=is_admin, is_executor=is_executor, current_mode=mode),
            parse_mode="HTML"
        )
        return

    username = message.from_user.username or "друг"
    await message.answer_photo(
        photo="https://storage.yandexcloud.net/ngueu-bot-images/Welcome.png",
        caption=(
            f"<b>🌟 Добро пожаловать, {username}, в НГУЭУ Помощник!</b>\n\n"
            "Мы рады, что ты с нами! НГУЭУ Помощник — твой личный гид по учебе и процессам университета.\n\n"
            "Перед началом работы нам нужно твоё <b>согласие</b> на обработку данных. Мы гарантируем конфиденциальность.\n\n"
            "<b>✅ Подтверди согласие, чтобы продолжить.</b>"
        ),
        reply_markup=get_consent_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(ConsentState.awaiting_consent)

@router.message(StateFilter(ConsentState.awaiting_consent), F.text == "✅ Согласен")
async def process_consent(message: types.Message, state: FSMContext):
    try:
        from config import ADMIN_IDS
        user_id = message.from_user.id
        username = message.from_user.username or f"user_{user_id}"

        logger.info(f"Пользователь {user_id} нажал Согласен. Регистрируем...")
        user = await get_or_create_user(user_id=user_id, username=username)

        # Проверяем роли
        is_admin = user_id in ADMIN_IDS
        is_executor = user.role == UserRole.executor
        mode = "admin" if is_admin else ("executor" if is_executor else "client")

        await message.answer("✅ Спасибо за согласие!", reply_markup=types.ReplyKeyboardRemove())
        await message.answer(
            f"Воспользуйся меню ниже для навигации (режим: {mode.upper()}):", 
            reply_markup=get_start_keyboard(is_admin=is_admin, is_executor=is_executor, current_mode=mode)
        )
        await state.clear()
    except Exception as e:
        logger.error(f"Ошибка при регистрации пользователя {message.from_user.id}: {e}")
        await message.answer("❌ Произошла ошибка при регистрации. Попробуй позже или напиши в поддержку.")

@router.message(StateFilter(ConsentState.awaiting_consent), F.text == "❌ Не согласен")
async def process_decline(message: types.Message, state: FSMContext):
    await message.answer("Жаль, что ты не согласен. Если передумаешь — напиши /start снова.", reply_markup=types.ReplyKeyboardRemove())
    await state.clear()

@router.callback_query(F.data == "go_back")
async def go_back_handler(query: CallbackQuery):
    try:
        from config import ADMIN_IDS
        user_id = query.from_user.id
        user = await get_user(user_id)
        
        is_admin = user_id in ADMIN_IDS
        is_executor = user and user.role == UserRole.executor
        
        # Проверяем, не находился ли пользователь в режиме клиента (по тексту или кнопкам)
        # Если в сообщении был заголовок "Режим клиента", то возвращаемся именно в него
        current_caption = query.message.caption or ""
        force_client = "Режим клиента" in current_caption or "👤" in current_caption
        
        mode = "client" if force_client else ("admin" if is_admin else ("executor" if is_executor else "client"))

        # Формируем приветственный текст
        if mode == "client":
            caption = (
                f"<b>🌟 С возвращением, {user.first_name or user.username or 'друг'}!</b>\n\n"
                "Воспользуйтесь меню ниже для навигации:"
            )
        else:
            caption = f"<b>🏠 Главное меню ({mode.upper()})</b>\n\nВоспользуйтесь кнопками ниже:"

        await query.message.edit_media(
            media=InputMediaPhoto(
                media="https://storage.yandexcloud.net/ngueu-bot-images/Welcome.png",
                caption=caption,
                parse_mode="HTML"
            ),
            reply_markup=get_start_keyboard(is_admin=is_admin, is_executor=is_executor, current_mode=mode)
        )
    except Exception as e:
        logger.error(f"Ошибка в go_back_handler: {e}")
        await query.answer()
    await query.answer()

@router.callback_query(F.data == "switch_to_client")
async def switch_to_client(query: CallbackQuery):
    from config import ADMIN_IDS
    user_id = query.from_user.id
    user = await get_user(user_id)
    is_admin = user_id in ADMIN_IDS
    is_executor = user and user.role == UserRole.executor
    
    await query.message.edit_caption(
        caption="<b>👤 Режим клиента</b>\n\nВы переключились в пользовательский интерфейс:",
        reply_markup=get_start_keyboard(is_admin=is_admin, is_executor=is_executor, current_mode="client"),
        parse_mode="HTML"
    )
    await query.answer()

@router.callback_query(F.data == "switch_to_admin")
async def switch_to_admin(query: CallbackQuery):
    from config import ADMIN_IDS
    user_id = query.from_user.id
    user = await get_user(user_id)
    is_admin = user_id in ADMIN_IDS
    is_executor = user and user.role == UserRole.executor
    
    if not is_admin:
        await query.answer("❌ У вас нет прав администратора.", show_alert=True)
        return

    await query.message.edit_caption(
        caption="<b>🛠 Режим администратора</b>\n\nВы вернулись в панель управления:",
        reply_markup=get_start_keyboard(is_admin=is_admin, is_executor=is_executor, current_mode="admin"),
        parse_mode="HTML"
    )
    await query.answer()

@router.callback_query(F.data == "switch_to_executor")
async def switch_to_executor(query: CallbackQuery):
    from config import ADMIN_IDS
    user_id = query.from_user.id
    user = await get_user(user_id)
    is_admin = user_id in ADMIN_IDS
    is_executor = user and user.role == UserRole.executor
    
    if not is_executor:
        await query.answer("❌ У вас нет прав исполнителя.", show_alert=True)
        return

    await query.message.edit_caption(
        caption="<b>👨‍💻 Режим исполнителя</b>\n\nВы переключились в рабочий кабинет:",
        reply_markup=get_start_keyboard(is_admin=is_admin, is_executor=is_executor, current_mode="executor"),
        parse_mode="HTML"
    )
    await query.answer()

@router.callback_query(F.data.endswith("_stub"))
async def stub_handler(query: CallbackQuery):
    await query.answer("⚠️ Этот раздел сейчас находится в разработке.", show_alert=True)
