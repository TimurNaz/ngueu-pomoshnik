from decimal import Decimal
from aiogram import Router, types, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from keyboards.client import get_client_back
from services.db_service import OrderService, UserService
from services.payment_service import PaymentService
from db.models import OrderStatus
import logging

logger = logging.getLogger(__name__)
router = Router()

@router.callback_query(F.data == "executor_dashboard")
async def executor_dashboard(query: CallbackQuery):
    """Главный экран кабинета исполнителя."""
    try:
        orders = await OrderService.get_executor_orders(query.from_user.id)

        text = (
            "👨‍💻 <b>Кабинет исполнителя</b>\n\n"
            f"У вас активных заказов: <b>{len(orders)}</b>\n"
            "Используйте кнопки ниже для управления."
        )

        keyboard_btns = []
        for order in orders:
            status_emoji = "⏳" if order.status == OrderStatus.assigned else "🛠"
            keyboard_btns.append([InlineKeyboardButton(
                text=f"{status_emoji} Заказ #{order.id}: {order.subject}",
                callback_data=f"exec_order_{order.id}"
            )])

        keyboard_btns.append([InlineKeyboardButton(text="🔙 Назад", callback_data="go_back")])
        markup = InlineKeyboardMarkup(inline_keyboard=keyboard_btns)

        try:
            await query.message.edit_media(
                media=InputMediaPhoto(
                    media="https://storage.yandexcloud.net/ngueu-bot-images/Become_a_performer.png",
                    caption=text,
                    parse_mode="HTML"
                ),
                reply_markup=markup
            )
        except Exception:
            await query.message.edit_caption(caption=text, reply_markup=markup, parse_mode="HTML")
        await query.answer()
    except Exception as e:
        logger.error(f"Ошибка в дашборде исполнителя: {e}")
        await query.answer("Ошибка при загрузке кабинета.")

@router.callback_query(F.data.startswith("exec_order_"))
async def show_executor_order_detail(query: CallbackQuery):
    """Детальный просмотр заказа исполнителем."""
    order_id = int(query.data.split("_")[-1])
    order = await OrderService.get_by_id(order_id)

    if not order:
        await query.answer("Заказ не найден.")
        return

    text = (
        f"📋 <b>Управление заказом #{order.id}</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📚 <b>Предмет:</b> {order.subject}\n"
        f"📝 <b>Тема:</b> {order.topic}\n"
        f"🚦 <b>Статус:</b> <i>{order.status.value}</i>\n"
        f"📅 <b>Дедлайн:</b> {order.deadline.strftime('%d.%m.%Y %H:%M') if order.deadline else 'Не указан'}\n"
        f"━━━━━━━━━━━━━━━━━━"
    )

    btns = []
    if order.status == OrderStatus.assigned:
        btns.append([InlineKeyboardButton(text="💰 Назначить цену", callback_data=f"exec_set_price_{order.id}")])
        btns.append([InlineKeyboardButton(text="✅ Принять в работу", callback_data=f"exec_accept_{order.id}")])
    elif order.status == OrderStatus.in_progress:
        btns.append([InlineKeyboardButton(text="📤 Сдать работу", callback_data=f"exec_submit_{order.id}")])

    btns.append([InlineKeyboardButton(text="🔙 К списку заказов", callback_data="executor_dashboard")])
    markup = InlineKeyboardMarkup(inline_keyboard=btns)

    await query.message.edit_caption(caption=text, reply_markup=markup, parse_mode="HTML")
    await query.answer()

@router.callback_query(F.data.startswith("exec_accept_"))
async def process_executor_accept(query: CallbackQuery):
    """Исполнитель принимает заказ."""
    order_id = int(query.data.split("_")[-1])
    success = await OrderService.update_status(order_id, OrderStatus.in_progress)

    if success:
        order = await OrderService.get_by_id(order_id)
        executor = query.from_user
        
        # Уведомляем КЛИЕНТА (Критично)
        try:
            await query.bot.send_message(
                chat_id=order.client_id,
                text=(
                    f"🚀 <b>Исполнитель приступил к выполнению вашей заявки #{order.id}!</b>\n\n"
                    f"📚 Предмет: {order.subject}\n"
                    f"👤 Исполнитель: {executor.first_name or executor.username}"
                ),
                parse_mode="HTML"
            )
        except Exception as e:
            logger.error(f"Не удалось уведомить клиента об отклике: {e}")

        # Уведомляем АДМИНОВ (Критично)
        from config import ADMIN_IDS
        admin_msg = (
            f"⚡️ <b>Исполнитель подтвердил заказ #{order.id}</b>\n\n"
            f"👨‍💻 Исполнитель: @{executor.username or executor.id}\n"
            f"📚 Предмет: {order.subject}"
        )
        for admin_id in ADMIN_IDS:
            try:
                await query.bot.send_message(admin_id, admin_msg, parse_mode="HTML")
            except: pass

        await query.answer("Заказ принят в работу!", show_alert=True)
        await show_executor_order_detail(query)
    else:
        await query.answer("Ошибка.")

@router.callback_query(F.data.startswith("exec_submit_"))
async def process_executor_submit_start(query: CallbackQuery, state: FSMContext):
    """Начало процесса сдачи работы (ожидание файла)."""
    order_id = int(query.data.split("_")[-1])
    
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отмена и назад", callback_data=f"exec_order_{order_id}")]
    ])
    
    await query.message.edit_caption(
        caption=(
            f"📎 <b>Загрузка результата для заказа #{order_id}</b>\n\n"
            "Пожалуйста, отправьте файл (документ) с готовой работой.\n\n"
            "<i>Если передумали — нажмите кнопку ниже.</i>"
        ),
        reply_markup=markup,
        parse_mode="HTML"
    )
    await state.update_data(submitting_order_id=order_id)
    await state.set_state("waiting_executor_file")
    await query.answer()

@router.message(F.document, StateFilter("waiting_executor_file"))
async def handle_executor_file(message: Message, state: FSMContext):
    """Прием файла от исполнителя и перевод заказа в review."""
    data = await state.get_data()
    order_id = data.get("submitting_order_id")

    if not order_id:
        await message.answer("Ошибка: заказ не найден.")
        await state.clear()
        return

    success = await OrderService.update_status(order_id, OrderStatus.review)

    if success:
        order = await OrderService.get_by_id(order_id)
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🏠 В кабинет исполнителя", callback_data="executor_dashboard")]
        ])
        await message.answer(
            f"✅ <b>Заказ #{order_id} отправлен на проверку админу!</b>", 
            reply_markup=markup,
            parse_mode="HTML"
        )

        # Уведомляем АДМИНОВ (Критично)
        from config import ADMIN_IDS
        admin_notif = (
            f"👀 <b>Заказ #{order_id} сдан на проверку!</b>\n\n"
            f"📚 Предмет: {order.subject}\n"
            f"👨‍💻 Исполнитель: @{message.from_user.username or message.from_user.id}\n\n"
            f"Проверьте работу в админ-панели."
        )
        for admin_id in ADMIN_IDS:
            try:
                await message.bot.send_message(admin_id, admin_notif, parse_mode="HTML")
            except: pass

        await state.clear()
    else:
        await message.answer("❌ Ошибка при сохранении.")


# ── Назначение цены ───────────────────────────────────────────

@router.callback_query(F.data.startswith("exec_set_price_"))
async def start_set_price(query: CallbackQuery, state: FSMContext):
    """Начало процесса назначения цены."""
    order_id = int(query.data.split("_")[-1])

    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отмена", callback_data=f"exec_order_{order_id}")]
    ])

    await query.message.edit_caption(
        caption=(
            f"💰 <b>Назначение цены для заказа #{order_id}</b>\n\n"
            "Введите стоимость работы в рублях (только число).\n"
            "Например: <code>5000</code>\n\n"
            f"Комиссия платформы: 10%\n"
            "<i>Если передумали — нажмите кнопку ниже.</i>"
        ),
        reply_markup=markup,
        parse_mode="HTML"
    )
    await state.update_data(pricing_order_id=order_id)
    await state.set_state("waiting_price_input")
    await query.answer()


@router.message(F.text, StateFilter("waiting_price_input"))
async def handle_price_input(message: Message, state: FSMContext):
    """Приём введённой цены от исполнителя."""
    data = await state.get_data()
    order_id = data.get("pricing_order_id")

    if not order_id:
        await message.answer("Ошибка: заказ не найден.")
        await state.clear()
        return

    # Валидация ввода
    price_text = message.text.strip().replace(" ", "").replace(",", ".")
    try:
        price = Decimal(price_text)
        if price <= 0:
            raise ValueError
    except (ValueError, Exception):
        await message.answer(
            "❌ Некорректная сумма. Введите положительное число, например: <code>5000</code>",
            parse_mode="HTML"
        )
        return

    try:
        order = await PaymentService.set_price(order_id, price)

        commission = float(order.commission_amount or 0)
        executor_amount = float(order.executor_amount or 0)

        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🏠 В кабинет исполнителя", callback_data="executor_dashboard")]
        ])
        await message.answer(
            f"✅ <b>Цена заказа #{order_id} установлена!</b>\n\n"
            f"💰 Стоимость: {float(price):.0f} ₽\n"
            f"📊 Комиссия платформы: {commission:.0f} ₽\n"
            f"💵 Ваш доход: {executor_amount:.0f} ₽\n\n"
            f"Клиент получил уведомление об оплате.",
            reply_markup=markup,
            parse_mode="HTML"
        )
        await state.clear()
    except ValueError as e:
        await message.answer(f"❌ {str(e)}")
        await state.clear()
    except Exception as e:
        logger.error(f"Ошибка назначения цены: {e}")
        await message.answer("❌ Произошла ошибка. Попробуйте позже.")
        await state.clear()
