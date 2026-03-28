"""
backend/bot/services/payment_provider.py
=========================================
Абстрактный интерфейс платёжного провайдера + общие типы данных.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal


@dataclass
class PaymentResult:
    """Результат создания платежа у провайдера."""
    provider_payment_id: str
    confirmation_url: str   # URL для редиректа клиента на оплату
    status: str


@dataclass
class RefundResult:
    """Результат операции возврата."""
    provider_refund_id: str
    status: str
    amount: Decimal


class PaymentProvider(ABC):
    """Абстрактный интерфейс платёжного провайдера."""

    @abstractmethod
    async def create_payment(
        self,
        amount: Decimal,
        description: str,
        order_id: int,
        return_url: str,
    ) -> PaymentResult:
        """Создать платёж и вернуть URL для оплаты."""
        ...

    @abstractmethod
    async def refund(
        self,
        provider_payment_id: str,
        amount: Decimal,
    ) -> RefundResult:
        """Выполнить возврат средств."""
        ...

    @abstractmethod
    async def get_status(
        self,
        provider_payment_id: str,
    ) -> str:
        """Получить текущий статус платежа у провайдера."""
        ...

    @abstractmethod
    async def verify_webhook(
        self,
        body: bytes,
        headers: dict,
    ) -> bool:
        """Проверить подпись webhook от провайдера."""
        ...
