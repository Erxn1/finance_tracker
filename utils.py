"""
Вспомогательные функции для валидации и форматирования.
"""

from datetime import datetime


def validate_date(date_str: str) -> bool:
    """Проверка корректности даты в формате ГГГГ-ММ-ДД."""
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def validate_amount(amount_str: str) -> bool:
    """Проверка, что строка может быть преобразована в положительное число."""
    try:
        value = float(amount_str)
        return value > 0
    except ValueError:
        return False


def format_currency(amount: float) -> str:
    """Форматирование суммы как валюты."""
    return f"{amount:,.2f} ₽"