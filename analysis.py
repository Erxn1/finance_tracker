"""
Модуль analysis.py
Анализ финансовых данных с использованием pandas.
Исправлены ошибки с пустыми данными и устаревшей частотой 'M'.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime
from models import Operation, OperationType


def operations_to_dataframe(operations: List[Operation]) -> pd.DataFrame:
    """
    Преобразует список операций в DataFrame pandas.

    Args:
        operations: список объектов Operation

    Returns:
        DataFrame с колонками: date, type, category, amount, comment, category_id
    """
    if not operations:
        # Возвращаем пустой DataFrame с правильными колонками
        return pd.DataFrame(columns=['date', 'type', 'category', 'amount', 'comment', 'category_id'])

    data = []
    for op in operations:
        data.append({
            'date': op.date,
            'type': op.type.value,
            'category': op.category.name,
            'amount': float(op.amount),
            'comment': op.comment,
            'category_id': op.category.id if op.category.id else 0
        })

    return pd.DataFrame(data)


def analyze_expenses_by_category(operations: List[Operation]) -> Dict[str, float]:
    """
    Анализирует расходы по категориям.

    Args:
        operations: список операций

    Returns:
        Словарь {категория: сумма_расходов}
    """
    df = operations_to_dataframe(operations)

    if df.empty:
        return {}

    # Фильтруем только расходы
    if 'type' not in df.columns:
        return {}

    expenses_df = df[df['type'] == 'расход']

    if expenses_df.empty:
        return {}

    # Группируем по категориям и суммируем
    result = expenses_df.groupby('category')['amount'].sum().to_dict()

    return result


def analyze_income_vs_expenses_over_time(operations: List[Operation],
                                         period: str = 'ME') -> Dict[str, Dict[str, float]]:
    """
    Анализирует доходы и расходы по времени.

    Args:
        operations: список операций
        period: период группировки ('D' - день, 'W' - неделя, 'ME' - месяц, 'Y' - год)

    Returns:
        Словарь {дата_периода: {'income': сумма, 'expense': сумма}}
    """
    df = operations_to_dataframe(operations)

    if df.empty:
        return {}

    # Преобразуем даты в datetime
    df['date'] = pd.to_datetime(df['date'])

    # Устанавливаем дату как индекс для группировки
    df.set_index('date', inplace=True)

    # Используем 'ME' вместо устаревшего 'M'
    if period == 'M':
        period = 'ME'

    # Группируем по периоду и типу
    grouped = df.groupby([pd.Grouper(freq=period), 'type'])['amount'].sum()

    # Преобразуем в нужный формат
    result = {}
    for (period_date, op_type), amount in grouped.items():
        # Для месячной группировки показываем только месяц и год
        if period == 'ME':
            period_str = period_date.strftime('%Y-%m')
        else:
            period_str = period_date.strftime('%Y-%m-%d')

        if period_str not in result:
            result[period_str] = {'income': 0.0, 'expense': 0.0}

        result[period_str]['income' if op_type == 'доход' else 'expense'] = float(amount)

    return result


def calculate_balance_statistics(operations: List[Operation]) -> Dict[str, Any]:
    """
    Рассчитывает общую статистику по балансу.

    Args:
        operations: список операций

    Returns:
        Словарь с различными статистиками
    """
    df = operations_to_dataframe(operations)

    if df.empty:
        return {
            'total_income': 0.0,
            'total_expense': 0.0,
            'balance': 0.0,
            'avg_monthly_income': 0.0,
            'avg_monthly_expense': 0.0,
            'top_expense_categories': {}
        }

    # Общие суммы
    total_income = 0.0
    total_expense = 0.0

    if 'type' in df.columns:
        income_mask = df['type'] == 'доход'
        expense_mask = df['type'] == 'расход'

        if income_mask.any():
            total_income = float(df.loc[income_mask, 'amount'].sum())
        if expense_mask.any():
            total_expense = float(df.loc[expense_mask, 'amount'].sum())

    balance = total_income - total_expense

    # Среднемесячные значения
    avg_monthly_income = 0.0
    avg_monthly_expense = 0.0

    if not df.empty and 'date' in df.columns and 'type' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
        df['month_year'] = df['date'].dt.to_period('M')

        # Доходы по месяцам
        monthly_income = df[df['type'] == 'доход'].groupby('month_year')['amount'].sum()
        if not monthly_income.empty:
            avg_monthly_income = float(monthly_income.mean())

        # Расходы по месяцам
        monthly_expense = df[df['type'] == 'расход'].groupby('month_year')['amount'].sum()
        if not monthly_expense.empty:
            avg_monthly_expense = float(monthly_expense.mean())

    # Самые частые категории расходов
    top_expense_categories = {}
    if 'type' in df.columns and 'category' in df.columns:
        expense_df = df[df['type'] == 'расход']
        if not expense_df.empty and 'category' in expense_df.columns:
            category_totals = expense_df.groupby('category')['amount'].sum()
            top_categories = category_totals.nlargest(5)
            top_expense_categories = {k: float(v) for k, v in top_categories.to_dict().items()}

    return {
        'total_income': total_income,
        'total_expense': total_expense,
        'balance': balance,
        'avg_monthly_income': avg_monthly_income,
        'avg_monthly_expense': avg_monthly_expense,
        'top_expense_categories': top_expense_categories
    }