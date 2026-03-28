"""
Реализации платёжных провайдеров.
"""

from services.payment_provider import PaymentProvider


def get_provider(provider_name: str) -> PaymentProvider:
    """Фабрика: возвращает экземпляр провайдера по имени."""
    if provider_name == "mock":
        from services.providers.mock_provider import MockProvider
        return MockProvider()
    # elif provider_name == "yookassa":
    #     from services.providers.yookassa_provider import YooKassaProvider
    #     return YooKassaProvider()
    raise ValueError(f"Неизвестный платёжный провайдер: {provider_name}")
