"""
backend/bot/db/models.py
========================
Все модели БД проекта НГУЭУ/Помощник.
"""

import enum
from datetime import datetime
from sqlalchemy import (
    BigInteger, Boolean, Column, DateTime, Enum,
    Float, ForeignKey, Integer, Numeric, String, Text,
    UniqueConstraint, func,
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship
from db.database import Base

# ── ENUMS ──────────────────────────────────────────────

class UserRole(str, enum.Enum):
    client   = "client"
    executor = "executor"
    admin    = "admin"

class LoyaltyLevel(str, enum.Enum):
    novice   = "novice"
    student  = "student"
    regular  = "regular"
    vip      = "vip"

class OrderStatus(str, enum.Enum):
    new         = "new"
    assigned    = "assigned"
    in_progress = "in_progress"
    review      = "review"
    done        = "done"
    canceled    = "canceled"

class PaymentStatus(str, enum.Enum):
    pending   = "pending"
    waiting   = "waiting"
    paid      = "paid"
    refunded  = "refunded"
    canceled  = "canceled"

class PaymentStage(str, enum.Enum):
    prepayment = "prepayment"
    final      = "final"

class BonusType(str, enum.Enum):
    registration       = "registration"
    purchase_cashback  = "purchase_cashback"
    referral           = "referral"
    holiday            = "holiday"
    manual             = "manual"
    spent              = "spent"

class ReferralStatus(str, enum.Enum):
    pending   = "pending"
    activated = "activated"

class HolidayTarget(str, enum.Enum):
    all       = "all"
    level_2   = "level_2"
    level_3   = "level_3"
    level_4   = "level_4"

class WorkType(str, enum.Enum):
    coursework = "coursework"
    diploma    = "diploma"
    abstract   = "abstract"
    lab        = "lab"
    practice   = "practice"
    other      = "other"

# ПЕРЕХОДИМ НА ПОЛНЫЕ НАЗВАНИЯ ДЛЯ СТАБИЛЬНОСТИ
class UrgencyLevel(str, enum.Enum):
    three_days = "three_days"
    one_week   = "one_week"
    two_weeks  = "two_weeks"
    one_month  = "one_month"

# ── БИЗНЕС-ЛОГИКА ──────────────────────────────────────────

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
    LoyaltyLevel.vip:     0.05,
}

REGISTRATION_BONUS    = 500
REFERRAL_BONUS        = 100
COMMISSION_RATE       = 0.10
MAX_BONUS_RATIO       = 0.50

def calculate_loyalty_level(total_spent: float) -> LoyaltyLevel:
    if total_spent >= LOYALTY_THRESHOLDS[LoyaltyLevel.vip]:
        return LoyaltyLevel.vip
    if total_spent >= LOYALTY_THRESHOLDS[LoyaltyLevel.regular]:
        return LoyaltyLevel.regular
    if total_spent >= LOYALTY_THRESHOLDS[LoyaltyLevel.student]:
        return LoyaltyLevel.student
    return LoyaltyLevel.novice

# ── MODELS ──────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"
    id          = Column(BigInteger, primary_key=True)
    username    = Column(String(64), nullable=True)
    first_name  = Column(String(128), nullable=True)
    last_name   = Column(String(128), nullable=True)
    role        = Column(Enum(UserRole, name="userrole"), nullable=False, default=UserRole.client)
    is_active   = Column(Boolean, nullable=False, default=True)
    bonus_balance      = Column(Numeric(12, 2), nullable=False, default=0)
    total_spent        = Column(Numeric(12, 2), nullable=False, default=0)
    loyalty_level      = Column(Enum(LoyaltyLevel, name="loyaltylevel"), nullable=False, default=LoyaltyLevel.novice)
    cashback_percent   = Column(Float, nullable=False, default=0.0)
    referral_code      = Column(String(16), unique=True, nullable=True)
    referred_by_id     = Column(BigInteger, ForeignKey("users.id"), nullable=True)
    referral_count     = Column(Integer, nullable=False, default=0)
    referral_bonus_total = Column(Numeric(12, 2), nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    executor_profile  = relationship("ExecutorProfile", back_populates="user", uselist=False)
    orders_as_client  = relationship("Order", back_populates="client", foreign_keys="Order.client_id")
    orders_as_executor = relationship("Order", back_populates="executor", foreign_keys="Order.executor_id")
    bonus_transactions = relationship("BonusTransaction", back_populates="user")
    referrals_sent    = relationship("Referral", back_populates="referrer", foreign_keys="Referral.referrer_id")
    reviews           = relationship("Review", back_populates="client")

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
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    user = relationship("User", back_populates="executor_profile")

class Order(Base):
    __tablename__ = "orders"
    id          = Column(Integer, primary_key=True, autoincrement=True)
    client_id   = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    executor_id = Column(BigInteger, ForeignKey("users.id"), nullable=True)
    work_type          = Column(Enum(WorkType, name="worktype"), nullable=False)
    subject            = Column(String(256), nullable=False)
    topic              = Column(String(512), nullable=False)
    teacher            = Column(String(256), nullable=True)
    requirements       = Column(Text, nullable=True)
    antiplagiat_percent = Column(Integer, nullable=True)
    deadline           = Column(DateTime(timezone=True), nullable=True)
    urgency            = Column(Enum(UrgencyLevel, name="urgencylevel"), nullable=True)
    status = Column(Enum(OrderStatus, name="orderstatus"), nullable=False, default=OrderStatus.new)
    step   = Column(Integer, nullable=False, default=0)
    price            = Column(Numeric(12, 2), nullable=True)
    commission_amount = Column(Numeric(12, 2), nullable=True)
    executor_amount  = Column(Numeric(12, 2), nullable=True)
    bonus_used       = Column(Numeric(12, 2), nullable=False, default=0)
    cashback_earned  = Column(Numeric(12, 2), nullable=False, default=0)
    created_at    = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    assigned_at   = Column(DateTime(timezone=True), nullable=True)
    completed_at  = Column(DateTime(timezone=True), nullable=True)
    updated_at    = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    client   = relationship("User", back_populates="orders_as_client", foreign_keys=[client_id])
    executor = relationship("User", back_populates="orders_as_executor", foreign_keys=[executor_id])
    payments = relationship("Payment", back_populates="order")
    review   = relationship("Review", back_populates="order", uselist=False)

class Payment(Base):
    __tablename__ = "payments"
    id      = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    user_id  = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    amount              = Column(Numeric(12, 2), nullable=False)
    status              = Column(Enum(PaymentStatus, name="paymentstatus"), nullable=False, default=PaymentStatus.pending)
    stage               = Column(Enum(PaymentStage, name="paymentstage"), nullable=False)
    yookassa_payment_id = Column(String(64), unique=True, nullable=True)
    prepayment_amount   = Column(Numeric(12, 2), nullable=True)
    final_payment_amount = Column(Numeric(12, 2), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    paid_at    = Column(DateTime(timezone=True), nullable=True)
    order = relationship("Order", back_populates="payments")
    user  = relationship("User")

class BonusTransaction(Base):
    __tablename__ = "bonus_transactions"
    id      = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    amount          = Column(Numeric(12, 2), nullable=False)
    type            = Column(Enum(BonusType, name="bonustype"), nullable=False)
    description     = Column(String(512), nullable=False)
    related_order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    user  = relationship("User", back_populates="bonus_transactions")
    order = relationship("Order")

class Referral(Base):
    __tablename__ = "referrals"
    __table_args__ = (UniqueConstraint("referrer_id", "referred_id", name="uq_referral_pair"),)
    id          = Column(Integer, primary_key=True, autoincrement=True)
    referrer_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    referred_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    status       = Column(Enum(ReferralStatus, name="referralstatus"), nullable=False, default=ReferralStatus.pending)
    bonus_paid   = Column(Boolean, nullable=False, default=False)
    bonus_paid_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    referrer = relationship("User", back_populates="referrals_sent", foreign_keys=[referrer_id])
    referred = relationship("User", foreign_keys=[referred_id])

class Review(Base):
    __tablename__ = "reviews"
    __table_args__ = (UniqueConstraint("order_id", name="uq_review_per_order"),)
    id        = Column(Integer, primary_key=True, autoincrement=True)
    order_id  = Column(Integer, ForeignKey("orders.id"), nullable=False)
    client_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    nps_score    = Column(Integer, nullable=False)
    comment      = Column(Text, nullable=True)
    is_published = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    order  = relationship("Order", back_populates="review")
    client = relationship("User", back_populates="reviews")

class HolidayBonus(Base):
    __tablename__ = "holiday_bonuses"
    id           = Column(Integer, primary_key=True, autoincrement=True)
    name         = Column(String(256), nullable=False)
    bonus_amount = Column(Numeric(12, 2), nullable=False)
    target       = Column(Enum(HolidayTarget, name="holidaytarget"), nullable=False, default=HolidayTarget.all)
    trigger_date = Column(DateTime(timezone=True), nullable=False)
    is_active    = Column(Boolean, nullable=False, default=True)
    is_sent      = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

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
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    author = relationship("User")
