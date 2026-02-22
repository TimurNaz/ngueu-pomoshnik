from aiogram import Router, types
from aiogram.types import CallbackQuery
from keyboards.client import ( get_client_back, get_faq_menu, get_faq_questions, get_client_app_and_back, get_about_us_inline)
from keyboards.client import faq_data
# from db.redis import redis_client
import json

router = Router()

# Базовые хендлеры
@router.callback_query(lambda q: q.data == "Personal_account")
async def Personal_account(query: CallbackQuery):
    await query.message.answer_photo(  # Исправлено на answer_photo
        photo='https://storage.yandexcloud.net/ngueu-bot-images/Personal_account.png',
        caption="📥 Подача заявки доступна в MiniApp. Форма скоро будет активна!",  # Добавлен caption
        reply_markup=get_client_app_and_back()
    )
    await query.answer()

@router.callback_query(lambda q: q.data == "About_us")
async def About_us(query: CallbackQuery):
    await query.message.answer_photo(
        photo="https://storage.yandexcloud.net/ngueu-bot-images/About.png",
        caption=(
            "ℹ️ <b>О нас</b>\n\n"
            "Мы — <b>НГУЭУ Помощник</b>, сервис от студентов НГУЭУ.\n"
            "Помогаем с учёбой: курсовые, дипломы, рефераты. "
            "Всё удобно, быстро и прямо в Telegram.\n\n"
            "📲 Ознакомьтесь с нашими ресурсами ниже:"
        ),
        reply_markup=get_about_us_inline(),
        parse_mode="HTML"
    )
    await query.answer()


# @router.callback_query(lambda query: query.data == "Questions_and_answers")
# async def Questions_and_answers(query: CallbackQuery):
#     image_url = 'https://imgur.com/uMJwEby' 
#     faq_text = "Выбери тему: "
    
#     cached_markup = await redis_client.get("faq_menu_markup")
#     if cached_markup:
#         markup = json.loads(cached_markup)  # Но тут тоже надо аккуратно
#     else:
#         markup = get_faq_menu()
#         # Кэшировать безопаснее в виде сериализованной строки или просто скипнуть
#         # await redis_client.set("faq_menu_markup", json.dumps(markup), ex=3600)

#     await query.message.answer_photo(photo=image_url, caption=faq_text, reply_markup=markup, parse_mode="Markdown")
#     await query.answer()

# @router.callback_query(lambda query: query.data in ["faq_about", "faq_ordering", "faq_guarantees", "faq_legal", "faq_jobs", "faq_bonuses", "faq_referral", "faq_partners", "faq_feedback"])
# async def faq_topic(query: CallbackQuery):
#     topic = query.data
#     cache_key = f"faq_questions:{topic}"
#     cached = await redis_client.get(cache_key)
#     if cached:
#         keyboard = json.loads(cached)
#     else:
#         keyboard = get_faq_questions(topic)
#         await redis_client.set(cache_key, json.dumps(keyboard), ex=3600)

#     await query.message.answer("Выбери вопрос: ", reply_markup=keyboard)

# @router.callback_query(lambda query: query.data.startswith("faq_") and query.data.endswith(("_q1", "_q2", "_q3", "_q4", "_q5")))
# async def faq_answer(query: CallbackQuery):
#     question_key = query.data
#     cache_key = f"faq_answer:{question_key}"
    
#     cached = await redis_client.get(cache_key)
#     if cached:
#         response = cached
#     else:
#         topic = question_key.split('_q')[0]
#         question, answer = faq_data[topic][question_key]
#         response = f"❓ **{question}**\n\n{answer}"
#         await redis_client.set(cache_key, response, ex=3600)

#     await query.message.answer(response, reply_markup=get_client_back())
#     await query.answer()

@router.callback_query(lambda query: query.data == "Questions_and_answers")
async def Questions_and_answers(query: CallbackQuery):
    image_url = 'https://storage.yandexcloud.net/ngueu-bot-images/Questions_and_answers.png' 
    faq_text = "Выбери тему: "
    await query.message.answer_photo(photo=image_url, caption=faq_text, reply_markup=get_faq_menu(), parse_mode="Markdown")
    await query.answer()


@router.callback_query(lambda query: query.data in ["faq_about", "faq_ordering", "faq_guarantees", "faq_legal", "faq_jobs", "faq_bonuses", "faq_referral", "faq_partners", "faq_feedback"])
async def faq_topic(query: CallbackQuery):
    topic = query.data
    await query.message.answer("Выбери вопрос: ", reply_markup=get_faq_questions(topic))
    await query.answer()

@router.callback_query(lambda query: query.data.startswith("faq_") and query.data.endswith(("_q1", "_q2", "_q3", "_q4", "_q5")))
async def faq_answer(query: CallbackQuery):
    question_key = query.data
    topic = question_key.split('_q')[0]
    question, answer = faq_data[topic][question_key]
    response = f"❓ **{question}**\n\n{answer}"
    await query.message.answer(response, reply_markup=get_client_back())
    await query.answer()
    

@router.callback_query(lambda q: q.data == "Stages_of_work")
async def Stages_of_work(query: CallbackQuery):
    await query.message.answer_photo(
        photo="https://storage.yandexcloud.net/ngueu-bot-images/Stages_of_work.png",
        caption=(
            "⏳ <b>Этапы работы</b>\n\n"
            "1. Заявка — через форму\n"
            "2. Подбор исполнителя — вручную\n"
            "3. Выполнение — отслеживаешь статус\n"
            "4. Оплата — через ЮKassa после завершения"
        ),
        reply_markup=get_client_back(),
        parse_mode="HTML"
    )
    await query.answer()
    
@router.callback_query(lambda q: q.data == "An_hour_with_support")
async def An_hour_with_support(query: CallbackQuery):
    await query.message.answer_photo(
        photo="https://storage.yandexcloud.net/ngueu-bot-images/An_hour_with_support.png",
        caption=(
            "💬 <b>Чат с поддержкой</b>\n\n"
            "Задай вопрос — мы онлайн 24/7.\n"
            "AI-бот + живые операторы."
        ),
        reply_markup=get_client_back(),
        parse_mode="HTML"
    )
    await query.answer()

@router.callback_query(lambda q: q.data == "Reviews")
async def Reviews(query: CallbackQuery):
    await query.message.answer_photo(
        photo='https://storage.yandexcloud.net/ngueu-bot-images/Reviews.png',
        caption="⭐ <b>Отзывы</b>\n\nМы ценим мнение каждого студента...",
        reply_markup=get_client_back(),
        parse_mode="HTML"
    )
    await query.answer()
    
@router.callback_query(lambda q: q.data == "Become_a_performer")
async def Become_a_performer(query: CallbackQuery):
    await query.message.answer_photo(
        photo="https://storage.yandexcloud.net/ngueu-bot-images/Become_a_performer.png",
        caption=(
            "🤝 <b>Работай с нами</b>\n\n"
            "Мы ищем студентов-исполнителей. Условия: 2 курс+, знание стандартов НГУЭУ, ответственность.\n"
            "Доход от 500₽ за заказ. Напиши в поддержку!"
        ),
        reply_markup=get_client_back(),
        parse_mode="HTML"
    )
    await query.answer()