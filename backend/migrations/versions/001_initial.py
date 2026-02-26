"""Initial migration — create all tables

Revision ID: 001_initial
Revises:
Create Date: 2026-02-23

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── 1. Создаём ENUM типы через сырой SQL с проверкой ──────
    enums = {
        "userrole": "('client', 'executor', 'admin')",
        "loyaltylevel": "('novice', 'student', 'regular', 'vip')",
        "orderstatus": "('new', 'assigned', 'in_progress', 'review', 'done', 'canceled')",
        "paymentstatus": "('pending', 'waiting', 'paid', 'refunded', 'canceled')",
        "paymentstage": "('prepayment', 'final')",
        "bonustype": "('registration', 'purchase_cashback', 'referral', 'holiday', 'manual', 'spent')",
        "referralstatus": "('pending', 'activated')",
        "holidaytarget": "('all', 'level_2', 'level_3', 'level_4')",
        "worktype": "('coursework', 'diploma', 'abstract', 'lab', 'practice', 'other')",
        "urgencylevel": "('three_days', 'one_week', 'two_weeks', 'one_month')"
    }
    
    for name, values in enums.items():
        op.execute(sa.text(f"DO $$ BEGIN IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = '{name}') THEN CREATE TYPE {name} AS ENUM {values}; END IF; END $$;"))

    def pg_enum(name, *values):
        return postgresql.ENUM(*values, name=name, create_type=False)

    # ── 3. TABLE: users ────────────────────────────────────────────
    op.create_table(
        "users",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("username", sa.String(64), nullable=True),
        sa.Column("first_name", sa.String(128), nullable=True),
        sa.Column("last_name", sa.String(128), nullable=True),
        sa.Column("role", pg_enum("userrole", "client", "executor", "admin"),
                  nullable=False, server_default="client"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("bonus_balance", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("total_spent", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("loyalty_level", pg_enum("loyaltylevel", "novice", "student", "regular", "vip"),
                  nullable=False, server_default="novice"),
        sa.Column("cashback_percent", sa.Float(), nullable=False, server_default="0"),
        sa.Column("referral_code", sa.String(16), nullable=True),
        sa.Column("referred_by_id", sa.BigInteger(), nullable=True),
        sa.Column("referral_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("referral_bonus_total", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("referral_code", name="uq_users_referral_code"),
        sa.ForeignKeyConstraint(["referred_by_id"], ["users.id"], name="fk_users_referred_by"),
    )

    # ── 4. TABLE: executor_profiles ────────────────────────────────
    op.create_table(
        "executor_profiles",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("specializations", postgresql.ARRAY(sa.String()), nullable=False, server_default="{}"),
        sa.Column("bio", sa.Text(), nullable=True),
        sa.Column("experience_years", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("rating", sa.Float(), nullable=False, server_default="5.0"),
        sa.Column("completed_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_verified", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("is_available", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("bonus_balance", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", name="uq_executor_profiles_user_id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_executor_profiles_user"),
    )

    # ── 5. TABLE: orders ────────────────────────────────────────────
    op.create_table(
        "orders",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("client_id", sa.BigInteger(), nullable=False),
        sa.Column("executor_id", sa.BigInteger(), nullable=True),
        sa.Column("work_type", pg_enum("worktype", "coursework", "diploma", "abstract", "lab", "practice", "other"),
                  nullable=False),
        sa.Column("subject", sa.String(256), nullable=False),
        sa.Column("topic", sa.String(512), nullable=False),
        sa.Column("teacher", sa.String(256), nullable=True),
        sa.Column("requirements", sa.Text(), nullable=True),
        sa.Column("antiplagiat_percent", sa.Integer(), nullable=True),
        sa.Column("deadline", sa.DateTime(timezone=True), nullable=True),
        sa.Column("urgency", pg_enum("urgencylevel", "three_days", "one_week", "two_weeks", "one_month"), nullable=True),
        sa.Column("status", pg_enum("orderstatus", "new", "assigned", "in_progress", "review", "done", "canceled"),
                  nullable=False, server_default="new"),
        sa.Column("step", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("price", sa.Numeric(12, 2), nullable=True),
        sa.Column("commission_amount", sa.Numeric(12, 2), nullable=True),
        sa.Column("executor_amount", sa.Numeric(12, 2), nullable=True),
        sa.Column("bonus_used", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("cashback_earned", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("assigned_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["client_id"], ["users.id"], name="fk_orders_client"),
        sa.ForeignKeyConstraint(["executor_id"], ["users.id"], name="fk_orders_executor"),
    )

    # ── 6. TABLE: payments ──────────────────────────────────────────
    op.create_table(
        "payments",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("order_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("status", pg_enum("paymentstatus", "pending", "waiting", "paid", "refunded", "canceled"),
                  nullable=False, server_default="pending"),
        sa.Column("stage", pg_enum("paymentstage", "prepayment", "final"), nullable=False),
        sa.Column("yookassa_payment_id", sa.String(64), nullable=True),
        sa.Column("prepayment_amount", sa.Numeric(12, 2), nullable=True),
        sa.Column("final_payment_amount", sa.Numeric(12, 2), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("paid_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("yookassa_payment_id", name="uq_payments_yookassa_id"),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"], name="fk_payments_order"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_payments_user"),
    )

    # ── 7. TABLE: bonus_transactions ────────────────────────────────
    op.create_table(
        "bonus_transactions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("type", pg_enum("bonustype", "registration", "purchase_cashback", "referral", "holiday", "manual", "spent"),
                  nullable=False),
        sa.Column("description", sa.String(512), nullable=False),
        sa.Column("related_order_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_bonus_tx_user"),
        sa.ForeignKeyConstraint(["related_order_id"], ["orders.id"], name="fk_bonus_tx_order"),
    )

    # ── 8. TABLE: referrals ─────────────────────────────────────────
    op.create_table(
        "referrals",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("referrer_id", sa.BigInteger(), nullable=False),
        sa.Column("referred_id", sa.BigInteger(), nullable=False),
        sa.Column("status", pg_enum("referralstatus", "pending", "activated"),
                  nullable=False, server_default="pending"),
        sa.Column("bonus_paid", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("bonus_paid_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("referrer_id", "referred_id", name="uq_referral_pair"),
        sa.ForeignKeyConstraint(["referrer_id"], ["users.id"], name="fk_referrals_referrer"),
        sa.ForeignKeyConstraint(["referred_id"], ["users.id"], name="fk_referrals_referred"),
    )

    # ── 9. TABLE: reviews ───────────────────────────────────────────
    op.create_table(
        "reviews",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("order_id", sa.Integer(), nullable=False),
        sa.Column("client_id", sa.BigInteger(), nullable=False),
        sa.Column("nps_score", sa.Integer(), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("is_published", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("order_id", name="uq_review_per_order"),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"], name="fk_reviews_order"),
        sa.ForeignKeyConstraint(["client_id"], ["users.id"], name="fk_reviews_client"),
    )

    # ── 10. TABLE: holiday_bonuses ──────────────────────────────────
    op.create_table(
        "holiday_bonuses",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(256), nullable=False),
        sa.Column("bonus_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("target", pg_enum("holidaytarget", "all", "level_2", "level_3", "level_4"),
                  nullable=False, server_default="all"),
        sa.Column("trigger_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("is_sent", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    # ── 11. TABLE: knowledge_base ───────────────────────────────────
    op.create_table(
        "knowledge_base",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("teacher_name", sa.String(256), nullable=False),
        sa.Column("department", sa.String(256), nullable=True),
        sa.Column("requirements", sa.Text(), nullable=True),
        sa.Column("formatting_notes", sa.Text(), nullable=True),
        sa.Column("comments", sa.Text(), nullable=True),
        sa.Column("created_by", sa.BigInteger(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], name="fk_knowledge_base_author"),
    )


def downgrade() -> None:
    op.drop_table("knowledge_base")
    op.drop_table("holiday_bonuses")
    op.drop_table("reviews")
    op.drop_table("referrals")
    op.drop_table("bonus_transactions")
    op.drop_table("payments")
    op.drop_table("orders")
    op.drop_table("executor_profiles")
    op.drop_table("users")

    for name in [
        "userrole", "loyaltylevel", "orderstatus", "paymentstatus",
        "paymentstage", "bonustype", "referralstatus", "holidaytarget",
        "worktype", "urgencylevel",
    ]:
        op.execute(f"DROP TYPE IF EXISTS {name} CASCADE")
