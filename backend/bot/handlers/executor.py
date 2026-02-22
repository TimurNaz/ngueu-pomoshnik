from aiogram import Router, types
from aiogram.types import CallbackQuery
from keyboards.client import get_client_back

router = Router()

@router.callback_query(lambda q: q.data == "executor_dashboard")
async def executor_dashboard(query: CallbackQuery):
    await query.message.answer_photo(
        photo="https://imgur.com/Mt6Vp9Y",  # Заглушка-картинка
        caption=(
            "👨‍💻 <b>Кабинет исполнителя</b>\n\n"
            "Здесь в будущем ты сможешь:\n"
            "• Получать доступ к заявкам\n"
            "• Отмечать выполнение\n"
            "• Отслеживать оплату\n\n"
            "⚠️ Пока что эта функция в разработке."
        ),
        reply_markup=get_client_back(),
        parse_mode="HTML"
    )
    await query.answer()