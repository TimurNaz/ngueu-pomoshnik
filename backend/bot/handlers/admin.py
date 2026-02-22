from aiogram import Router, types
from aiogram.types import CallbackQuery
from keyboards.client import get_client_back

router = Router()

@router.callback_query(lambda q: q.data == "admin_dashboard")
async def admin_dashboard(query: CallbackQuery):
    await query.message.answer_photo(
        photo="https://imgur.com/NSPLFOD",  # Заглушка-фото
        caption=(
            "🛠 <b>Панель администратора</b>\n\n"
            "🔍 Здесь будет функционал:\n"
            "• Просмотр и фильтрация заявок\n"
            "• Назначение исполнителей\n"
            "• Контроль выполнения\n"
            "• Статистика и отчёты\n\n"
            "⚠️ Пока в разработке, интеграция с backend будет позже."
        ),
        reply_markup=get_client_back(),
        parse_mode="HTML"
    )
    await query.answer()