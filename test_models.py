"""
Модуль test_models.py
Unit-тесты для проверки корректности работы классов из models.py.
Используется стандартный модуль unittest.
"""

import unittest
from datetime import datetime
from models import Operation, OperationType, Category


class TestCategory(unittest.TestCase):
    """Тестирует класс Category."""

    def setUp(self):
        """Подготовка тестовых данных перед каждым тестом."""
        self.test_category = Category(
            id=1,
            name="Продукты",
            description="Покупка еды",
            is_active=True
        )

    def test_category_creation(self):
        """Проверяет корректное создание объекта Category."""
        self.assertEqual(self.test_category.id, 1)
        self.assertEqual(self.test_category.name, "Продукты")
        self.assertEqual(self.test_category.description, "Покупка еды")
        self.assertTrue(self.test_category.is_active)

    def test_category_default_values(self):
        """Проверяет значения по умолчанию."""
        category = Category(name="Тест")
        self.assertIsNone(category.id)
        self.assertEqual(category.name, "Тест")
        self.assertEqual(category.description, "")
        self.assertTrue(category.is_active)

    def test_category_validation_empty_name(self):
        """Проверяет валидацию пустого названия."""
        with self.assertRaises(ValueError):
            Category(name="")

    def test_category_validation_long_name(self):
        """Проверяет валидацию слишком длинного названия."""
        long_name = "Очень длинное название категории, которое превышает лимит в 50 символов"
        with self.assertRaises(ValueError):
            Category(name=long_name)

    def test_category_str_representation(self):
        """Проверяет строковое представление объекта."""
        # dataclass автоматически создаёт __repr__
        repr_str = repr(self.test_category)
        self.assertIn("Category", repr_str)
        self.assertIn("name='Продукты'", repr_str)


class TestOperation(unittest.TestCase):
    """Тестирует класс Operation."""

    def setUp(self):
        """Подготовка тестовых данных."""
        self.category = Category(name="Продукты")
        self.test_operation = Operation(
            id=1,
            amount=1500.50,
            type=OperationType.EXPENSE,
            category=self.category,
            date=datetime(2024, 5, 15),
            comment="Покупка продуктов"
        )

    def test_operation_creation(self):
        """Проверяет корректное создание объекта Operation."""
        self.assertEqual(self.test_operation.id, 1)
        self.assertEqual(self.test_operation.amount, 1500.50)
        self.assertEqual(self.test_operation.type, OperationType.EXPENSE)
        self.assertEqual(self.test_operation.category, self.category)
        self.assertEqual(self.test_operation.comment, "Покупка продуктов")
        self.assertEqual(self.test_operation.date.year, 2024)
        self.assertEqual(self.test_operation.date.month, 5)

    def test_operation_default_values(self):
        """Проверяет значения по умолчанию."""
        operation = Operation(
            amount=100.0,
            type=OperationType.INCOME,
            category=self.category
        )
        self.assertIsNone(operation.id)
        self.assertEqual(operation.comment, "")
        # Дата должна быть близка к текущей
        self.assertIsNotNone(operation.date)

    def test_operation_validation_negative_amount(self):
        """Проверяет валидацию отрицательной суммы."""
        with self.assertRaises(ValueError):
            Operation(amount=-100, type=OperationType.EXPENSE, category=self.category)

    def test_operation_validation_zero_amount(self):
        """Проверяет валидацию нулевой суммы."""
        with self.assertRaises(ValueError):
            Operation(amount=0, type=OperationType.EXPENSE, category=self.category)

    def test_operation_validation_wrong_category_type(self):
        """Проверяет валидацию типа категории."""
        with self.assertRaises(TypeError):
            Operation(amount=100, type=OperationType.EXPENSE, category="Неправильная категория")

    def test_formatted_amount_income(self):
        """Проверяет форматирование суммы для дохода."""
        operation = Operation(
            amount=75000,
            type=OperationType.INCOME,
            category=Category(name="Зарплата")
        )
        self.assertEqual(operation.formatted_amount, "+75000.00")

    def test_formatted_amount_expense(self):
        """Проверяет форматирование суммы для расхода."""
        self.assertEqual(self.test_operation.formatted_amount, "-1500.50")

    def test_get_info_method(self):
        """Проверяет метод get_info()."""
        info = self.test_operation.get_info()

        self.assertEqual(info['id'], 1)
        self.assertEqual(info['amount'], 1500.5)
        self.assertEqual(info['type'], 'расход')
        self.assertEqual(info['category'], 'Продукты')
        self.assertEqual(info['comment'], 'Покупка продуктов')
        # Проверяем формат даты
        self.assertEqual(info['date'], '2024-05-15 00:00')

    def test_update_timestamp(self):
        """Проверяет обновление времени изменения."""
        old_timestamp = self.test_operation.updated_at
        self.test_operation.update_timestamp()
        new_timestamp = self.test_operation.updated_at

        self.assertNotEqual(old_timestamp, new_timestamp)
        self.assertGreater(new_timestamp, old_timestamp)

    def test_comment_truncation(self):
        """Проверяет обрезку длинного комментария."""
        long_comment = "Очень длинный комментарий, который явно превышает лимит в 200 символов. " \
                       "Давайте добавим ещё текста, чтобы точно превысить лимит. " \
                       "Ещё немного текста, и ещё, и ещё, пока не наберём больше 200 символов."

        operation = Operation(
            amount=100,
            type=OperationType.EXPENSE,
            category=self.category,
            comment=long_comment
        )

        # Комментарий должен быть обрезан до 200 символов с добавлением "..."
        self.assertLessEqual(len(operation.comment), 200)
        self.assertTrue(operation.comment.endswith("..."))


class TestOperationType(unittest.TestCase):
    """Тестирует перечисление OperationType."""

    def test_enum_values(self):
        """Проверяет значения перечисления."""
        self.assertEqual(OperationType.INCOME.value, "доход")
        self.assertEqual(OperationType.EXPENSE.value, "расход")

    def test_enum_comparison(self):
        """Проверяет сравнение значений перечисления."""
        self.assertNotEqual(OperationType.INCOME, OperationType.EXPENSE)
        self.assertEqual(OperationType.INCOME, OperationType.INCOME)

    def test_enum_from_string(self):
        """Проверяет создание enum из строки."""
        income_from_str = OperationType("доход")
        expense_from_str = OperationType("расход")

        self.assertEqual(income_from_str, OperationType.INCOME)
        self.assertEqual(expense_from_str, OperationType.EXPENSE)

    def test_enum_invalid_string(self):
        """Проверяет обработку неверной строки."""
        with self.assertRaises(ValueError):
            OperationType("неправильный_тип")


# Дополнительные тесты для проверки взаимодействия классов
class TestModelsIntegration(unittest.TestCase):
    """Тестирует взаимодействие между классами."""

    def test_operation_with_multiple_categories(self):
        """Проверяет создание операций с разными категориями."""
        categories = [
            Category(name="Продукты"),
            Category(name="Транспорт"),
            Category(name="Развлечения")
        ]

        for i, category in enumerate(categories):
            operation = Operation(
                amount=100 * (i + 1),
                type=OperationType.EXPENSE,
                category=category,
                comment=f"Тест {category.name}"
            )

            self.assertEqual(operation.category.name, category.name)
            self.assertIsInstance(operation.category, Category)

    def test_category_state_change(self):
        """Проверяет изменение состояния категории."""
        category = Category(name="Тест", is_active=True)
        operation = Operation(
            amount=100,
            type=OperationType.EXPENSE,
            category=category
        )

        # Меняем состояние категории
        category.is_active = False
        self.assertFalse(category.is_active)

        # Операция всё ещё должна ссылаться на ту же категорию
        self.assertEqual(operation.category, category)
        self.assertFalse(operation.category.is_active)


if __name__ == "__main__":
    # Запуск всех тестов
    unittest.main(verbosity=2)