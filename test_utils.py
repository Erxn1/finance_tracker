"""
Модуль test_utils.py
Unit-тесты для функций валидации из utils.py.
"""

import unittest
import re
from datetime import datetime
from utils import validate_date, validate_amount, validate_category_name, format_currency


class TestValidateDate(unittest.TestCase):
    """Тестирует функцию validate_date()."""

    def test_valid_dates(self):
        """Проверяет корректные даты."""
        valid_dates = [
            "2024-01-01",  # Первый день года
            "2024-12-31",  # Последний день года
            "2024-02-29",  # Високосный год
            "2023-02-28",  # Не високосный год
            "2000-01-01",  # Начало века
            "2099-12-31",  # Конец века
        ]

        for date_str in valid_dates:
            with self.subTest(date=date_str):
                self.assertTrue(
                    validate_date(date_str),
                    f"Дата '{date_str}' должна быть валидной"
                )

    def test_invalid_dates(self):
        """Проверяет некорректные даты."""
        invalid_dates = [
            "2024-13-01",  # Несуществующий месяц
            "2024-00-01",  # Нулевой месяц
            "2024-01-32",  # Несуществующий день
            "2024-01-00",  # Нулевой день
            "2024-02-30",  # 30 февраля
            "2023-02-29",  # 29 февраля в невисокосный год
            "24-01-01",  # Короткий год
            "2024-1-01",  # Месяц без ведущего нуля
            "2024-01-1",  # День без ведущего нуля
            "2024/01/01",  # Неправильный разделитель
            "01-01-2024",  # Неправильный формат (день-месяц-год)
            "not-a-date",  # Не дата вообще
            "",  # Пустая строка
            "   ",  # Пробелы
        ]

        for date_str in invalid_dates:
            with self.subTest(date=date_str):
                self.assertFalse(
                    validate_date(date_str),
                    f"Дата '{date_str}' должна быть невалидной"
                )

    def test_edge_cases(self):
        """Проверяет граничные случаи."""
        # Минимальная разумная дата
        self.assertTrue(validate_date("1900-01-01"))

        # Максимальная разумная дата
        self.assertTrue(validate_date("2100-12-31"))

        # Проверяем регулярное выражение
        pattern = r'^\d{4}-\d{2}-\d{2}$'

        valid_pattern = "2024-05-15"
        self.assertIsNotNone(re.match(pattern, valid_pattern))

        invalid_pattern = "2024-5-15"  # Без ведущего нуля
        self.assertIsNone(re.match(pattern, invalid_pattern))

    def test_datetime_conversion(self):
        """Проверяет, что валидные даты могут быть преобразованы в datetime."""
        test_cases = [
            ("2024-05-15", datetime(2024, 5, 15)),
            ("2024-12-31", datetime(2024, 12, 31)),
            ("2000-01-01", datetime(2000, 1, 1)),
        ]

        for date_str, expected_dt in test_cases:
            with self.subTest(date=date_str):
                self.assertTrue(validate_date(date_str))

                # Проверяем преобразование
                dt = datetime.strptime(date_str, "%Y-%m-%d")
                self.assertEqual(dt, expected_dt)


class TestValidateAmount(unittest.TestCase):
    """Тестирует функцию validate_amount()."""

    def test_valid_amounts(self):
        """Проверяет корректные суммы."""
        valid_amounts = [
            "0.01",  # Минимальная сумма
            "1",  # Целое число
            "100",  # Большее целое
            "100.50",  # С копейками
            "9999.99",  # Максимальные копейки
            "1000000",  # Большая сумма
            "100.5",  # Без ведущего нуля в копейках
            "0.1",  # Десятая часть
            "0.99",  # Девяносто девять копеек
        ]

        for amount_str in valid_amounts:
            with self.subTest(amount=amount_str):
                self.assertTrue(
                    validate_amount(amount_str),
                    f"Сумма '{amount_str}' должна быть валидной"
                )

    def test_invalid_amounts(self):
        """Проверяет некорректные суммы."""
        invalid_amounts = [
            "-100",  # Отрицательная
            "0",  # Ноль
            "-0.01",  # Отрицательная с копейками
            "100.555",  # Три знака после запятой
            "100.001",  # Три знака после запятой
            "not-a-number",  # Не число
            "1.2.3",  # Несколько точек
            "1,50",  # Запятая вместо точки
            "",  # Пустая строка
            "   ",  # Пробелы
            "100.",  # Точка без цифр после
            ".50",  # Точка без цифр до
        ]

        for amount_str in invalid_amounts:
            with self.subTest(amount=amount_str):
                self.assertFalse(
                    validate_amount(amount_str),
                    f"Сумма '{amount_str}' должна быть невалидной"
                )

    def test_amount_conversion(self):
        """Проверяет преобразование строки в число."""
        test_cases = [
            ("100.50", 100.50),
            ("0.01", 0.01),
            ("999.99", 999.99),
            ("100", 100.0),
            ("0.1", 0.1),
        ]

        for amount_str, expected_float in test_cases:
            with self.subTest(amount=amount_str):
                self.assertTrue(validate_amount(amount_str))

                # Проверяем преобразование
                amount_float = float(amount_str)
                self.assertEqual(amount_float, expected_float)
                self.assertGreater(amount_float, 0)  # Должно быть положительным


class TestValidateCategoryName(unittest.TestCase):
    """Тестирует функцию validate_category_name()."""

    def test_valid_category_names(self):
        """Проверяет корректные названия категорий."""
        valid_names = [
            "Продукты",
            "Транспорт",
            "Развлечения",
            "Зарплата",
            "А",  # Минимальная длина
            "Категория с пробелами",  # С пробелами
            "Категория-с-дефисами",  # С дефисами
            "Категория_с_подчеркиваниями",  # С подчеркиваниями
            "Категория123",  # С цифрами
            "A" * 50,  # Максимальная длина
        ]

        for name in valid_names:
            with self.subTest(name=name):
                self.assertTrue(
                    validate_category_name(name),
                    f"Название '{name}' должно быть валидным"
                )

    def test_invalid_category_names(self):
        """Проверяет некорректные названия категорий."""
        invalid_names = [
            "",  # Пустая строка
            "   ",  # Только пробелы
            "\t\n",  # Только пробельные символы
            "A" * 51,  # Слишком длинное (>50)
            "; DROP TABLE users",  # SQL-инъекция
            "-- комментарий",  # SQL-комментарий
            "/* комментарий */",  # SQL-комментарий
            "категория;",  # Точка с запятой
            "категория--",  # Двойной дефис
            "категория/*",  # Начинается комментарий
            "*/категория",  # Заканчивается комментарий
        ]

        for name in invalid_names:
            with self.subTest(name=name):
                self.assertFalse(
                    validate_category_name(name),
                    f"Название '{name}' должно быть невалидным"
                )

    def test_category_name_trimming(self):
        """Проверяет обрезку пробелов."""
        test_cases = [
            ("  Продукты  ", "Продукты"),  # Пробелы по краям
            ("Транспорт\t\n", "Транспорт"),  # Пробельные символы
            ("  Развлечения \n ", "Развлечения"),
        ]

        for input_name, expected_name in test_cases:
            with self.subTest(name=input_name):
                # Проверяем, что функция обрабатывает пробелы
                is_valid = validate_category_name(input_name)

                # Если есть только пробелы - невалидно
                if not input_name.strip():
                    self.assertFalse(is_valid)
                else:
                    self.assertTrue(is_valid)


class TestFormatCurrency(unittest.TestCase):
    """Тестирует функцию format_currency()."""

    def test_format_currency_basic(self):
        """Проверяет базовое форматирование."""
        test_cases = [
            (100.50, "100.50 ₽"),
            (0.01, "0.01 ₽"),
            (9999.99, "9,999.99 ₽"),
            (1000000, "1,000,000.00 ₽"),
            (0, "0.00 ₽"),
            (-100.50, "-100.50 ₽"),  # Отрицательные тоже форматируются
        ]

        for amount, expected in test_cases:
            with self.subTest(amount=amount, expected=expected):
                result = format_currency(amount)
                self.assertEqual(result, expected)

    def test_format_currency_large_numbers(self):
        """Проверяет форматирование больших чисел."""
        test_cases = [
            (123456789.99, "123,456,789.99 ₽"),
            (9876543210.50, "9,876,543,210.50 ₽"),
        ]

        for amount, expected in test_cases:
            with self.subTest(amount=amount):
                result = format_currency(amount)
                self.assertEqual(result, expected)

    def test_format_currency_edge_cases(self):
        """Проверяет граничные случаи."""
        # Очень маленькое число
        self.assertEqual(format_currency(0.001), "0.00 ₽")  # Округление

        # Очень большое число
        self.assertEqual(format_currency(1e12), "1,000,000,000,000.00 ₽")

        # Точность
        self.assertEqual(format_currency(100.999), "101.00 ₽")  # Округление
        self.assertEqual(format_currency(100.004), "100.00 ₽")  # Округление вниз
        self.assertEqual(format_currency(100.005), "100.01 ₽")  # Округление вверх


class TestUtilsIntegration(unittest.TestCase):
    """Интеграционные тесты для модуля utils."""

    def test_full_validation_workflow(self):
        """Проверяет полный рабочий процесс валидации."""
        # Корректные данные
        valid_data = {
            "date": "2024-05-15",
            "amount": "1500.50",
            "category": "Продукты",
        }

        self.assertTrue(validate_date(valid_data["date"]))
        self.assertTrue(validate_amount(valid_data["amount"]))
        self.assertTrue(validate_category_name(valid_data["category"]))

        # Некорректные данные
        invalid_data = {
            "date": "2024-13-01",
            "amount": "-100",
            "category": "",
        }

        self.assertFalse(validate_date(invalid_data["date"]))
        self.assertFalse(validate_amount(invalid_data["amount"]))
        self.assertFalse(validate_category_name(invalid_data["category"]))

    def test_real_world_scenarios(self):
        """Тестирует реальные сценарии использования."""
        scenarios = [
            {
                "description": "Покупка в магазине",
                "date": "2024-05-15",
                "amount": "1500.50",
                "category": "Продукты",
                "should_be_valid": True,
            },
            {
                "description": "Зарплата",
                "date": "2024-05-31",
                "amount": "75000",
                "category": "Зарплата",
                "should_be_valid": True,
            },
            {
                "description": "Некорректная дата",
                "date": "2024-02-30",
                "amount": "500",
                "category": "Транспорт",
                "should_be_valid": False,
            },
            {
                "description": "Отрицательная сумма",
                "date": "2024-05-15",
                "amount": "-100",
                "category": "Развлечения",
                "should_be_valid": False,
            },
            {
                "description": "Пустая категория",
                "date": "2024-05-15",
                "amount": "1000",
                "category": "",
                "should_be_valid": False,
            },
        ]

        for scenario in scenarios:
            with self.subTest(description=scenario["description"]):
                date_valid = validate_date(scenario["date"])
                amount_valid = validate_amount(scenario["amount"])
                category_valid = validate_category_name(scenario["category"])

                all_valid = date_valid and amount_valid and category_valid

                self.assertEqual(
                    all_valid,
                    scenario["should_be_valid"],
                    f"Сценарий '{scenario['description']}': ожидалось {scenario['should_be_valid']}, "
                    f"получено {all_valid} (дата: {date_valid}, сумма: {amount_valid}, "
                    f"категория: {category_valid})"
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)