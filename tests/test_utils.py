"""
Тесты для утилит
"""

import unittest
from utils import validate_date, validate_amount, format_currency


class TestUtils(unittest.TestCase):
    """Тесты для вспомогательных функций"""

    def test_validate_date(self):
        """Валидация даты"""
        # Валидные даты
        self.assertTrue(validate_date("2024-01-15"))
        self.assertTrue(validate_date("2024-12-31"))
        self.assertTrue(validate_date("2020-02-29"))  # Високосный год

        # Невалидные даты
        self.assertFalse(validate_date("2024-13-01"))  # Несуществующий месяц
        self.assertFalse(validate_date("2024-01-32"))  # Несуществующий день
        self.assertFalse(validate_date("01-01-2024"))  # Неправильный формат
        self.assertFalse(validate_date("2024/01/15"))  # Неправильный разделитель
        self.assertFalse(validate_date(""))  # Пустая строка
        self.assertFalse(validate_date("abc"))  # Не дата

    def test_validate_amount(self):
        """Валидация суммы"""
        # Валидные суммы
        self.assertTrue(validate_amount("100"))
        self.assertTrue(validate_amount("100.50"))
        self.assertTrue(validate_amount("0.01"))  # Минимальная положительная
        self.assertTrue(validate_amount("999999.99"))

        # Невалидные суммы
        self.assertFalse(validate_amount("0"))  # Ноль
        self.assertFalse(validate_amount("-100"))  # Отрицательная
        self.assertFalse(validate_amount(""))  # Пустая строка
        self.assertFalse(validate_amount("abc"))  # Не число
        self.assertFalse(validate_amount("100,50"))  # Неправильный разделитель

        # Граничные случаи
        self.assertTrue(validate_amount("0.0001"))  # Очень маленькое положительное
        self.assertTrue(validate_amount("0.00001"))  # Даже очень маленькое число валидно

    def test_format_currency(self):
        """Форматирование валюты"""
        self.assertEqual(format_currency(1000), "1,000.00 ₽")
        self.assertEqual(format_currency(1000.50), "1,000.50 ₽")
        self.assertEqual(format_currency(0.01), "0.01 ₽")
        self.assertEqual(format_currency(9999999.99), "9,999,999.99 ₽")

        # Отрицательные числа
        self.assertEqual(format_currency(-1000), "-1,000.00 ₽")
        self.assertEqual(format_currency(-1000.50), "-1,000.50 ₽")


if __name__ == "__main__":
    unittest.main()