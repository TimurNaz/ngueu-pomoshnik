from aiogram import Router, types, F
from aiogram.types import CallbackQuery, InputMediaPhoto
from keyboards.client import ( get_client_back, get_faq_menu, get_faq_questions, get_client_app_and_back, get_about_us_inline)
from keyboards.client import faq_data
import logging

logger = logging.getLogger(__name__)
router = Router()

async def safe_edit_message(query: CallbackQuery, photo_url: str, caption: str, reply_markup):
    """Универсальный метод для чистого обновления сообщения с фото."""
    try:
        # Пытаемся обновить и фото, и текст
        await query.message.edit_media(
            media=InputMediaPhoto(media=photo_url, caption=caption, parse_mode="HTML"),
            reply_markup=reply_markup
        )
    except Exception as e:
        # Если фото уже то же самое или возникла ошибка - обновляем только текст и кнопки
        try:
            await query.message.edit_caption(caption=caption, reply_markup=reply_markup, parse_mode="HTML")
        except Exception:
            # Крайний случай: если всё упало, присылаем новое и удаляем старое
            await query.message.delete()
            await query.message.answer_photo(photo=photo_url, caption=caption, reply_markup=reply_markup, parse_mode="HTML")

# Базовые хендлеры
@router.callback_query(F.data == "Personal_account")
async def Personal_account(query: CallbackQuery):
    await safe_edit_message(
        query,
        photo_url='https://storage.yandexcloud.net/ngueu-bot-images/Personal_account.png',
        caption="📥 Подача заявки доступна в MiniApp. Форма скоро будет активна!",
        reply_markup=get_client_app_and_back()
    )
    await query.answer()

@router.callback_query(F.data == "About_us")
async def About_us(query: CallbackQuery):
    await safe_edit_message(
        query,
        photo_url="https://storage.yandexcloud.net/ngueu-bot-images/About.png",
        caption=(
            "ℹ️ <b>О нас</b>\n\n"
            "Мы — <b>НГУЭУ Помощник</b>, сервис от студентов НГУЭУ.\n"
            "Помогаем с учёбой: курсовые, дипломы, рефераты. "
            "Всё удобно, быстро и прямо в Telegram.\n\n"
            "📲 Ознакомьтесь с нашими ресурсами ниже:"
        ),
        reply_markup=get_about_us_inline()
    )
    await query.answer()

@router.callback_query(F.data == "Questions_and_answers")
async def Questions_and_answers(query: CallbackQuery):
    await safe_edit_message(
        query,
        photo_url='https://storage.yandexcloud.net/ngueu-bot-images/Questions_and_answers.png',
        caption="❓ <b>Часто задаваемые вопросы</b>\n\nВыберите интересующую вас тему ниже:",
        reply_markup=get_faq_menu()
    )
    await query.answer()

@router.callback_query(F.data.in_(["faq_about", "faq_ordering", "faq_guarantees", "faq_legal", "faq_jobs", "faq_bonuses", "faq_referral", "faq_partners", "faq_feedback"]))
async def faq_topic(query: CallbackQuery):
    topic = query.data
    await query.message.edit_caption(
        caption="🔍 <b>Выберите вопрос:</b>", 
        reply_markup=get_faq_questions(topic),
        parse_mode="HTML"
    )
    await query.answer()

@router.callback_query(F.data.startswith("faq_") and F.data.endswith(("_q1", "_q2", "_q3", "_q4", "_q5")))
async def faq_answer(query: CallbackQuery):
    question_key = query.data
    topic = question_key.split('_q')[0]
    question, answer = faq_data[topic][question_key]
    response = f"❓ <b>{question}</b>\n\n{answer}"

    await query.message.edit_caption(caption=response, reply_markup=get_client_back(), parse_mode="HTML")
    await query.answer()

@router.callback_query(F.data == "Stages_of_work")
async def Stages_of_work(query: CallbackQuery):
    await safe_edit_message(
        query,
        photo_url="https://storage.yandexcloud.net/ngueu-bot-images/Stages_of_work.png",
        caption=(
            "⏳ <b>Этапы работы</b>\n\n"
            "1. Заявка — через форму\n"
            "2. Подбор исполнителя — вручную\n"
            "3. Выполнение — отслеживаешь статус\n"
            "4. Оплата — через ЮKassa после завершения"
        ),
        reply_markup=get_client_back()
    )
    await query.answer()

@router.callback_query(F.data == "An_hour_with_support")
async def An_hour_with_support(query: CallbackQuery):
    await safe_edit_message(
        query,
        photo_url="https://storage.yandexcloud.net/ngueu-bot-images/An_hour_with_support.png",
        caption=(
            "💬 <b>Чат с поддержкой</b>\n\n"
            "Задай вопрос — мы онлайн 24/7.\n"
            "AI-бот + живые операторы."
        ),
        reply_markup=get_client_back()
    )
    await query.answer()

@router.callback_query(F.data == "Reviews")
async def Reviews(query: CallbackQuery):
    await safe_edit_message(
        query,
        photo_url='https://storage.yandexcloud.net/ngueu-bot-images/Reviews.png',
        caption="⭐ <b>Отзывы</b>\n\nМы ценим мнение каждого студента. Ознакомиться с отзывами можно в нашем канале.",
        reply_markup=get_client_back()
    )
    await query.answer()

@router.callback_query(F.data == "Become_a_performer")
async def Become_a_performer(query: CallbackQuery):
    await safe_edit_message(
        query,
        photo_url="https://storage.yandexcloud.net/ngueu-bot-images/Become_a_performer.png",
        caption=(
            "🤝 <b>Работай с нами</b>\n\n"
            "Мы ищем студентов-исполнителей. Условия: 2 курс+, знание стандартов НГУЭУ, ответственность.\n"
            "Доход от 500₽ за заказ. Напиши в поддержку!"
        ),
        reply_markup=get_client_back()
    )
    await query.answer()