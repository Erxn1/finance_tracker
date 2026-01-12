"""
Анализ финансовых данных
"""

import pandas as pd
from typing import List, Dict, Any
from datetime import datetime, date
from models import Operation, OperationType


def operations_to_df(operations: List[Operation]) -> pd.DataFrame:
    """Конвертирует список операций в DataFrame"""
    if not operations:
        return pd.DataFrame()

    data = []
    for op in operations:
        data.append({
            'date': op.date,
            'type': op.type.value,
            'category': op.category.name,
            'amount': op.amount,
            'signed_amount': op.signed_amount,
            'comment': op.comment
        })

    return pd.DataFrame(data)


def get_category_stats(operations: List[Operation]) -> Dict[str, float]:
    """Статистика расходов по категориям"""
    if not operations:
        return {}

    # Собираем расходы по категориям
    expenses = {}
    for op in operations:
        if op.type == OperationType.EXPENSE:
            cat_name = op.category.name
            expenses[cat_name] = expenses.get(cat_name, 0) + op.amount

    return dict(sorted(expenses.items(), key=lambda x: x[1], reverse=True))


def get_monthly_stats(operations: List[Operation]) -> Dict[str, Dict[str, float]]:
    """Статистика по месяцам"""
    if not operations:
        return {}

    # Группируем по месяцам
    monthly = {}
    for op in operations:
        month_key = op.date.strftime('%Y-%m')
        if month_key not in monthly:
            monthly[month_key] = {'income': 0.0, 'expense': 0.0, 'balance': 0.0}

        if op.type == OperationType.INCOME:
            monthly[month_key]['income'] += op.amount
        else:
            monthly[month_key]['expense'] += op.amount

    # Вычисляем баланс для каждого месяца
    for month in monthly:
        monthly[month]['balance'] = monthly[month]['income'] - monthly[month]['expense']

    return dict(sorted(monthly.items()))


def get_financial_summary(operations: List[Operation]) -> Dict[str, Any]:
    """Основная финансовая статистика"""
    if not operations:
        return {
            'total_income': 0.0,
            'total_expense': 0.0,
            'balance': 0.0,
            'avg_income': 0.0,
            'avg_expense': 0.0,
            'top_categories': {}
        }

    # Базовые показатели
    total_income = 0.0
    total_expense = 0.0
    monthly_income = {}
    monthly_expense = {}

    for op in operations:
        month = op.date.strftime('%Y-%m')
        if op.type == OperationType.INCOME:
            total_income += op.amount
            monthly_income[month] = monthly_income.get(month, 0) + op.amount
        else:
            total_expense += op.amount
            monthly_expense[month] = monthly_expense.get(month, 0) + op.amount

    balance = total_income - total_expense

    # Средние значения
    avg_income = total_income / len(monthly_income) if monthly_income else 0
    avg_expense = total_expense / len(monthly_expense) if monthly_expense else 0

    # Топ-5 категорий расходов
    category_expenses = get_category_stats(operations)
    top_categories = dict(list(category_expenses.items())[:5])

    return {
        'total_income': round(total_income, 2),
        'total_expense': round(total_expense, 2),
        'balance': round(balance, 2),
        'avg_income': round(avg_income, 2),
        'avg_expense': round(avg_expense, 2),
        'top_categories': top_categories
    }


def get_recent_operations(operations: List[Operation], days: int = 30) -> List[Operation]:
    """Операции за последние N дней"""
    cutoff = datetime.now().timestamp() - days * 24 * 60 * 60

    recent = []
    for op in operations:
        if op.date.timestamp() >= cutoff:
            recent.append(op)

    return sorted(recent, key=lambda x: x.date, reverse=True)[:50]  # Ограничиваем 50 записями