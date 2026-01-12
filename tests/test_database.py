"""
Тесты для работы с базой данных
"""

import unittest
import os
import tempfile
from datetime import datetime
from models import Category, Operation, OperationType
from database import Database


class TestDatabase(unittest.TestCase):
    """Тесты для работы с базой данных"""

    def setUp(self):
        """Создание временной базы данных для тестов"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")
        self.db = Database(self.db_path)

    def tearDown(self):
        """Очистка после тестов"""
        self.db.close()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        os.rmdir(self.temp_dir)

    def test_category_operations(self):
        """Работа с категориями"""
        # Создание категории
        category = Category(name="Продукты", description="Еда")
        category_id = self.db.save_category(category)

        self.assertIsNotNone(category_id)
        self.assertEqual(category.id, category_id)

        # Получение категории
        retrieved = self.db.get_category(category_id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.name, "Продукты")
        self.assertEqual(retrieved.description, "Еда")

        # Получение всех категорий
        all_categories = self.db.get_all_categories()
        self.assertEqual(len(all_categories), 1)
        self.assertEqual(all_categories[0].name, "Продукты")

    def test_operation_operations(self):
        """Работа с операциями"""
        # Создаем категорию
        category = Category(name="Зарплата")
        self.db.save_category(category)

        # Создаем операцию
        operation = Operation(
            amount=50000,
            type=OperationType.INCOME,
            category=category,
            date=datetime(2024, 1, 15),
            comment="Аванс"
        )

        operation_id = self.db.save_operation(operation)
        self.assertIsNotNone(operation_id)

        # Получение операции
        retrieved = self.db.get_operation(operation_id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.amount, 50000)
        self.assertEqual(retrieved.type, OperationType.INCOME)
        self.assertEqual(retrieved.category.name, "Зарплата")
        self.assertEqual(retrieved.comment, "Аванс")

        # Получение всех операций
        all_operations = self.db.get_all_operations()
        self.assertEqual(len(all_operations), 1)
        self.assertEqual(all_operations[0].id, operation_id)

    def test_operation_filtering(self):
        """Фильтрация операций по дате"""
        # Создаем категорию
        category = Category(name="Тест")
        self.db.save_category(category)

        # Просто создаем 3 операции
        for i in range(3):
            op = Operation(
                amount=100 * (i + 1),
                category=category,
                date=datetime(2024, 1, i + 1)  # 1, 2, 3 января
            )
            self.db.save_operation(op)

        # Получаем все операции без фильтра
        all_ops = self.db.get_all_operations()
        print(f"Все операции: {len(all_ops)}")

        # Фильтрация по периоду (1-2 января)
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 1, 2)

        filtered = self.db.get_all_operations(start_date=start_date, end_date=end_date)
        print(f"Отфильтровано: {len(filtered)}")

        # Должно быть 2 операции (1 и 2 января)
        self.assertEqual(len(filtered), 2)

    def test_balance_calculation(self):
        """Расчет баланса"""
        # Создаем категории
        salary_cat = Category(name="Зарплата")
        food_cat = Category(name="Еда")
        self.db.save_category(salary_cat)
        self.db.save_category(food_cat)

        # Добавляем операции
        operations = [
            (50000, OperationType.INCOME, salary_cat, "Зарплата"),
            (1500, OperationType.EXPENSE, food_cat, "Продукты"),
            (2000, OperationType.EXPENSE, food_cat, "Ресторан"),
            (10000, OperationType.INCOME, salary_cat, "Премия")
        ]

        for amount, op_type, category, comment in operations:
            op = Operation(
                amount=amount,
                type=op_type,
                category=category,
                date=datetime.now(),
                comment=comment
            )
            self.db.save_operation(op)

        # Проверяем баланс
        income, expense, balance = self.db.get_balance()

        self.assertEqual(income, 60000.0)  # 50000 + 10000
        self.assertEqual(expense, 3500.0)  # 1500 + 2000
        self.assertEqual(balance, 56500.0)  # 60000 - 3500

    def test_operation_deletion(self):
        """Удаление операции"""
        category = Category(name="Тест")
        self.db.save_category(category)

        operation = Operation(amount=1000, category=category)
        operation_id = self.db.save_operation(operation)

        # Удаляем операцию
        result = self.db.delete_operation(operation_id)
        self.assertTrue(result)

        # Проверяем, что операция удалена
        retrieved = self.db.get_operation(operation_id)
        self.assertIsNone(retrieved)

        # Повторное удаление должно вернуть False
        result = self.db.delete_operation(operation_id)
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()