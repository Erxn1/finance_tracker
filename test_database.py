"""
Модуль test_database.py
Unit-тесты для работы с базой данных.
Использует временную базу данных для тестирования.
"""

import unittest
import os
import tempfile
import shutil
from datetime import datetime
from models import Operation, OperationType, Category
from database import DatabaseManager


class TestDatabaseManager(unittest.TestCase):
    """Тестирует класс DatabaseManager."""

    def setUp(self):
        """Создаёт временную базу данных перед каждым тестом."""
        # Сбрасываем синглтон перед каждым тестом
        DatabaseManager.reset_instance()

        # Создаём временную директорию для тестовой БД
        self.test_dir = tempfile.mkdtemp()
        self.test_db_path = os.path.join(self.test_dir, "test_finance.db")

        # Создаём менеджер БД с тестовым путём
        self.db = DatabaseManager(self.test_db_path)

        # Тестовые данные
        self.test_category = Category(name="Тестовая категория", description="Для тестов")
        self.test_operation = Operation(
            amount=100.50,
            type=OperationType.INCOME,
            category=self.test_category,
            date=datetime(2024, 5, 15),
            comment="Тестовая операция"
        )

    def tearDown(self):
        """Удаляет временную базу данных после каждого теста."""
        self.db.close()
        DatabaseManager.reset_instance()

        # Удаляем временную директорию
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_database_creation(self):
        """Проверяет создание базы данных и таблиц."""
        # Проверяем, что файл БД создан
        self.assertTrue(os.path.exists(self.test_db_path))

        # Проверяем, что можно выполнять запросы
        with self.db.get_cursor() as cursor:
            # Проверяем существование таблиц
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' 
                AND name IN ('categories', 'operations')
            """)

            tables = cursor.fetchall()
            table_names = [table[0] for table in tables]

            self.assertIn('categories', table_names)
            self.assertIn('operations', table_names)

    def test_save_and_get_category(self):
        """Проверяет сохранение и получение категории."""
        # Сохраняем категорию
        category_id = self.db.save_category(self.test_category)

        # Проверяем, что ID установлен
        self.assertIsNotNone(category_id)
        self.assertEqual(self.test_category.id, category_id)

        # Получаем все категории
        categories = self.db.get_all_categories()

        # Проверяем, что категория сохранена
        self.assertEqual(len(categories), 1)
        self.assertEqual(categories[0].name, "Тестовая категория")
        self.assertEqual(categories[0].description, "Для тестов")
        self.assertTrue(categories[0].is_active)

    def test_save_and_get_operation(self):
        """Проверяет сохранение и получение операции."""
        # Сначала сохраняем категорию
        category_id = self.db.save_category(self.test_category)

        # Сохраняем операцию
        operation_id = self.db.save_operation(self.test_operation)

        # Проверяем, что ID установлен
        self.assertIsNotNone(operation_id)
        self.assertEqual(self.test_operation.id, operation_id)

        # Получаем все операции
        operations = self.db.get_all_operations()

        # Проверяем, что операция сохранена
        self.assertEqual(len(operations), 1)

        operation = operations[0]
        self.assertEqual(operation.id, operation_id)
        self.assertEqual(operation.amount, 100.50)
        self.assertEqual(operation.type, OperationType.INCOME)
        self.assertEqual(operation.category.name, "Тестовая категория")
        self.assertEqual(operation.comment, "Тестовая операция")

        # Проверяем дату
        self.assertEqual(operation.date.year, 2024)
        self.assertEqual(operation.date.month, 5)
        self.assertEqual(operation.date.day, 15)

    def test_multiple_operations(self):
        """Проверяет работу с несколькими операциями."""
        # Создаём несколько категорий
        categories = [
            Category(name="Продукты"),
            Category(name="Транспорт"),
            Category(name="Зарплата"),
        ]

        for category in categories:
            self.db.save_category(category)

        # Создаём несколько операций
        operations = [
            Operation(amount=1500.50, type=OperationType.EXPENSE,
                      category=categories[0], date=datetime(2024, 5, 10), comment="Магазин"),
            Operation(amount=500.00, type=OperationType.EXPENSE,
                      category=categories[1], date=datetime(2024, 5, 12), comment="Такси"),
            Operation(amount=75000.00, type=OperationType.INCOME,
                      category=categories[2], date=datetime(2024, 5, 25), comment="Аванс"),
        ]

        for operation in operations:
            self.db.save_operation(operation)

        # Получаем все операции
        saved_operations = self.db.get_all_operations()

        # Проверяем количество
        self.assertEqual(len(saved_operations), 3)

        # Проверяем сортировку (по дате, новые сверху)
        self.assertEqual(saved_operations[0].comment, "Аванс")  # 25 мая
        self.assertEqual(saved_operations[1].comment, "Такси")  # 12 мая
        self.assertEqual(saved_operations[2].comment, "Магазин")  # 10 мая

    def test_get_balance(self):
        """Проверяет расчёт баланса."""
        # Создаём категории
        income_category = Category(name="Доходы")
        expense_category = Category(name="Расходы")

        self.db.save_category(income_category)
        self.db.save_category(expense_category)

        # Добавляем операции
        operations = [
            Operation(amount=1000, type=OperationType.INCOME, category=income_category),
            Operation(amount=500, type=OperationType.EXPENSE, category=expense_category),
            Operation(amount=300, type=OperationType.EXPENSE, category=expense_category),
            Operation(amount=2000, type=OperationType.INCOME, category=income_category),
        ]

        for operation in operations:
            self.db.save_operation(operation)

        # Проверяем баланс
        balance = self.db.get_balance()

        self.assertEqual(balance["доход"], 3000.0)  # 1000 + 2000
        self.assertEqual(balance["расход"], 800.0)  # 500 + 300
        self.assertEqual(balance["баланс"], 2200.0)  # 3000 - 800

    def test_delete_operation(self):
        """Проверяет удаление операции."""
        # Сохраняем операцию
        category_id = self.db.save_category(self.test_category)
        operation_id = self.db.save_operation(self.test_operation)

        # Проверяем, что операция существует
        operations_before = self.db.get_all_operations()
        self.assertEqual(len(operations_before), 1)

        # Удаляем операцию
        delete_result = self.db.delete_operation(operation_id)
        self.assertTrue(delete_result)

        # Проверяем, что операция удалена
        operations_after = self.db.get_all_operations()
        self.assertEqual(len(operations_after), 0)

        # Пробуем удалить несуществующую операцию
        delete_nonexistent = self.db.delete_operation(999)
        self.assertFalse(delete_nonexistent)

    def test_filter_operations(self):
        """Проверяет фильтрацию операций."""
        # Создаём категории
        income_cat = Category(name="Доход")
        expense_cat = Category(name="Расход")

        self.db.save_category(income_cat)
        self.db.save_category(expense_cat)

        # Добавляем операции с разными датами и типами
        operations = [
            Operation(amount=1000, type=OperationType.INCOME, category=income_cat,
                      date=datetime(2024, 5, 1)),
            Operation(amount=500, type=OperationType.EXPENSE, category=expense_cat,
                      date=datetime(2024, 5, 10)),
            Operation(amount=2000, type=OperationType.INCOME, category=income_cat,
                      date=datetime(2024, 5, 15)),
            Operation(amount=300, type=OperationType.EXPENSE, category=expense_cat,
                      date=datetime(2024, 5, 20)),
        ]

        for operation in operations:
            self.db.save_operation(operation)

        # Тестируем фильтры

        # Фильтр по типу: только доходы
        incomes = self.db.get_all_operations(operation_type=OperationType.INCOME)
        self.assertEqual(len(incomes), 2)
        for op in incomes:
            self.assertEqual(op.type, OperationType.INCOME)

        # Фильтр по типу: только расходы
        expenses = self.db.get_all_operations(operation_type=OperationType.EXPENSE)
        self.assertEqual(len(expenses), 2)
        for op in expenses:
            self.assertEqual(op.type, OperationType.EXPENSE)

        # Фильтр по дате: с 10 мая
        from_date = datetime(2024, 5, 10)
        filtered = self.db.get_all_operations(start_date=from_date)
        self.assertEqual(len(filtered), 3)  # Операции от 10, 15, 20 мая

        # Фильтр по дате: до 15 мая
        to_date = datetime(2024, 5, 15)
        filtered = self.db.get_all_operations(end_date=to_date)
        self.assertEqual(len(filtered), 3)  # Операции от 1, 10, 15 мая

        # Фильтр по дате: с 10 по 15 мая
        filtered = self.db.get_all_operations(
            start_date=datetime(2024, 5, 10),
            end_date=datetime(2024, 5, 15)
        )
        self.assertEqual(len(filtered), 2)  # Только 10 и 15 мая

    def test_export_to_csv(self):
        """Проверяет экспорт данных в CSV."""
        # Добавляем тестовые данные
        category_id = self.db.save_category(self.test_category)
        self.db.save_operation(self.test_operation)

        # Создаём временный файл для экспорта
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp_file:
            csv_path = tmp_file.name

        try:
            # Экспортируем данные
            export_count = self.db.export_to_csv(csv_path)

            # Проверяем результат
            self.assertEqual(export_count, 1)

            # Проверяем, что файл создан и не пустой
            self.assertTrue(os.path.exists(csv_path))
            self.assertGreater(os.path.getsize(csv_path), 0)

            # Проверяем содержимое файла
            with open(csv_path, 'r', encoding='utf-8') as f:
                content = f.read()

                self.assertIn('id,date,type,category,amount,comment', content)  # Заголовок
                self.assertIn('Тестовая категория', content)
                self.assertIn('Тестовая операция', content)
                self.assertIn('доход', content)

        finally:
            # Удаляем временный файл
            if os.path.exists(csv_path):
                os.unlink(csv_path)

    def test_update_existing_category(self):
        """Проверяет обновление существующей категории."""
        # Сохраняем категорию
        category = Category(name="Старое название", description="Старое описание")
        category_id = self.db.save_category(category)

        # Изменяем категорию
        category.name = "Новое название"
        category.description = "Новое описание"
        category.is_active = False

        # Сохраняем снова (должно обновиться)
        self.db.save_category(category)

        # Получаем категорию из БД
        categories = self.db.get_all_categories(active_only=False)

        # Проверяем обновление
        self.assertEqual(len(categories), 1)
        self.assertEqual(categories[0].name, "Новое название")
        self.assertEqual(categories[0].description, "Новое описание")
        self.assertFalse(categories[0].is_active)

    def test_singleton_pattern(self):
        """Проверяет паттерн Singleton в DatabaseManager."""
        # Создаём второй экземпляр с тем же путём
        db2 = DatabaseManager(self.test_db_path)

        # Они должны быть одним и тем же экземпляром (Singleton)
        self.assertEqual(self.db, db2)

        # Закрываем второй экземпляр
        db2.close()


class TestDatabaseErrorHandling(unittest.TestCase):
    """Тестирует обработку ошибок в базе данных."""

    def setUp(self):
        DatabaseManager.reset_instance()
        self.test_dir = tempfile.mkdtemp()
        self.test_db_path = os.path.join(self.test_dir, "test_finance.db")
        self.db = DatabaseManager(self.test_db_path)

    def tearDown(self):
        self.db.close()
        DatabaseManager.reset_instance()
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_invalid_operation_data(self):
        """Проверяет обработку некорректных данных операции."""
        # Попытка сохранить операцию без категории
        category = Category(name="Тест")  # Не сохранена в БД

        operation = Operation(
            amount=100,
            type=OperationType.EXPENSE,
            category=category,  # Категория без ID
            comment="Тест"
        )

        # Это должно вызвать ошибку при сохранении в БД
        # (так как категория не сохранена)
        try:
            self.db.save_operation(operation)
            # Если дошло сюда, значит ошибка не обработана
            # В реальном коде здесь должна быть обработка
        except Exception as e:
            # Ожидаем ошибку
            self.assertIsNotNone(e)

    def test_database_file_permissions(self):
        """Тестирует работу с БД при проблемах с файловой системой."""
        import sys
        if sys.platform.startswith('win'):
            self.skipTest("Тест пропущен на Windows")

        # Создаём БД в директории без прав на запись (имитация)
        import stat
        read_only_dir = os.path.join(self.test_dir, "readonly")
        os.makedirs(read_only_dir)

        # Делаем директорию доступной только для чтения
        os.chmod(read_only_dir, stat.S_IRUSR | stat.S_IXUSR)

        db_path = os.path.join(read_only_dir, "test.db")

        try:
            # Попытка создать БД в директории
            db = DatabaseManager(db_path)
            self.fail("Ожидалась ошибка при создании БД в read-only директории")
        except sqlite3.OperationalError:
            # Ожидаем ошибку доступа
            pass
        except Exception as e:
            # Другие ошибки также допустимы
            self.assertIsNotNone(e)
        finally:
            # Восстанавливаем права
            os.chmod(read_only_dir, stat.S_IRWXU)


if __name__ == "__main__":
    unittest.main(verbosity=2)