"""
Модели данных для финансового трекера
Классы для представления операций и категорий
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class OperationType(Enum):
    """Типы финансовых операций"""
    INCOME = "доход"
    EXPENSE = "расход"


@dataclass
class Category:
    """Категория для группировки операций"""

    id: Optional[int] = None
    name: str = ""
    description: str = ""
    is_active: bool = True

    def __post_init__(self):
        """Проверка данных при создании"""
        self.name = self.name.strip()
        if not self.name:
            raise ValueError("Название категории обязательно")
        if len(self.name) > 50:
            self.name = self.name[:50]

    def __str__(self):
        return self.name

    @classmethod
    def default_expense(cls) -> 'Category':
        """Создаёт категорию по умолчанию для расходов"""
        return cls(name="Разное", description="Прочие расходы")

    @classmethod
    def default_income(cls) -> 'Category':
        """Создаёт категорию по умолчанию для доходов"""
        return cls(name="Прочие доходы")


@dataclass
class Operation:
    """Финансовая операция (доход или расход)"""

    amount: float
    type: OperationType = OperationType.EXPENSE
    category: Optional[Category] = None
    date: datetime = field(default_factory=datetime.now)
    comment: str = ""
    id: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Настройка после создания объекта"""
        # Проверяем сумму
        if self.amount <= 0:
            raise ValueError(f"Некорректная сумма: {self.amount}")

        # Устанавливаем категорию по умолчанию если не указана
        if self.category is None:
            if self.type == OperationType.INCOME:
                self.category = Category.default_income()
            else:
                self.category = Category.default_expense()

        # Обрезаем длинный комментарий
        if len(self.comment) > 200:
            self.comment = self.comment[:197] + "..."

    def update(self, **kwargs):
        """Обновление полей операции"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.now()

    @property
    def signed_amount(self) -> float:
        """Возвращает сумму со знаком (+ для доходов, - для расходов)"""
        if self.type == OperationType.INCOME:
            return self.amount
        return -self.amount

    @property
    def formatted_amount(self) -> str:
        """Отформатированная сумма со знаком"""
        sign = "+" if self.type == OperationType.INCOME else "-"
        return f"{sign}{self.amount:.2f} ₽"

    def to_dict(self) -> dict:
        """Преобразование в словарь для сериализации"""
        return {
            "id": self.id,
            "amount": self.amount,
            "type": self.type.value,
            "category": self.category.name if self.category else "",
            "date": self.date.strftime("%Y-%m-%d"),
            "comment": self.comment,
            "formatted_amount": self.formatted_amount
        }

    def __repr__(self):
        """Краткое строковое представление"""
        date_str = self.date.strftime("%d.%m.%Y")
        return f"Операция({date_str}, {self.category.name}, {self.formatted_amount})"


# Тестовые примеры
if __name__ == "__main__":
    # Простые тесты без лишних комментариев
    cat1 = Category(name="Продукты", description="Еда")
    print(f"Категория: {cat1}")

    # Расход
    op1 = Operation(
        amount=1500.50,
        type=OperationType.EXPENSE,
        category=cat1,
        comment="Покупка продуктов"
    )
    print(f"Расход: {op1}")
    print(f"Данные: {op1.to_dict()}")

    # Доход
    cat2 = Category(name="Зарплата")
    op2 = Operation(
        amount=50000,
        type=OperationType.INCOME,
        category=cat2
    )
    print(f"\nДоход: {op2}")
    print(f"Сумма со знаком: {op2.signed_amount}")

    # Операция без категории
    op3 = Operation(amount=300, comment="Наличные")
    print(f"\nОперация без явной категории: {op3}")

    # Обновление операции
    op1.update(amount=2000, comment="Больше продуктов")
    print(f"\nПосле обновления: {op1.comment}")