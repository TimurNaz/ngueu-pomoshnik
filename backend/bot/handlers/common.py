from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, StateFilter
from states.consent import ConsentState
from keyboards.client import get_consent_keyboard, get_start_keyboard
from services.user_service import get_or_create_user
from aiogram.types import CallbackQuery


router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
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
        parse_mode="HTML"  # Указываем HTML форматирование
    )
    await state.set_state(ConsentState.awaiting_consent)

@router.message(StateFilter(ConsentState.awaiting_consent), lambda m: m.text == "✅ Согласен")
async def process_consent(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    username = message.from_user.username

    await get_or_create_user(user_id=user_id, username=username)
    await message.answer("✅ Спасибо за согласие!", reply_markup=get_start_keyboard())
    await state.clear()

@router.message(StateFilter(ConsentState.awaiting_consent), lambda m: m.text == "❌ Не согласен")
async def process_decline(message: types.Message, state: FSMContext):
    await message.answer("Жаль, что ты не согласен. Если передумаешь — напиши /start снова.")
    await state.clear()

@router.callback_query(lambda q: q.data == "go_back")
async def go_back_handler(query: CallbackQuery):
    await query.message.delete()  # Удаляем последнее сообщение
    await query.answer()  # Отвечаем на callback, чтобы убрать "часики"