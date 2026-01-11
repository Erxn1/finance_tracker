"""
Модуль models.py
Определяет основные классы данных (сущности) для приложения финансового трекера.
Используются принципы ООП и аннотации типов для ясности кода.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional  # Для указания необязательных полей


class OperationType(Enum):
    """
    Перечисление (Enum) для типов операций.
    Enum используется для безопасности: предотвращает опечатки в строках.
    Вместо строк 'income'/'expense' используем OperationType.INCOME/OperationType.EXPENSE
    """
    INCOME = "доход"  # Константа для дохода
    EXPENSE = "расход"  # Константа для расхода


@dataclass
class Category:
    """
    Класс, представляющий категорию для доходов/расходов.
    @dataclass автоматически создаёт конструктор __init__, методы __repr__ и другие.
    """
    id: Optional[int] = None  # Уникальный идентификатор, None для новой категории
    name: str = ""  # Название категории (например, "Еда", "Зарплата")
    description: str = ""  # Описание категории (необязательное поле)
    is_active: bool = True  # Флаг активности категории (можно "отключать" старые)

    def __post_init__(self):
        """Метод, вызываемый автоматически ПОСЛЕ стандартного конструктора dataclass."""
        # Валидация данных при создании объекта
        if not self.name.strip():
            raise ValueError("Название категории не может быть пустым")
        if len(self.name) > 50:
            raise ValueError("Название категории слишком длинное")


@dataclass
class Operation:
    """
    Основной класс, представляющий финансовую операцию (доход или расход).
    Содержит все поля, указанные в техническом задании.
    """
    # Основные поля операции
    id: Optional[int] = None  # Уникальный ID, None для новой операции
    amount: float = 0.0  # Сумма операции (дробное число)
    type: OperationType = OperationType.EXPENSE  # Тип из перечисления, по умолчанию расход
    category: Optional[Category] = None  # Теперь явно указываем, что может быть None
    date: datetime = field(default_factory=datetime.now)
    # Дата и время операции, по умолчанию текущие
    comment: str = ""  # Комментарий пользователя (необязательное поле)

    # Служебные поля для учёта времени создания/обновления
    created_at: datetime = field(default_factory=datetime.now, repr=False)
    updated_at: datetime = field(default_factory=datetime.now, repr=False)

    def __post_init__(self):
        """Проверка данных при создании объекта операции."""
        # Валидация суммы
        if self.amount <= 0:
            raise ValueError(f"Сумма операции должна быть положительной. Получено: {self.amount}")

        # Проверка категории - если не передана, создаём дефолтную
        if self.category is None:
            self.category = Category(name="Общее")

        # Проверка, что category - это объект класса Category
        if not isinstance(self.category, Category):
            raise TypeError(f"category должна быть объектом Category. Получено: {type(self.category)}")

        # Обрезка комментария, если он слишком длинный
        if len(self.comment) > 200:
            self.comment = self.comment[:197] + "..."  # Обрезаем и добавляем многоточие

    def update_timestamp(self):
        """Обновляет время последнего изменения операции."""
        self.updated_at = datetime.now()

    @property
    def formatted_amount(self) -> str:
        """
        Свойство (property) для форматированного отображения суммы.
        Возвращает сумму со знаком '+' для доходов и '-' для расходов.
        """
        sign = "+" if self.type == OperationType.INCOME else "-"
        return f"{sign}{self.amount:.2f}"

    def get_info(self) -> dict:
        """
        Возвращает информацию об операции в виде словаря.
        Полезно для сериализации (сохранения в JSON/CSV) или передачи в GUI.
        """
        return {
            "id": self.id,
            "amount": self.amount,
            "type": self.type.value,  # Используем .value для получения строки "доход"/"расход"
            "category": self.category.name if self.category else "",
            "date": self.date.strftime("%Y-%m-%d %H:%M"),  # Форматируем дату в строку
            "comment": self.comment,
            "formatted_amount": self.formatted_amount
        }


# Пример использования классов (для тестирования модуля)
if __name__ == "__main__":
    """
    Этот блок выполняется только при ПРЯМОМ запуске models.py,
    но не при импорте этого модуля в другие файлы.
    Полезно для быстрого тестирования функциональности.
    """

    # 1. Создаём тестовую категорию
    food_category = Category(name="Продукты", description="Покупка еды и напитков")
    print(f"Создана категория: {food_category}")

    # 2. Создаём операцию расхода
    expense_operation = Operation(
        amount=1500.50,
        type=OperationType.EXPENSE,
        category=food_category,
        comment="Покупка продуктов на неделю"
    )
    print(f"\nСоздана операция расхода: {expense_operation}")
    print(f"Форматированная сумма: {expense_operation.formatted_amount}")
    print(f"Информация в виде словаря: {expense_operation.get_info()}")

    # 3. Создаём операцию дохода
    salary_category = Category(name="Зарплата")
    income_operation = Operation(
        amount=75000.0,
        type=OperationType.INCOME,
        category=salary_category,
        date=datetime(2024, 5, 25)  # Указываем конкретную дату
    )
    print(f"\nСоздана операция дохода: {income_operation}")
    print(f"Форматированная сумма: {income_operation.formatted_amount}")

    # 4. Пример обработки ошибок
    try:
        # Попытка создать операцию с неверной суммой
        wrong_operation = Operation(amount=-100)
    except ValueError as e:
        print(f"\nОшибка валидации (как и ожидалось): {e}")

    # 5. Тест обрезки комментария
    long_comment = "Очень длинный комментарий " * 20
    test_operation = Operation(
        amount=100.0,
        category=Category(name="Тест"),
        comment=long_comment
    )
    print(f"\nДлина оригинального комментария: {len(long_comment)}")
    print(f"Длина обрезанного комментария: {len(test_operation.comment)}")
    print(f"Комментарий заканчивается на '...': {test_operation.comment.endswith('...')}")
    print(f"Первые 50 символов комментария: {test_operation.comment[:50]}")