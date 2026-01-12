"""
Тесты для моделей данных
"""

import unittest
from datetime import datetime
from models import Category, Operation, OperationType


class TestCategory(unittest.TestCase):
    """Тесты для класса Category"""

    def test_category_creation(self):
        """Создание категории с валидными данными"""
        cat = Category(id=1, name="Продукты", description="Еда")
        self.assertEqual(cat.id, 1)
        self.assertEqual(cat.name, "Продукты")
        self.assertEqual(cat.description, "Еда")
        self.assertTrue(cat.is_active)

    def test_category_validation(self):
        """Валидация названия категории"""
        # Пустое название
        with self.assertRaises(ValueError):
            Category(name="")

        # Название с пробелами обрезается
        cat = Category(name="  Тест  ", description="  Описание  ")
        self.assertEqual(cat.name, "Тест")
        self.assertEqual(cat.description, "  Описание  ")

    def test_default_categories(self):
        """Создание категорий по умолчанию"""
        expense_cat = Category.default_expense()
        self.assertEqual(expense_cat.name, "Разное")

        income_cat = Category.default_income()
        self.assertEqual(income_cat.name, "Прочие доходы")


class TestOperation(unittest.TestCase):
    """Тесты для класса Operation"""

    def setUp(self):
        """Подготовка тестовых данных"""
        self.category = Category(name="Тест")
        self.date = datetime(2024, 1, 15)

    def test_operation_creation(self):
        """Создание операции"""
        op = Operation(
            amount=1000.50,
            type=OperationType.INCOME,
            category=self.category,
            date=self.date,
            comment="Тестовая операция"
        )

        self.assertEqual(op.amount, 1000.50)
        self.assertEqual(op.type, OperationType.INCOME)
        self.assertEqual(op.category.name, "Тест")
        self.assertEqual(op.comment, "Тестовая операция")

    def test_operation_validation(self):
        """Валидация суммы операции"""
        # Отрицательная сумма
        with self.assertRaises(ValueError):
            Operation(amount=-100, category=self.category)

        # Нулевая сумма
        with self.assertRaises(ValueError):
            Operation(amount=0, category=self.category)

    def test_default_category(self):
        """Автоматическое создание категории по умолчанию"""
        # Расход без категории
        expense = Operation(amount=100, type=OperationType.EXPENSE)
        self.assertEqual(expense.category.name, "Разное")

        # Доход без категории
        income = Operation(amount=100, type=OperationType.INCOME)
        self.assertEqual(income.category.name, "Прочие доходы")

    def test_signed_amount(self):
        """Сумма со знаком"""
        expense = Operation(amount=100, type=OperationType.EXPENSE)
        self.assertEqual(expense.signed_amount, -100)

        income = Operation(amount=100, type=OperationType.INCOME)
        self.assertEqual(income.signed_amount, 100)

    def test_formatted_amount(self):
        """Форматирование суммы"""
        expense = Operation(amount=1500.50, type=OperationType.EXPENSE)
        self.assertEqual(expense.formatted_amount, "-1500.50 ₽")

        income = Operation(amount=50000, type=OperationType.INCOME)
        self.assertEqual(income.formatted_amount, "+50000.00 ₽")

    def test_comment_truncation(self):
        """Обрезка длинного комментария"""
        long_comment = "Очень длинный комментарий " * 10
        op = Operation(amount=100, category=self.category, comment=long_comment)

        self.assertLessEqual(len(op.comment), 200)
        self.assertTrue(op.comment.endswith("..."))

    def test_update_method(self):
        """Обновление операции"""
        op = Operation(amount=100, category=self.category)
        old_updated = op.updated_at

        op.update(amount=200, comment="Обновлено")

        self.assertEqual(op.amount, 200)
        self.assertEqual(op.comment, "Обновлено")
        self.assertNotEqual(op.updated_at, old_updated)

    def test_to_dict(self):
        """Преобразование в словарь"""
        op = Operation(
            amount=1000,
            type=OperationType.INCOME,
            category=self.category,
            date=datetime(2024, 1, 15),
            comment="Тест"
        )

        result = op.to_dict()
        self.assertEqual(result["amount"], 1000)
        self.assertEqual(result["type"], "доход")
        self.assertEqual(result["category"], "Тест")
        self.assertEqual(result["date"], "2024-01-15")
        self.assertEqual(result["formatted_amount"], "+1000.00 ₽")


if __name__ == "__main__":
    unittest.main()