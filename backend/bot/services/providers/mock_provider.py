"""
Mock-провайдер для разработки и тестирования.
Все операции мгновенно «успешны», без реальных платежей.
"""

import uuid
from decimal import Decimal

from services.payment_provider import PaymentProvider, PaymentResult, RefundResult


class MockProvider(PaymentProvider):
    """Mock-провайдер: мгновенный успех всех операций."""

    async def create_payment(
        self,
        amount: Decimal,
        description: str,
        order_id: int,
        return_url: str,
    ) -> PaymentResult:
        payment_id = f"mock_{uuid.uuid4().hex[:16]}"
        return PaymentResult(
            provider_payment_id=payment_id,
            confirmation_url=f"{return_url}?payment_id={payment_id}&mock=1",
            status="pending",
        )

    async def refund(
        self,
        provider_payment_id: str,
        amount: Decimal,
    ) -> RefundResult:
        return RefundResult(
            provider_refund_id=f"refund_{uuid.uuid4().hex[:8]}",
            status="succeeded",
            amount=amount,
        )

    async def get_status(
        self,
        provider_payment_id: str,
    ) -> str:
        return "succeeded"

    async def verify_webhook(
        self,
        body: bytes,
        headers: dict,
    ) -> bool:
        return True
