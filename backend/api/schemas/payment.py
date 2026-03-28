from pydantic import BaseModel
from typing import Optional


class PaymentCreate(BaseModel):
    order_id: int
    user_id: int
    bonus_amount: float = 0.0


class PaymentCancel(BaseModel):
    user_id: int


class OrderConfirm(BaseModel):
    user_id: int


class OrderDispute(BaseModel):
    user_id: int
    reason: str
