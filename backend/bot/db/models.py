"""
backend/bot/db/models.py
========================
Все модели БД проекта НГУЭУ/Помощник.

Таблицы:
  users               — пользователи (клиенты, исполнители, админы)
  executor_profiles   — профиль исполнителя (1:1 к users)
  orders              — заявки
  payments            — транзакции ЮKassa
  bonus_transactions  — история бонусной карты (начисления/списания)
  referrals           — реферальные связи
  reviews             — отзывы + NPS
  holiday_bonuses     — праздничный календарь начислений
  knowledge_base      — база преподавателей/требований
"""

import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    BigInteger, Boolean, Column, DateTime, Enum,
    Float, ForeignKey, Integer, Numeric, String, Text,
    UniqueConstraint, func,
)
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import relationship

from db.database import Base


# ──────────────────────────────────────────────────────────────
# ENUMS
# ──────────────────────────────────────────────────────────────

class UserRole(str, enum.Enum):
    client   = "client"
    executor = "executor"
    admin    = "admin"


class LoyaltyLevel(str, enum.Enum):
    """
    Уровень рассчитывается автоматически из total_spent:
      Новичок   : 0 ₽
      Студент   : 3 000 ₽
      Постоянный: 8 000 ₽
      VIP       : 15 000 ₽  → кэшбек 5%
    """
    novice   = "novice"
    student  = "student"
    regular  = "regular"
    vip      = "vip"


class OrderStatus(str, enum.Enum):
    new         = "new"          # только создана
    assigned    = "assigned"     # исполнитель назначен
    in_progress = "in_progress"  # взята в работу
    review      = "review"       # отправлена клиенту на проверку
    done        = "done"         # принята клиентом
    canceled    = "canceled"     # отменена


class PaymentStatus(str, enum.Enum):
    pending   = "pending"    # ожидает оплаты
    waiting   = "waiting"    # средства заморожены
    paid      = "paid"       # оплачено
    refunded  = "refunded"   # возврат
    canceled  = "canceled"   # отменён


class PaymentStage(str, enum.Enum):
    prepayment = "prepayment"  # 50% предоплата
    final      = "final"       # 50% после принятия


class BonusType(str, enum.Enum):
    registration       = "registration"       # +500 при регистрации
    purchase_cashback  = "purchase_cashback"  # % от суммы заказа
    referral           = "referral"           # +100 за друга
    holiday            = "holiday"            # праздничное начисление
    manual             = "manual"             # ручное начисление от админа
    spent              = "spent"              # списание при оплате заказа


class ReferralStatus(str, enum.Enum):
    pending   = "pending"    # зарегистрировался, но ещё не купил
    activated = "activated"  # совершил первую покупку → бонус выплачен


class HolidayTarget(str, enum.Enum):
    all       = "all"
    level_2   = "level_2"
    level_3   = "level_3"
    level_4   = "level_4"


# ──────────────────────────────────────────────────────────────
# КОНСТАНТЫ БИЗНЕС-ЛОГИКИ (меняются здесь → влияют везде)
# ──────────────────────────────────────────────────────────────

LOYALTY_THRESHOLDS = {
    LoyaltyLevel.novice:  0,
    LoyaltyLevel.student: 3_000,
    LoyaltyLevel.regular: 8_000,
    LoyaltyLevel.vip:     15_000,
}

CASHBACK_RATES = {
    LoyaltyLevel.novice:  0.00,
    LoyaltyLevel.student: 0.00,
    LoyaltyLevel.regular: 0.00,
    LoyaltyLevel.vip:     0.05,   # 5%
}

REGISTRATION_BONUS    = 500      # ₽ при первой регистрации
REFERRAL_BONUS        = 100      # ₽ за каждого купившего друга
COMMISSION_RATE       = 0.10     # 10% комиссия сервиса
MAX_BONUS_RATIO       = 0.50     # бонусами можно оплатить до 50% суммы


def calculate_loyalty_level(total_spent: float) -> LoyaltyLevel:
    """Рассчитать уровень лояльности по сумме покупок."""
    if total_spent >= LOYALTY_THRESHOLDS[LoyaltyLevel.vip]:
        return LoyaltyLevel.vip
    if total_spent >= LOYALTY_THRESHOLDS[LoyaltyLevel.regular]:
        return LoyaltyLevel.regular
    if total_spent >= LOYALTY_THRESHOLDS[LoyaltyLevel.student]:
        return LoyaltyLevel.student
    return LoyaltyLevel.novice


# ──────────────────────────────────────────────────────────────
# MODEL: users
# ──────────────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    # Идентификация
    id          = Column(BigInteger, primary_key=True)   # Telegram user_id
    username    = Column(String(64), nullable=True)       # @username (может быть None)
    first_name  = Column(String(128), nullable=True)
    last_name   = Column(String(128), nullable=True)
    role        = Column(Enum(UserRole), nullable=False, default=UserRole.client)
    is_active   = Column(Boolean, nullable=False, default=True)

    # Бонусная карта
    bonus_balance      = Column(Numeric(12, 2), nullable=False, default=0)
    total_spent        = Column(Numeric(12, 2), nullable=False, default=0)
    loyalty_level      = Column(
        Enum(LoyaltyLevel), nullable=False, default=LoyaltyLevel.novice
    )
    cashback_percent   = Column(Float, nullable=False, default=0.0)

    # Реферальная программа
    referral_code      = Column(String(16), unique=True, nullable=True)
    referred_by_id     = Column(BigInteger, ForeignKey("users.id"), nullable=True)
    referral_count     = Column(Integer, nullable=False, default=0)
    referral_bonus_total = Column(Numeric(12, 2), nullable=False, default=0)

    # Временны́е метки
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(),
                        onupdate=func.now(), nullable=False)

    # Relationships
    referred_by       = relationship("User", remote_side="User.id", foreign_keys=[referred_by_id])
    executor_profile  = relationship("ExecutorProfile", back_populates="user", uselist=False)
    orders_as_client  = relationship("Order", back_populates="client",
                                     foreign_keys="Order.client_id")
    orders_as_executor = relationship("Order", back_populates="executor",
                                      foreign_keys="Order.executor_id")
    bonus_transactions = relationship("BonusTransaction", back_populates="user")
    referrals_sent    = relationship("Referral", back_populates="referrer",
                                     foreign_keys="Referral.referrer_id")
    reviews           = relationship("Review", back_populates="client")

    def __repr__(self):
        return f"<User id={self.id} role={self.role} level={self.loyalty_level}>"


# ──────────────────────────────────────────────────────────────
# MODEL: executor_profiles
# ──────────────────────────────────────────────────────────────

class ExecutorProfile(Base):
    __tablename__ = "executor_profiles"

    id      = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), unique=True, nullable=False)

    specializations = Column(ARRAY(String), nullable=False, default=list)
    bio             = Column(Text, nullable=True)
    experience_years = Column(Integer, nullable=False, default=0)

    rating          = Column(Float, nullable=False, default=5.0)
    completed_count = Column(Integer, nullable=False, default=0)
    is_verified     = Column(Boolean, nullable=False, default=False)
    is_available    = Column(Boolean, nullable=False, default=True)

    bonus_balance   = Column(Numeric(12, 2), nullable=False, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(),
                        onupdate=func.now(), nullable=False)

    user = relationship("User", back_populates="executor_profile")

    def __repr__(self):
        return f"<ExecutorProfile user_id={self.user_id} rating={self.rating}>"


# ──────────────────────────────────────────────────────────────
# MODEL: orders
# ──────────────────────────────────────────────────────────────

class WorkType(str, enum.Enum):
    coursework = "coursework"
    diploma    = "diploma"
    abstract   = "abstract"
    lab        = "lab"
    practice   = "practice"
    other      = "other"


class UrgencyLevel(str, enum.Enum):
    three_days   = "3d"
    one_week     = "1w"
    two_weeks    = "2w"
    one_month    = "1m"


class Order(Base):
    __tablename__ = "orders"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    client_id   = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    executor_id = Column(BigInteger, ForeignKey("users.id"), nullable=True)

    # Данные заявки
    work_type          = Column(Enum(WorkType), nullable=False)
    subject            = Column(String(256), nullable=False)
    topic              = Column(String(512), nullable=False)
    teacher            = Column(String(256), nullable=True)
    requirements       = Column(Text, nullable=True)
    antiplagiat_percent = Column(Integer, nullable=True)   # 70/75/80/85 или None
    deadline           = Column(DateTime(timezone=True), nullable=True)
    urgency            = Column(Enum(UrgencyLevel), nullable=True)

    # Статус
    status = Column(Enum(OrderStatus), nullable=False, default=OrderStatus.new)
    step   = Column(Integer, nullable=False, default=0)   # 0..3 для прогресс-бара

    # Финансы
    price            = Column(Numeric(12, 2), nullable=True)   # назначается исполнителем
    commission_amount = Column(Numeric(12, 2), nullable=True)  # 10%
    executor_amount  = Column(Numeric(12, 2), nullable=True)   # цена - комиссия
    bonus_used       = Column(Numeric(12, 2), nullable=False, default=0)   # списано бонусов
    cashback_earned  = Column(Numeric(12, 2), nullable=False, default=0)   # начислено кэшбека

    # Временны́е метки
    created_at    = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    assigned_at   = Column(DateTime(timezone=True), nullable=True)
    completed_at  = Column(DateTime(timezone=True), nullable=True)
    updated_at    = Column(DateTime(timezone=True), server_default=func.now(),
                           onupdate=func.now(), nullable=False)

    # Relationships
    client   = relationship("User", back_populates="orders_as_client",
                            foreign_keys=[client_id])
    executor = relationship("User", back_populates="orders_as_executor",
                            foreign_keys=[executor_id])
    payments = relationship("Payment", back_populates="order")
    review   = relationship("Review", back_populates="order", uselist=False)

    def __repr__(self):
        return f"<Order id={self.id} status={self.status} price={self.price}>"


# ──────────────────────────────────────────────────────────────
# MODEL: payments
# ──────────────────────────────────────────────────────────────

class Payment(Base):
    __tablename__ = "payments"

    id      = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    user_id  = Column(BigInteger, ForeignKey("users.id"), nullable=False)

    amount              = Column(Numeric(12, 2), nullable=False)
    status              = Column(Enum(PaymentStatus), nullable=False, default=PaymentStatus.pending)
    stage               = Column(Enum(PaymentStage), nullable=False)

    yookassa_payment_id = Column(String(64), unique=True, nullable=True)
    prepayment_amount   = Column(Numeric(12, 2), nullable=True)
    final_payment_amount = Column(Numeric(12, 2), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    paid_at    = Column(DateTime(timezone=True), nullable=True)

    order = relationship("Order", back_populates="payments")
    user  = relationship("User")

    def __repr__(self):
        return f"<Payment id={self.id} amount={self.amount} status={self.status}>"


# ──────────────────────────────────────────────────────────────
# MODEL: bonus_transactions
# ──────────────────────────────────────────────────────────────

class BonusTransaction(Base):
    __tablename__ = "bonus_transactions"

    id      = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)

    # Положительное = начисление, отрицательное = списание
    amount          = Column(Numeric(12, 2), nullable=False)
    type            = Column(Enum(BonusType), nullable=False)
    description     = Column(String(512), nullable=False)
    related_order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user  = relationship("User", back_populates="bonus_transactions")
    order = relationship("Order")

    def __repr__(self):
        sign = "+" if self.amount >= 0 else ""
        return f"<BonusTransaction user={self.user_id} {sign}{self.amount} [{self.type}]>"


# ──────────────────────────────────────────────────────────────
# MODEL: referrals
# ──────────────────────────────────────────────────────────────

class Referral(Base):
    __tablename__ = "referrals"
    __table_args__ = (
        UniqueConstraint("referrer_id", "referred_id", name="uq_referral_pair"),
    )

    id          = Column(Integer, primary_key=True, autoincrement=True)
    referrer_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    referred_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)

    status       = Column(Enum(ReferralStatus), nullable=False, default=ReferralStatus.pending)
    bonus_paid   = Column(Boolean, nullable=False, default=False)
    bonus_paid_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    referrer = relationship("User", back_populates="referrals_sent",
                            foreign_keys=[referrer_id])
    referred = relationship("User", foreign_keys=[referred_id])

    def __repr__(self):
        return f"<Referral referrer={self.referrer_id} → referred={self.referred_id} [{self.status}]>"


# ──────────────────────────────────────────────────────────────
# MODEL: reviews
# ──────────────────────────────────────────────────────────────

class Review(Base):
    __tablename__ = "reviews"
    __table_args__ = (
        UniqueConstraint("order_id", name="uq_review_per_order"),
    )

    id        = Column(Integer, primary_key=True, autoincrement=True)
    order_id  = Column(Integer, ForeignKey("orders.id"), nullable=False)
    client_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)

    nps_score    = Column(Integer, nullable=False)   # 1..10
    comment      = Column(Text, nullable=True)
    is_published = Column(Boolean, nullable=False, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    order  = relationship("Order", back_populates="review")
    client = relationship("User", back_populates="reviews")

    def __repr__(self):
        return f"<Review order={self.order_id} nps={self.nps_score}>"


# ──────────────────────────────────────────────────────────────
# MODEL: holiday_bonuses
# ──────────────────────────────────────────────────────────────

class HolidayBonus(Base):
    __tablename__ = "holiday_bonuses"

    id           = Column(Integer, primary_key=True, autoincrement=True)
    name         = Column(String(256), nullable=False)    # "Новый год", "День студента"
    bonus_amount = Column(Numeric(12, 2), nullable=False)
    target       = Column(Enum(HolidayTarget), nullable=False, default=HolidayTarget.all)
    trigger_date = Column(DateTime(timezone=True), nullable=False)
    is_active    = Column(Boolean, nullable=False, default=True)
    is_sent      = Column(Boolean, nullable=False, default=False)  # уже отправлено?

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self):
        return f"<HolidayBonus '{self.name}' {self.bonus_amount}₽ → {self.target}>"


# ──────────────────────────────────────────────────────────────
# MODEL: knowledge_base
# ──────────────────────────────────────────────────────────────

class KnowledgeBase(Base):
    __tablename__ = "knowledge_base"

    id           = Column(Integer, primary_key=True, autoincrement=True)
    teacher_name = Column(String(256), nullable=False)
    department   = Column(String(256), nullable=True)
    requirements = Column(Text, nullable=True)
    formatting_notes = Column(Text, nullable=True)
    comments     = Column(Text, nullable=True)
    created_by   = Column(BigInteger, ForeignKey("users.id"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(),
                        onupdate=func.now(), nullable=False)

    author = relationship("User")

    def __repr__(self):
        return f"<KnowledgeBase teacher='{self.teacher_name}' dept='{self.department}'>"
