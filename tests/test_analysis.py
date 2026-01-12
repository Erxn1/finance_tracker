"""
Тесты для модуля анализа данных
"""

import unittest
from datetime import datetime, timedelta
from models import Category, Operation, OperationType
from analysis import (
    get_category_stats,
    get_monthly_stats,
    get_financial_summary,
    get_recent_operations
)


class TestAnalysis(unittest.TestCase):
    """Тесты для функций анализа"""

    def setUp(self):
        """Создание тестовых данных"""
        self.categories = {
            "salary": Category(name="Зарплата"),
            "food": Category(name="Еда"),
            "transport": Category(name="Транспорт"),
            "entertainment": Category(name="Развлечения")
        }

        # Создаем тестовые операции
        self.operations = []

        # Доходы
        self.operations.append(Operation(
            amount=50000,
            type=OperationType.INCOME,
            category=self.categories["salary"],
            date=datetime(2024, 1, 15)
        ))

        self.operations.append(Operation(
            amount=10000,
            type=OperationType.INCOME,
            category=self.categories["salary"],
            date=datetime(2024, 2, 15)
        ))

        # Расходы
        self.operations.append(Operation(
            amount=1500,
            type=OperationType.EXPENSE,
            category=self.categories["food"],
            date=datetime(2024, 1, 10),
            comment="Продукты"
        ))

        self.operations.append(Operation(
            amount=2000,
            type=OperationType.EXPENSE,
            category=self.categories["food"],
            date=datetime(2024, 1, 20),
            comment="Ресторан"
        ))

        self.operations.append(Operation(
            amount=500,
            type=OperationType.EXPENSE,
            category=self.categories["transport"],
            date=datetime(2024, 1, 5),
            comment="Такси"
        ))

        self.operations.append(Operation(
            amount=3000,
            type=OperationType.EXPENSE,
            category=self.categories["entertainment"],
            date=datetime(2024, 2, 1),
            comment="Кино"
        ))

    def test_category_stats(self):
        """Статистика по категориям расходов"""
        stats = get_category_stats(self.operations)

        # Проверяем наличие всех категорий расходов
        self.assertIn("Еда", stats)
        self.assertIn("Транспорт", stats)
        self.assertIn("Развлечения", stats)

        # Проверяем суммы
        self.assertEqual(stats["Еда"], 3500)  # 1500 + 2000
        self.assertEqual(stats["Транспорт"], 500)
        self.assertEqual(stats["Развлечения"], 3000)

        # Проверяем сортировку (по убыванию суммы)
        # Еда: 3500, Развлечения: 3000, Транспорт: 500
        categories = list(stats.keys())
        self.assertEqual(categories[0], "Еда")  # 3500 - самая большая
        self.assertEqual(categories[1], "Развлечения")  # 3000
        self.assertEqual(categories[2], "Транспорт")  # 500

    def test_monthly_stats(self):
        """Статистика по месяцам"""
        stats = get_monthly_stats(self.operations)

        # Проверяем наличие месяцев
        self.assertIn("2024-01", stats)
        self.assertIn("2024-02", stats)

        # Январь
        jan_stats = stats["2024-01"]
        self.assertEqual(jan_stats["income"], 50000)
        self.assertEqual(jan_stats["expense"], 4000)  # 1500 + 2000 + 500
        self.assertEqual(jan_stats["balance"], 46000)  # 50000 - 4000

        # Февраль
        feb_stats = stats["2024-02"]
        self.assertEqual(feb_stats["income"], 10000)
        self.assertEqual(feb_stats["expense"], 3000)
        self.assertEqual(feb_stats["balance"], 7000)

    def test_financial_summary(self):
        """Сводная финансовая статистика"""
        summary = get_financial_summary(self.operations)

        # Базовые показатели
        self.assertEqual(summary["total_income"], 60000)  # 50000 + 10000
        self.assertEqual(summary["total_expense"], 7000)  # 1500 + 2000 + 500 + 3000
        self.assertEqual(summary["balance"], 53000)  # 60000 - 7000

        # Средние значения
        self.assertEqual(summary["avg_income"], 30000)  # 60000 / 2 месяца
        self.assertEqual(summary["avg_expense"], 3500)  # 7000 / 2 месяца

        # Топ категорий (только расходы)
        # В нашей реализации get_financial_summary возвращает топ-5, но у нас 3 категории
        # Значит должно вернуть все 3
        top_categories = summary["top_categories"]
        self.assertIn("Развлечения", top_categories)
        self.assertIn("Еда", top_categories)
        self.assertIn("Транспорт", top_categories)
        self.assertEqual(len(top_categories), 3)  # Все 3 категории расходов

    def test_recent_operations(self):
        """Получение недавних операций"""
        # Добавляем операцию с текущей датой
        recent_op = Operation(
            amount=1000,
            type=OperationType.EXPENSE,
            category=self.categories["food"],
            date=datetime.now()
        )
        self.operations.append(recent_op)

        recent = get_recent_operations(self.operations, days=7)

        # Должна быть только операция за последние 7 дней
        self.assertEqual(len(recent), 1)
        self.assertEqual(recent[0].amount, 1000)

    def test_empty_data(self):
        """Работа с пустыми данными"""
        empty_ops = []

        # Категории
        cat_stats = get_category_stats(empty_ops)
        self.assertEqual(cat_stats, {})

        # Месяцы
        monthly_stats = get_monthly_stats(empty_ops)
        self.assertEqual(monthly_stats, {})

        # Сводка
        summary = get_financial_summary(empty_ops)
        self.assertEqual(summary["total_income"], 0.0)
        self.assertEqual(summary["total_expense"], 0.0)
        self.assertEqual(summary["balance"], 0.0)
        self.assertEqual(summary["top_categories"], {})

        # Недавние операции
        recent = get_recent_operations(empty_ops)
        self.assertEqual(recent, [])


if __name__ == "__main__":
    unittest.main()