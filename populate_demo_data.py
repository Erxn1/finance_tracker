#!/usr/bin/env python3
"""
Простой скрипт для заполнения базы данных демонстрационными данными.
Запуск: python create_demo_data.py
"""

import sys
import os
from datetime import datetime, timedelta
import random

# Добавляем путь к модулям проекта
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models import Category, Operation, OperationType
from database import Database


def create_demo_data():
    """Создает демонстрационные данные за последние 3 месяца"""

    print("Создание демонстрационных данных...")

    # Подключаемся к базе данных
    db = Database("finance.db")

    # Создаем категории доходов
    income_cats = [
        Category(name="Зарплата"),
        Category(name="Фриланс"),
        Category(name="Инвестиции"),
    ]

    # Создаем категории расходов
    expense_cats = [
        Category(name="Продукты"),
        Category(name="Транспорт"),
        Category(name="Развлечения"),
        Category(name="Одежда"),
        Category(name="Жилье"),
    ]

    # Сохраняем все категории
    all_cats = income_cats + expense_cats
    for cat in all_cats:
        db.save_category(cat)

    print(f"Создано {len(all_cats)} категорий")

    # Генерируем данные за последние 3 месяца
    today = datetime.now()
    total_ops = 0

    for month in range(3):
        # Вычисляем год и месяц
        target_date = today - timedelta(days=30 * month)
        year = target_date.year
        month_num = target_date.month

        print(f"  Добавляем данные за {month_num:02d}.{year}...")

        # Добавляем зарплату (10-15 числа)
        salary_date = datetime(year, month_num, random.randint(10, 15))
        salary_op = Operation(
            amount=random.randint(50000, 70000),
            type=OperationType.INCOME,
            category=income_cats[0],  # Зарплата
            date=salary_date,
            comment="Заработная плата"
        )
        db.save_operation(salary_op)
        total_ops += 1

        # Добавляем продукты (4 раза в месяц)
        for _ in range(4):
            day = random.randint(1, 28)
            date = datetime(year, month_num, day)
            products_op = Operation(
                amount=random.randint(1000, 4000),
                type=OperationType.EXPENSE,
                category=expense_cats[0],  # Продукты
                date=date,
                comment="Покупка продуктов"
            )
            db.save_operation(products_op)
            total_ops += 1

        # Добавляем транспорт (2 раза в месяц)
        for _ in range(2):
            day = random.randint(1, 28)
            date = datetime(year, month_num, day)
            transport_op = Operation(
                amount=random.randint(500, 2000),
                type=OperationType.EXPENSE,
                category=expense_cats[1],  # Транспорт
                date=date,
                comment="Транспортные расходы"
            )
            db.save_operation(transport_op)
            total_ops += 1

        # Добавляем развлечения (1-2 раза в месяц)
        for _ in range(random.randint(1, 2)):
            day = random.randint(1, 28)
            date = datetime(year, month_num, day)
            fun_op = Operation(
                amount=random.randint(1500, 5000),
                type=OperationType.EXPENSE,
                category=expense_cats[2],  # Развлечения
                date=date,
                comment="Кино/ресторан"
            )
            db.save_operation(fun_op)
            total_ops += 1

    # Показываем статистику
    all_ops = db.get_all_operations()
    income, expense, balance = db.get_balance()

    print(f"\n✅ Создано {total_ops} демонстрационных операций")
    print(f"💰 Баланс: {balance:,.2f} ₽")
    print(f"📈 Доходы: {income:,.2f} ₽")
    print(f"📉 Расходы: {expense:,.2f} ₽")
    print("\nЗапустите приложение: python main.py")


if __name__ == "__main__":
    try:
        create_demo_data()
    except Exception as e:
        print(f"Ошибка: {e}")
        print("Убедитесь, что все зависимости установлены:")
        print("pip install pandas matplotlib")