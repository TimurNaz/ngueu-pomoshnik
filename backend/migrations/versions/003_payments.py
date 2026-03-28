"""Add payment system: new statuses, order/payment fields

Revision ID: 003_payments
Revises: 002_notifications
Create Date: 2026-03-22

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "003_payments"
down_revision: Union[str, None] = "002_notifications"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── 1. ALTER TYPE — добавление новых enum-значений ──────────
    # PostgreSQL не позволяет ALTER TYPE ADD VALUE внутри транзакции,
    # поэтому коммитим текущую транзакцию Alembic перед этим блоком.
    op.execute(sa.text("COMMIT"))

    # OrderStatus: +5 значений
    for val in ("priced", "paid", "confirming", "completed", "disputed"):
        op.execute(sa.text(
            f"ALTER TYPE orderstatus ADD VALUE IF NOT EXISTS '{val}'"
        ))

    # NotificationType: +8 значений
    for val in (
        "price_set", "payment_pending", "payment_success", "payment_refunded",
        "order_confirming", "order_completed", "order_disputed", "payment_reminder",
    ):
        op.execute(sa.text(
            f"ALTER TYPE notificationtype ADD VALUE IF NOT EXISTS '{val}'"
        ))

    # Открываем новую транзакцию для DDL-операций
    op.execute(sa.text("BEGIN"))

    # ── 2. Orders: новые поля ───────────────────────────────────
    op.add_column("orders", sa.Column("priced_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("orders", sa.Column("paid_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("orders", sa.Column("confirmed_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("orders", sa.Column("payment_deadline", sa.DateTime(timezone=True), nullable=True))

    # ── 3. Payments: переименование + новые поля ────────────────
    # Переименовать yookassa_payment_id → provider_payment_id
    op.alter_column("payments", "yookassa_payment_id", new_column_name="provider_payment_id")
    op.drop_constraint("uq_payments_yookassa_id", "payments", type_="unique")
    op.create_unique_constraint("uq_payments_provider_id", "payments", ["provider_payment_id"])

    # Новые колонки
    op.add_column("payments", sa.Column("provider_name", sa.String(32), nullable=True))
    op.add_column("payments", sa.Column("frozen_amount", sa.Numeric(12, 2), nullable=True))
    op.add_column("payments", sa.Column("released_amount", sa.Numeric(12, 2), server_default="0"))
    op.add_column("payments", sa.Column("refunded_amount", sa.Numeric(12, 2), server_default="0"))
    op.add_column("payments", sa.Column("bonus_used", sa.Numeric(12, 2), server_default="0"))
    op.add_column("payments", sa.Column("executor_paid", sa.Boolean(), server_default="false"))
    op.add_column("payments", sa.Column("executor_paid_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("payments", sa.Column("cancel_deadline", sa.DateTime(timezone=True), nullable=True))
    op.add_column("payments", sa.Column("confirmation_deadline", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    # ── Payments: убрать новые колонки ──────────────────────────
    for col in (
        "provider_name", "frozen_amount", "released_amount", "refunded_amount",
        "bonus_used", "executor_paid", "executor_paid_at",
        "cancel_deadline", "confirmation_deadline",
    ):
        op.drop_column("payments", col)

    # Переименовать обратно
    op.drop_constraint("uq_payments_provider_id", "payments", type_="unique")
    op.alter_column("payments", "provider_payment_id", new_column_name="yookassa_payment_id")
    op.create_unique_constraint("uq_payments_yookassa_id", "payments", ["yookassa_payment_id"])

    # ── Orders: убрать новые колонки ────────────────────────────
    for col in ("priced_at", "paid_at", "confirmed_at", "payment_deadline"):
        op.drop_column("orders", col)

    # Enum-значения нельзя удалить в PostgreSQL без пересоздания типа.
    # Оставляем как есть для безопасности downgrade.
