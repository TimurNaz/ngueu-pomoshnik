"""Add notifications table

Revision ID: 002_notifications
Revises: 001_initial
Create Date: 2026-03-22

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "002_notifications"
down_revision: Union[str, None] = "001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Создаём ENUM тип
    op.execute(sa.text(
        "DO $$ BEGIN "
        "IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'notificationtype') "
        "THEN CREATE TYPE notificationtype AS ENUM "
        "('order_created', 'executor_assigned', 'order_in_progress', 'order_review', "
        "'order_done', 'order_canceled', 'bonus', 'system'); "
        "END IF; END $$;"
    ))

    notificationtype = postgresql.ENUM(
        'order_created', 'executor_assigned', 'order_in_progress', 'order_review',
        'order_done', 'order_canceled', 'bonus', 'system',
        name='notificationtype', create_type=False
    )

    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.BigInteger(), sa.ForeignKey("users.id"), nullable=False, index=True),
        sa.Column("type", notificationtype, nullable=False),
        sa.Column("title", sa.String(256), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("order_id", sa.Integer(), sa.ForeignKey("orders.id"), nullable=True),
        sa.Column("is_read", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("notifications")
    op.execute(sa.text("DROP TYPE IF EXISTS notificationtype"))
