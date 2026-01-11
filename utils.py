"""
Модуль utils.py
Вспомогательные функции для валидации данных.
Исправлено округление валюты с использованием Decimal для точности.
"""

import re
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP


def validate_date(date_string: str) -> bool:
    """
    Проверяет, соответствует ли строка формату YYYY-MM-DD.

    Args:
        date_string: строка с датой

    Returns:
        True если формат правильный, False в противном случае
    """
    pattern = r'^\d{4}-\d{2}-\d{2}$'
    if not re.match(pattern, date_string):
        return False

    try:
        datetime.strptime(date_string, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def validate_amount(amount_string: str) -> bool:
    """
    Проверяет, является ли строка положительным числом.

    Args:
        amount_string: строка с суммой

    Returns:
        True если это положительное число, False в противном случае
    """
    # Разрешаем запятую в качестве разделителя дробной части
    if ',' in amount_string:
        amount_string = amount_string.replace(',', '.')

    # Проверяем формат: цифры, необязательная точка и до 2 знаков после
    pattern = r'^\d+(\.\d{1,2})?$'
    if not re.match(pattern, amount_string):
        return False

    try:
        amount = float(amount_string)
        return amount > 0
    except ValueError:
        return False


def validate_category_name(name: str) -> bool:
    """
    Проверяет название категории.

    Args:
        name: название категории

    Returns:
        True если название корректно, False в противном случае
    """
    if not name or not name.strip():
        return False

    # Обрезаем пробелы и проверяем длину
    trimmed_name = name.strip()
    if len(trimmed_name) > 50:
        return False

    # Запрещённые символы для предотвращения SQL-инъекций
    forbidden = [';', '--', '/*', '*/', "'", '"', '`']
    for char in forbidden:
        if char in trimmed_name:
            return False

    return True


def format_currency(amount: float) -> str:
    """
    Форматирует сумму как денежное значение с точным округлением.

    Args:
        amount: сумма (может быть отрицательной для расходов)

    Returns:
        Отформатированная строка с разделителями тысяч и правильным округлением
    """
    try:
        # Преобразуем float в Decimal через строку для максимальной точности
        # Используем 10 знаков после запятой для точности
        decimal_amount = Decimal(str(round(amount, 10)))

        # Округляем до 2 знаков с правилом "банковское округление" (ROUND_HALF_UP)
        rounded = decimal_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        # Форматируем с разделителями тысяч
        # Для отрицательных чисел форматирование работает корректно
        formatted = f"{rounded:,.2f} ₽"

        # Убираем возможные -0.00 (заменяем на 0.00)
        if formatted == "-0.00 ₽":
            return "0.00 ₽"

        return formatted
    except Exception:
        # Fallback на стандартное форматирование в случае ошибки
        return f"{amount:,.2f} ₽"


# Пример использования функций (для тестирования модуля)
if __name__ == "__main__":
    """
    Тестирование функций модуля utils.py
    """
    print("=" * 50)
    print("Тестирование модуля utils.py")
    print("=" * 50)

    # Тест validate_date
    print("\n1. Тест validate_date():")
    test_dates = [
        ("2024-05-15", True),
        ("2024-13-01", False),
        ("2024-02-30", False),
        ("24-05-15", False),
        ("2024/05/15", False),
        ("not-a-date", False),
    ]

    for date_str, expected in test_dates:
        result = validate_date(date_str)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{date_str}' -> {result} (ожидалось: {expected})")

    # Тест validate_amount
    print("\n2. Тест validate_amount():")
    test_amounts = [
        ("100.50", True),
        ("0.01", True),
        ("100", True),
        ("-100", False),
        ("0", False),
        ("100.555", False),
        ("1,50", True),  # С запятой
        ("not-a-number", False),
    ]

    for amount_str, expected in test_amounts:
        result = validate_amount(amount_str)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{amount_str}' -> {result} (ожидалось: {expected})")

    # Тест validate_category_name
    print("\n3. Тест validate_category_name():")
    test_names = [
        ("Продукты", True),
        ("", False),
        ("   ", False),
        ("A" * 51, False),  # Слишком длинное
        ("Категория;DROP", False),  # С точкой с запятой
        ("Категория--", False),  # С двойным дефисом
        ("Категория /*", False),  # С комментарием SQL
    ]

    for name, expected in test_names:
        result = validate_category_name(name)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{name}' -> {result} (ожидалось: {expected})")

    # Тест format_currency
    print("\n4. Тест format_currency():")
    test_amounts = [
        (100.50, "100.50 ₽"),
        (0.01, "0.01 ₽"),
        (100, "100.00 ₽"),
        (1000, "1,000.00 ₽"),
        (1000000, "1,000,000.00 ₽"),
        (100.004, "100.00 ₽"),  # Округление вниз
        (100.005, "100.01 ₽"),  # Округление вверх
        (100.995, "101.00 ₽"),  # Ещё одно округление вверх
        (-100.50, "-100.50 ₽"),  # Отрицательное число
        (-0.005, "0.00 ₽"),  # Отрицательное близкое к нулю
    ]

    for amount, expected in test_amounts:
        result = format_currency(amount)
        status = "✅" if result == expected else "❌"
        print(f"{status} {amount} -> '{result}' (ожидалось: '{expected}')")

    print("\n" + "=" * 50)
    print("Тестирование завершено")
    print("=" * 50)