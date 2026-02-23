from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import WebAppInfo

from config import MINIAPP_URL
from keyboards.faq_data import faq_data

def get_consent_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ Согласен")],
            [KeyboardButton(text="❌ Не согласен")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def get_start_keyboard():
    return InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Личный кабинет", callback_data="Personal_account")],
        [InlineKeyboardButton(text="О нас", callback_data="About_us")],
        [InlineKeyboardButton(text="Этапы работы", callback_data="Stages_of_work")],
        [InlineKeyboardButton(text="FAQ", callback_data="Questions_and_answers")],
        [InlineKeyboardButton(text="💬 Час с поддержкой", callback_data="An_hour_with_support")],
        [InlineKeyboardButton(text="Отзывы", callback_data="Reviews")],
        [InlineKeyboardButton(text="Стать исполнителя", callback_data="Become_a_performer")]
    ]
)

def get_faq_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📘 О сервисе", callback_data="faq_about")],
        [InlineKeyboardButton(text="💼 Заказ и выполнение услуг", callback_data="faq_ordering")],
        [InlineKeyboardButton(text="🛡️ Гарантии и безопасность", callback_data="faq_guarantees")],
        [InlineKeyboardButton(text="📜 Юридическая информация", callback_data="faq_legal")],
        [InlineKeyboardButton(text="🧑‍💼 Сотрудничество и трудоустройство", callback_data="faq_jobs")],
        [InlineKeyboardButton(text="🎁 Бонусная система и акции", callback_data="faq_bonuses")],
        [InlineKeyboardButton(text="🤝 Партнёрская программа", callback_data="faq_referral")],
        [InlineKeyboardButton(text="🛍️ Скидки и партнёры", callback_data="faq_partners")],
        [InlineKeyboardButton(text="💬 Обратная связь и идеи", callback_data="faq_feedback")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="go_back")]
    ])

def get_faq_questions(topic):
    questions = {
        "faq_about": [
            ("Что за платформа?", "faq_about_q1"),
            ("Где работает сервис?", "faq_about_q2"),
            ("Кому полезен сервис?", "faq_about_q3"),
        ],
        "faq_ordering": [
            ("Как оформить заказ?", "faq_ordering_q1"),
            ("Кто выполняет заказы?", "faq_ordering_q2"),
            ("Как получить результат?", "faq_ordering_q3"),
            ("Что если результат не устроит?", "faq_ordering_q4"),
        ],
        "faq_guarantees": [
            ("Есть ли гарантия качества?", "faq_guarantees_q1"),
            ("Что если исполнитель подвёл?", "faq_guarantees_q2"),
            ("Как защищены мои данные?", "faq_guarantees_q3"),
        ],
        "faq_legal": [
            ("Что за оферта?", "faq_legal_q1"),
            ("Ваши услуги законны?", "faq_legal_q2"),
            ("Какие ограничения?", "faq_legal_q3"),
        ],
        "faq_jobs": [
            ("Как попасть в команду?", "faq_jobs_q1"),
            ("Есть ли вакансии?", "faq_jobs_q2"),
            ("Можно работать удалённо?", "faq_jobs_q3"),
        ],
        "faq_bonuses": [
            ("Как начисляются бонусы?", "faq_bonuses_q1"),
            ("Где использовать бонусы?", "faq_bonuses_q2"),
            ("Как участвовать в акциях?", "faq_bonuses_q3"),
        ],
        "faq_referral": [
            ("Как пригласить друга?", "faq_referral_q1"),
            ("Что получу за приглашение?", "faq_referral_q2"),
            ("Где смотреть статистику?", "faq_referral_q3"),
        ],
        "faq_partners": [
            ("Кто ваши партнёры?", "faq_partners_q1"),
            ("Как получить скидку?", "faq_partners_q2"),
            ("Где взять промокод?", "faq_partners_q3"),
        ],
        "faq_feedback": [
            ("Как предложить идею?", "faq_feedback_q1"),
            ("Где оставить отзыв?", "faq_feedback_q2"),
            ("Как связаться с поддержкой?", "faq_feedback_q3"),
        ]
    }
    if topic in questions:
        get_faq_menu = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=text, callback_data=callback)] for text, callback in questions[topic]
        ] + [[InlineKeyboardButton(text="⬅️ Назад", callback_data="go_back")]])
        return get_faq_menu
    return None

def get_client_back():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад", callback_data="go_back")]
        ]
    )

def get_client_app_and_back():
    url = _miniapp_url()
    if url:
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Открыть приложение", web_app=WebAppInfo(url=url))],
            [InlineKeyboardButton(text="🔙 Назад", callback_data="go_back")]
        ])
    return get_client_back()


def _miniapp_url():
    """Чистый HTTPS URL для MiniApp (без лишнего текста из ngrok)."""
    raw = (MINIAPP_URL or "").strip().split()[0] if (MINIAPP_URL or "").strip() else ""
    return raw if raw.startswith("https://") else ""


def get_about_us_inline():
    rows = []
    app_url = _miniapp_url()
    if app_url:
        rows.append([InlineKeyboardButton(text="🌐 Открыть приложение", web_app=WebAppInfo(url=app_url))])
    rows.extend([
        [InlineKeyboardButton(text="📸 Instagram", url="https://instagram.com/yourpage")],
        [InlineKeyboardButton(text="💬 Отзывы", url="https://t.me/your_feedback_channel")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="go_back")],
    ])
    return InlineKeyboardMarkup(inline_keyboard=rows)