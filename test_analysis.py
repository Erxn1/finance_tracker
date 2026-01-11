"""
Модуль test_analysis.py
Unit-тесты для проверки функций анализа данных из analysis.py.
"""

import unittest
import pandas as pd
from datetime import datetime
from models import Operation, OperationType, Category
from analysis import (
    operations_to_dataframe,
    analyze_expenses_by_category,
    analyze_income_vs_expenses_over_time,
    calculate_balance_statistics
)


class TestAnalysisFunctions(unittest.TestCase):
    """Тестирует функции анализа данных."""

    def setUp(self):
        """Подготовка тестовых данных."""
        # Создаём тестовые категории
        self.food_category = Category(name="Продукты", id=1)
        self.transport_category = Category(name="Транспорт", id=2)
        self.salary_category = Category(name="Зарплата", id=3)
        self.entertainment_category = Category(name="Развлечения", id=4)

        # Создаём тестовые операции
        self.test_operations = [
            # Расходы
            Operation(
                amount=1500.50,
                type=OperationType.EXPENSE,
                category=self.food_category,
                date=datetime(2024, 5, 10),
                comment="Супермаркет"
            ),
            Operation(
                amount=500.00,
                type=OperationType.EXPENSE,
                category=self.transport_category,
                date=datetime(2024, 5, 12),
                comment="Такси"
            ),
            Operation(
                amount=2000.00,
                type=OperationType.EXPENSE,
                category=self.food_category,
                date=datetime(2024, 5, 15),
                comment="Ресторан"
            ),
            Operation(
                amount=1000.00,
                type=OperationType.EXPENSE,
                category=self.entertainment_category,
                date=datetime(2024, 5, 20),
                comment="Кино"
            ),

            # Доходы
            Operation(
                amount=75000.00,
                type=OperationType.INCOME,
                category=self.salary_category,
                date=datetime(2024, 5, 25),
                comment="Аванс"
            ),
            Operation(
                amount=10000.00,
                type=OperationType.INCOME,
                category=self.salary_category,
                date=datetime(2024, 5, 28),
                comment="Премия"
            )
        ]

    def test_operations_to_dataframe_empty(self):
        """Проверяет преобразование пустого списка операций."""
        df = operations_to_dataframe([])
        self.assertTrue(df.empty)
        self.assertEqual(len(df), 0)
        self.assertListEqual(list(df.columns),
                             ['date', 'type', 'category', 'amount', 'comment', 'category_id'])

    def test_operations_to_dataframe_correctness(self):
        """Проверяет корректность преобразования операций в DataFrame."""
        df = operations_to_dataframe(self.test_operations)

        # Проверяем размерность
        self.assertEqual(len(df), len(self.test_operations))

        # Проверяем колонки
        expected_columns = ['date', 'type', 'category', 'amount', 'comment', 'category_id']
        self.assertListEqual(list(df.columns), expected_columns)

        # Проверяем типы данных
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(df['date']))
        self.assertEqual(df['type'].dtype, object)
        self.assertEqual(df['category'].dtype, object)
        self.assertTrue(pd.api.types.is_float_dtype(df['amount']))

        # Проверяем данные
        self.assertEqual(df['type'].iloc[0], 'расход')
        self.assertEqual(df['type'].iloc[4], 'доход')
        self.assertEqual(df['category'].iloc[0], 'Продукты')
        self.assertEqual(df['amount'].iloc[0], 1500.50)

    def test_analyze_expenses_by_category_empty(self):
        """Проверяет анализ пустого списка операций."""
        result = analyze_expenses_by_category([])
        self.assertEqual(result, {})

    def test_analyze_expenses_by_category_only_income(self):
        """Проверяет анализ, когда есть только доходы."""
        income_only = [op for op in self.test_operations if op.type == OperationType.INCOME]
        result = analyze_expenses_by_category(income_only)
        self.assertEqual(result, {})

    def test_analyze_expenses_by_category_correctness(self):
        """Проверяет корректность анализа расходов по категориям."""
        result = analyze_expenses_by_category(self.test_operations)

        # Проверяем структуру результата
        self.assertIsInstance(result, dict)

        # Проверяем, что только расходы попали в анализ
        expected_categories = {"Продукты", "Транспорт", "Развлечения"}
        self.assertEqual(set(result.keys()), expected_categories)

        # Проверяем суммы
        # Продукты: 1500.50 + 2000.00 = 3500.50
        # Транспорт: 500.00
        # Развлечения: 1000.00
        self.assertAlmostEqual(result["Продукты"], 3500.50)
        self.assertAlmostEqual(result["Транспорт"], 500.00)
        self.assertAlmostEqual(result["Развлечения"], 1000.00)

        # Проверяем, что доходы не попали в результат
        self.assertNotIn("Зарплата", result)

    def test_analyze_expenses_by_category_single_category(self):
        """Проверяет анализ с одной категорией расходов."""
        # Создаём операции только с одной категорией
        single_category_ops = [
            op for op in self.test_operations
            if op.type == OperationType.EXPENSE and op.category.name == "Продукты"
        ]

        result = analyze_expenses_by_category(single_category_ops)

        self.assertEqual(len(result), 1)
        self.assertIn("Продукты", result)
        self.assertAlmostEqual(result["Продукты"], 3500.50)

    def test_analyze_income_vs_expenses_over_time_empty(self):
        """Проверяет анализ пустого списка операций."""
        result = analyze_income_vs_expenses_over_time([])
        self.assertEqual(result, {})

    def test_analyze_income_vs_expenses_over_time_default_period(self):
        """Проверяет анализ по умолчанию (по месяцам)."""
        result = analyze_income_vs_expenses_over_time(self.test_operations)

        self.assertIsInstance(result, dict)
        self.assertGreater(len(result), 0)

        # Проверяем структуру каждой записи
        for date_key, values in result.items():
            self.assertIsInstance(date_key, str)
            self.assertIsInstance(values, dict)
            self.assertIn('income', values)
            self.assertIn('expense', values)

    def test_analyze_income_vs_expenses_over_time_daily(self):
        """Проверяет анализ по дням."""
        result = analyze_income_vs_expenses_over_time(self.test_operations, period='D')

        # Должно быть 6 уникальных дат (по одной операции в день)
        self.assertEqual(len(result), 6)

    def test_analyze_income_vs_expenses_over_time_correctness(self):
        """Проверяет корректность расчётов доходов и расходов."""
        # Тестируем с операциями только за один день
        same_day_operations = [
            Operation(amount=1000, type=OperationType.INCOME,
                      category=self.salary_category, date=datetime(2024, 5, 10)),
            Operation(amount=500, type=OperationType.EXPENSE,
                      category=self.food_category, date=datetime(2024, 5, 10)),
            Operation(amount=300, type=OperationType.EXPENSE,
                      category=self.transport_category, date=datetime(2024, 5, 10))
        ]

        result = analyze_income_vs_expenses_over_time(same_day_operations, period='D')

        self.assertEqual(len(result), 1)

        date_key = "2024-05-10"
        self.assertIn(date_key, result)

        daily_data = result[date_key]
        self.assertAlmostEqual(daily_data['income'], 1000.00)
        self.assertAlmostEqual(daily_data['expense'], 800.00)  # 500 + 300

    def test_calculate_balance_statistics_empty(self):
        """Проверяет статистику для пустого списка операций."""
        result = calculate_balance_statistics([])

        expected_keys = ['total_income', 'total_expense', 'balance',
                         'avg_monthly_income', 'avg_monthly_expense', 'top_expense_categories']

        for key in expected_keys:
            self.assertIn(key, result)

        # Все значения должны быть нулевыми
        self.assertEqual(result['total_income'], 0)
        self.assertEqual(result['total_expense'], 0)
        self.assertEqual(result['balance'], 0)
        self.assertEqual(result['avg_monthly_income'], 0)
        self.assertEqual(result['avg_monthly_expense'], 0)
        self.assertEqual(result['top_expense_categories'], {})

    def test_calculate_balance_statistics_correctness(self):
        """Проверяет корректность расчёта статистики баланса."""
        result = calculate_balance_statistics(self.test_operations)

        # Проверяем ключи
        expected_keys = ['total_income', 'total_expense', 'balance',
                         'avg_monthly_income', 'avg_monthly_expense', 'top_expense_categories']
        for key in expected_keys:
            self.assertIn(key, result)

        # Проверяем вычисления
        # Общий доход: 75000 + 10000 = 85000
        # Общий расход: 1500.50 + 500 + 2000 + 1000 = 5000.50
        # Баланс: 85000 - 5000.50 = 79999.50
        self.assertAlmostEqual(result['total_income'], 85000.00)
        self.assertAlmostEqual(result['total_expense'], 5000.50)
        self.assertAlmostEqual(result['balance'], 79999.50)

        # Проверяем топ категорий расходов
        top_categories = result['top_expense_categories']
        self.assertIsInstance(top_categories, dict)
        self.assertIn('Продукты', top_categories)
        self.assertAlmostEqual(top_categories['Продукты'], 3500.50)

    def test_calculate_balance_statistics_only_income(self):
        """Проверяет статистику, когда есть только доходы."""
        income_only = [op for op in self.test_operations if op.type == OperationType.INCOME]
        result = calculate_balance_statistics(income_only)

        self.assertAlmostEqual(result['total_income'], 85000.00)
        self.assertAlmostEqual(result['total_expense'], 0)
        self.assertAlmostEqual(result['balance'], 85000.00)
        self.assertEqual(result['top_expense_categories'], {})

    def test_calculate_balance_statistics_only_expense(self):
        """Проверяет статистику, когда есть только расходы."""
        expense_only = [op for op in self.test_operations if op.type == OperationType.EXPENSE]
        result = calculate_balance_statistics(expense_only)

        self.assertAlmostEqual(result['total_income'], 0)
        self.assertAlmostEqual(result['total_expense'], 5000.50)
        self.assertAlmostEqual(result['balance'], -5000.50)

        # Проверяем топ категорий
        top_categories = result['top_expense_categories']
        self.assertEqual(len(top_categories), 3)  # 3 категории расходов
        self.assertIn('Продукты', top_categories)


class TestAnalysisEdgeCases(unittest.TestCase):
    """Тестирует крайние случаи в функциях анализа."""

    def setUp(self):
        """Подготовка тестовых данных."""
        self.category = Category(name="Большие суммы", id=1)

    def test_large_amounts(self):
        """Проверяет работу с большими суммами."""
        operations = [
            Operation(amount=10 ** 6, type=OperationType.INCOME,
                      category=self.category, date=datetime(2024, 1, 1)),
            Operation(amount=999999.99, type=OperationType.EXPENSE,
                      category=self.category, date=datetime(2024, 1, 1))
        ]

        df = operations_to_dataframe(operations)
        self.assertEqual(len(df), 2)
        self.assertAlmostEqual(df['amount'].iloc[0], 10 ** 6)

        stats = calculate_balance_statistics(operations)
        self.assertAlmostEqual(stats['balance'], 0.01)  # 1000000 - 999999.99

    def test_many_categories(self):
        """Проверяет работу с большим количеством категорий."""
        operations = []

        # Создаём 50 различных категорий
        for i in range(50):
            category = Category(name=f"Категория_{i}", id=i)
            operation = Operation(
                amount=100 + i,
                type=OperationType.EXPENSE,
                category=category,
                date=datetime(2024, 5, 1)
            )
            operations.append(operation)

        result = analyze_expenses_by_category(operations)
        self.assertEqual(len(result), 50)

        # Проверяем, что все категории присутствуют
        for i in range(50):
            self.assertIn(f"Категория_{i}", result)
            self.assertAlmostEqual(result[f"Категория_{i}"], 100 + i)

    def test_dates_in_different_years(self):
        """Проверяет анализ операций за разные годы."""
        operations = [
            Operation(amount=1000, type=OperationType.INCOME,
                      category=Category(name="Зарплата", id=1),
                      date=datetime(2023, 12, 31)),
            Operation(amount=500, type=OperationType.EXPENSE,
                      category=Category(name="Продукты", id=2),
                      date=datetime(2024, 1, 1))
        ]

        result = analyze_income_vs_expenses_over_time(operations, period='ME')

        # Должно быть 2 месяца в результатах
        self.assertGreaterEqual(len(result), 2)

    def test_operations_with_missing_data(self):
        """Проверяет обработку операций с неполными данными."""
        # Операция без комментария
        operation = Operation(
            amount=100,
            type=OperationType.EXPENSE,
            category=self.category,
            date=datetime(2024, 1, 1),
            comment=""
        )

        df = operations_to_dataframe([operation])
        self.assertEqual(len(df), 1)
        self.assertEqual(df['comment'].iloc[0], "")

    def test_negative_balance(self):
        """Проверяет расчёт отрицательного баланса."""
        operations = [
            Operation(amount=500, type=OperationType.EXPENSE,
                      category=self.category, date=datetime(2024, 1, 1)),
            Operation(amount=300, type=OperationType.EXPENSE,
                      category=self.category, date=datetime(2024, 1, 2))
        ]

        stats = calculate_balance_statistics(operations)
        self.assertEqual(stats['total_income'], 0)
        self.assertEqual(stats['total_expense'], 800)
        self.assertEqual(stats['balance'], -800)

    def test_same_category_different_names(self):
        """Проверяет обработку категорий с одинаковыми именами."""
        category1 = Category(name="Категория", id=1)
        category2 = Category(name="Категория", id=2)  # То же имя, другой ID

        operations = [
            Operation(amount=100, type=OperationType.EXPENSE,
                      category=category1, date=datetime(2024, 1, 1)),
            Operation(amount=200, type=OperationType.EXPENSE,
                      category=category2, date=datetime(2024, 1, 2))
        ]

        result = analyze_expenses_by_category(operations)
        # Должны объединиться по имени
        self.assertEqual(len(result), 1)
        self.assertIn("Категория", result)
        self.assertEqual(result["Категория"], 300)


if __name__ == "__main__":
    # Запуск с подробным выводом
    unittest.main(verbosity=2)