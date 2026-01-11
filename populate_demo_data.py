"""
Модуль populate_demo_data.py
Скрипт для заполнения базы данных демонстрационными данными.
Запускается один раз для инициализации реалистичных данных для тестирования.
"""

import sys
import os
from datetime import datetime, timedelta
import random

# Добавляем текущую директорию в путь, чтобы импортировать наши модули
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models import Operation, OperationType, Category
from database import DatabaseManager


def generate_demo_categories():
    """Генерирует список демонстрационных категорий."""
    return [
        # Доходы
        Category(name="Зарплата", description="Основная заработная плата"),
        Category(name="Фриланс", description="Внешние проекты и подработки"),
        Category(name="Инвестиции", description="Дивиденды и проценты"),
        Category(name="Подарки", description="Денежные подарки"),
        Category(name="Возврат долга", description="Возвращённые друзьям деньги"),

        # Расходы
        Category(name="Продукты", description="Еда и напитки"),
        Category(name="Кафе и рестораны", description="Питание вне дома"),
        Category(name="Транспорт", description="Общественный транспорт, такси, бензин"),
        Category(name="Коммунальные услуги", description="Квартплата, электричество, вода, интернет"),
        Category(name="Развлечения", description="Кино, концерты, игры"),
        Category(name="Одежда", description="Одежда и обувь"),
        Category(name="Здоровье", description="Аптека, врачи, спортзал"),
        Category(name="Образование", description="Курсы, книги"),
        Category(name="Подарки", description="Подарки для друзей и семьи"),
        Category(name="Техника", description="Электроника и гаджеты"),
        Category(name="Кредит", description="Ежемесячный платеж по кредиту"),
        Category(name="Прочее", description="Прочие расходы"),
    ]


def generate_demo_operations(categories, num_operations=100):
    """
    Генерирует список демонстрационных операций.

    Args:
        categories: список объектов Category
        num_operations: количество операций для генерации
    """
    operations = []

    # Разделяем категории на доходы и расходы
    income_categories = [c for c in categories if
                         c.name in ["Зарплата", "Фриланс", "Инвестиции", "Подарки", "Возврат долга"]]
    expense_categories = [c for c in categories if c.name not in [ic.name for ic in income_categories]]

    # Устанавливаем период для генерации данных (последние 3 месяца)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)

    for i in range(num_operations):
        # Случайно выбираем тип операции (с большей вероятностью расходов, как в реальной жизни)
        if random.random() < 0.7:  # 70% расходов
            op_type = OperationType.EXPENSE
            category = random.choice(expense_categories)

            # Генерируем сумму расхода в зависимости от категории
            if category.name == "Продукты":
                amount = round(random.uniform(200, 3000), 2)
            elif category.name == "Кафе и рестораны":
                amount = round(random.uniform(300, 2000), 2)
            elif category.name == "Транспорт":
                amount = round(random.uniform(50, 1500), 2)
            elif category.name == "Коммунальные услуги":
                amount = round(random.uniform(2000, 10000), 2)
            elif category.name == "Кредит":
                amount = round(random.uniform(5000, 30000), 2)
            elif category.name == "Техника":
                amount = round(random.uniform(1000, 50000), 2)
            else:
                amount = round(random.uniform(100, 5000), 2)

            # Комментарии для расходов
            comments = [
                f"Покупка {category.name.lower()}",
                f"Оплата {category.name.lower()}",
                f"Ежемесячный платеж за {category.name.lower()}",
                f"Расход на {category.name.lower()}",
                ""
            ]
            comment = random.choice(comments)

        else:  # 30% доходов
            op_type = OperationType.INCOME
            category = random.choice(income_categories)

            # Генерируем сумму дохода в зависимости от категории
            if category.name == "Зарплата":
                amount = round(random.uniform(50000, 150000), 2)
            elif category.name == "Фриланс":
                amount = round(random.uniform(5000, 50000), 2)
            elif category.name == "Инвестиции":
                amount = round(random.uniform(1000, 20000), 2)
            else:
                amount = round(random.uniform(1000, 10000), 2)

            # Комментарии для доходов
            comments = [
                f"Получение {category.name.lower()}",
                f"Оплата за проект",
                f"Ежемесячный {category.name.lower()}",
                f"Доход от {category.name.lower()}",
                ""
            ]
            comment = random.choice(comments)

        # Генерируем случайную дату в пределах периода
        days_diff = (end_date - start_date).days
        random_days = random.randint(0, days_diff)
        random_hours = random.randint(0, 23)
        random_minutes = random.randint(0, 59)

        operation_date = start_date + timedelta(days=random_days, hours=random_hours, minutes=random_minutes)

        # Создаём операцию
        operation = Operation(
            amount=amount,
            type=op_type,
            category=category,
            date=operation_date,
            comment=comment
        )

        operations.append(operation)

    return operations


def main():
    """Основная функция для заполнения базы данных демо-данными."""
    print("=" * 60)
    print("Генератор демонстрационных данных для Финансового Трекера")
    print("=" * 60)

    # Инициализируем менеджер базы данных
    db = DatabaseManager()

    # Запрашиваем подтверждение у пользователя
    response = input(
        "\nЭто действие удалит все существующие данные и создаст демонстрационные.\nПродолжить? (да/нет): ")

    if response.lower() not in ['да', 'yes', 'y', 'д']:
        print("Операция отменена.")
        return

    try:
        # Очищаем существующие данные
        print("\nОчистка существующих данных...")
        with db.get_cursor() as cursor:
            cursor.execute("DELETE FROM operations")
            cursor.execute("DELETE FROM categories")
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='operations' OR name='categories'")
        db._connection.commit()

        # Создаём демонстрационные категории
        print("Создание демонстрационных категорий...")
        categories = generate_demo_categories()
        for category in categories:
            db.save_category(category)

        print(f"Создано {len(categories)} категорий")

        # Создаём демонстрационные операции
        print("Создание демонстрационных операций...")
        operations = generate_demo_operations(categories, num_operations=150)

        for i, operation in enumerate(operations):
            db.save_operation(operation)
            # Выводим прогресс
            if (i + 1) % 20 == 0:
                print(f"  Добавлено {i + 1} операций...")

        print(f"Создано {len(operations)} операций")

        # Рассчитываем и выводим итоговую статистику
        print("\n" + "=" * 60)
        print("ИТОГОВАЯ СТАТИСТИКА:")
        print("=" * 60)

        balance = db.get_balance()
        print(f"Общий доход: {balance['доход']:,.2f} ₽")
        print(f"Общий расход: {balance['расход']:,.2f} ₽")
        print(f"Текущий баланс: {balance['баланс']:,.2f} ₽")

        # Получаем все операции для детальной статистики
        all_ops = db.get_all_operations()
        income_ops = [op for op in all_ops if op.type == OperationType.INCOME]
        expense_ops = [op for op in all_ops if op.type == OperationType.EXPENSE]

        print(f"\nКоличество доходных операций: {len(income_ops)}")
        print(f"Количество расходных операций: {len(expense_ops)}")

        # Анализ по категориям расходов
        print("\nТоп-5 категорий по расходам:")
        expense_by_category = {}
        for op in expense_ops:
            cat_name = op.category.name
            expense_by_category[cat_name] = expense_by_category.get(cat_name, 0) + op.amount

        sorted_categories = sorted(expense_by_category.items(), key=lambda x: x[1], reverse=True)
        for i, (cat_name, amount) in enumerate(sorted_categories[:5]):
            percentage = (amount / balance['расход'] * 100) if balance['расход'] > 0 else 0
            print(f"  {i + 1}. {cat_name}: {amount:,.2f} ₽ ({percentage:.1f}%)")

        print("\n" + "=" * 60)
        print("Демонстрационные данные успешно созданы!")
        print("Запустите приложение (python main.py) для работы с данными.")
        print("=" * 60)

    except Exception as e:
        print(f"\nОшибка при создании демонстрационных данных: {str(e)}")
    finally:
        db.close()


if __name__ == "__main__":
    main()