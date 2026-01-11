"""
Модуль database.py
Отвечает за работу с базой данных SQLite: создание, сохранение, чтение, удаление операций.
Использует паттерн Singleton для создания единственного подключения к БД.
"""

import sqlite3
from contextlib import contextmanager
from datetime import datetime
from typing import List, Optional, Dict, Any

# Импортируем наши классы из models.py
from models import Operation, OperationType, Category


class DatabaseManager:
    """
    Главный класс для управления базой данных.
    Реализует паттерн Singleton (только один экземпляр).
    """

    # Синглтон: храним единственный экземпляр класса
    _instance = None
    _connection = None
    _db_name = "finance.db"

    def __new__(cls, db_name: str = None):
        """Метод создания нового экземпляра (часть реализации Singleton)."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            if db_name:
                cls._db_name = db_name
        return cls._instance

    def __init__(self, db_name: str = None):
        """Инициализация подключения к базе данных."""
        if db_name:
            DatabaseManager._db_name = db_name

        # Если соединение уже установлено, пропускаем инициализацию
        if self._connection is not None:
            return

        self._connection = sqlite3.connect(
            DatabaseManager._db_name,
            check_same_thread=False  # Для безопасности в многопоточных приложениях
        )
        self._connection.row_factory = sqlite3.Row  # Преобразует строки в словари
        self._create_tables()

    @classmethod
    def reset_instance(cls):
        """Сбросить синглтон-экземпляр (для тестирования)."""
        if cls._connection:
            cls._connection.close()
        cls._instance = None
        cls._connection = None
        cls._db_name = "finance.db"

    def _create_tables(self):
        """
        Создаёт таблицы в базе данных, если они ещё не существуют.
        Использует SQL-транзакцию для атомарности.
        """
        sql_script = """
        -- Таблица категорий
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Таблица операций (доходы/расходы)
        CREATE TABLE IF NOT EXISTS operations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL CHECK (amount > 0),
            type TEXT NOT NULL CHECK (type IN ('доход', 'расход')),
            category_id INTEGER NOT NULL,
            date TIMESTAMP NOT NULL,
            comment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES categories (id)
                ON DELETE RESTRICT  -- Запрещаем удалять категорию, если есть операции
        );

        -- Индексы для ускорения поиска
        CREATE INDEX IF NOT EXISTS idx_operations_date ON operations(date);
        CREATE INDEX IF NOT EXISTS idx_operations_type ON operations(type);
        CREATE INDEX IF NOT EXISTS idx_operations_category ON operations(category_id);
        """

        with self._connection:
            # executemany выполняет несколько SQL-команд
            self._connection.executescript(sql_script)

    @contextmanager
    def get_cursor(self):
        """
        Контекстный менеджер для работы с курсором.
        Гарантирует закрытие курсора даже при возникновении ошибки.
        """
        cursor = self._connection.cursor()
        try:
            yield cursor
        finally:
            cursor.close()

    # ===== МЕТОДЫ ДЛЯ РАБОТЫ С КАТЕГОРИЯМИ =====

    def save_category(self, category: Category) -> int:
        """
        Сохраняет категорию в базу данных.
        Возвращает ID сохранённой категории.
        """
        sql = """
        INSERT OR REPLACE INTO categories (id, name, description, is_active)
        VALUES (?, ?, ?, ?)
        """

        # Преобразуем объект Category в кортеж для SQL-запроса
        params = (
            category.id if category.id is not None else None,
            category.name,
            category.description,
            1 if category.is_active else 0  # Преобразуем bool в int для SQLite
        )

        with self.get_cursor() as cursor:
            cursor.execute(sql, params)
            self._connection.commit()

            # Если у категории не было ID, получаем сгенерированный
            if category.id is None:
                category.id = cursor.lastrowid

        return category.id

    def get_all_categories(self, active_only: bool = True) -> List[Category]:
        """
        Возвращает список всех категорий из базы данных.

        Args:
            active_only: если True, возвращает только активные категории
        """
        sql = "SELECT * FROM categories"
        if active_only:
            sql += " WHERE is_active = 1"
        sql += " ORDER BY name"

        categories = []
        with self.get_cursor() as cursor:
            cursor.execute(sql)
            rows = cursor.fetchall()

            for row in rows:
                # Преобразуем строку БД в объект Category
                category = Category(
                    id=row['id'],
                    name=row['name'],
                    description=row['description'] or "",
                    is_active=bool(row['is_active'])
                )
                categories.append(category)

        return categories

    # ===== МЕТОДЫ ДЛЯ РАБОТЫ С ОПЕРАЦИЯМИ =====

    def save_operation(self, operation: Operation) -> int:
        """
        Сохраняет операцию в базу данных.
        Сначала сохраняет категорию (если нужно), затем саму операцию.
        """
        # 1. Сохраняем категорию (если у неё нет ID)
        if operation.category.id is None:
            self.save_category(operation.category)

        # 2. Сохраняем операцию
        sql = """
        INSERT OR REPLACE INTO operations 
            (id, amount, type, category_id, date, comment, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """

        params = (
            operation.id if operation.id is not None else None,
            operation.amount,
            operation.type.value,  # Используем .value для получения строки
            operation.category.id,
            operation.date.isoformat(),  # Преобразуем datetime в строку ISO
            operation.comment,
            datetime.now().isoformat()  # Обновляем время изменения
        )

        with self.get_cursor() as cursor:
            cursor.execute(sql, params)
            self._connection.commit()

            if operation.id is None:
                operation.id = cursor.lastrowid

        return operation.id

    def get_all_operations(
            self,
            start_date: Optional[datetime] = None,
            end_date: Optional[datetime] = None,
            operation_type: Optional[OperationType] = None,
            category_id: Optional[int] = None
    ) -> List[Operation]:
        """
        Возвращает список операций с возможностью фильтрации.

        Args:
            start_date: начальная дата для фильтрации
            end_date: конечная дата для фильтрации
            operation_type: тип операции (доход/расход)
            category_id: ID категории для фильтрации
        """
        sql = """
        SELECT o.*, c.name as category_name, c.description as category_description
        FROM operations o
        JOIN categories c ON o.category_id = c.id
        WHERE 1=1
        """
        params = []

        # Динамически добавляем условия фильтрации
        if start_date:
            sql += " AND o.date >= ?"
            params.append(start_date.isoformat())
        if end_date:
            sql += " AND o.date <= ?"
            params.append(end_date.isoformat())
        if operation_type:
            sql += " AND o.type = ?"
            params.append(operation_type.value)
        if category_id:
            sql += " AND o.category_id = ?"
            params.append(category_id)

        sql += " ORDER BY o.date DESC, o.id DESC"

        operations = []
        with self.get_cursor() as cursor:
            cursor.execute(sql, params)
            rows = cursor.fetchall()

            for row in rows:
                # Создаём объект Category из данных БД
                category = Category(
                    id=row['category_id'],
                    name=row['category_name'],
                    description=row['category_description'] or "",
                    is_active=True
                )

                # Создаём объект Operation
                operation = Operation(
                    id=row['id'],
                    amount=row['amount'],
                    type=OperationType(row['type']),  # Преобразуем строку в Enum
                    category=category,
                    date=datetime.fromisoformat(row['date']),
                    comment=row['comment'] or ""
                )
                operations.append(operation)

        return operations

    def delete_operation(self, operation_id: int) -> bool:
        """Удаляет операцию по ID. Возвращает True если удаление успешно."""
        sql = "DELETE FROM operations WHERE id = ?"

        with self.get_cursor() as cursor:
            cursor.execute(sql, (operation_id,))
            self._connection.commit()
            return cursor.rowcount > 0

    def get_balance(self) -> Dict[str, float]:
        """
        Рассчитывает текущий баланс, общие доходы и расходы.
        Использует SQL-агрегацию для эффективного расчёта.
        """
        sql = """
        SELECT 
            type,
            SUM(amount) as total
        FROM operations 
        GROUP BY type
        """

        balance = {"доход": 0.0, "расход": 0.0, "баланс": 0.0}

        with self.get_cursor() as cursor:
            cursor.execute(sql)
            rows = cursor.fetchall()

            for row in rows:
                balance[row['type']] = row['total']

            # Рассчитываем баланс
            balance["баланс"] = balance["доход"] - balance["расход"]

        return balance

    # ===== МЕТОДЫ ДЛЯ ИМПОРТА/ЭКСПОРТА =====

    def export_to_csv(self, filepath: str) -> int:
        """
        Экспортирует все операции в CSV файл.
        Возвращает количество экспортированных записей.
        """
        import csv

        operations = self.get_all_operations()

        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            # Определяем заголовки CSV
            fieldnames = ['id', 'date', 'type', 'category', 'amount', 'comment']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for op in operations:
                writer.writerow({
                    'id': op.id,
                    'date': op.date.strftime('%Y-%m-%d %H:%M'),
                    'type': op.type.value,
                    'category': op.category.name,
                    'amount': op.amount,
                    'comment': op.comment
                })

        return len(operations)

    def close(self):
        """Закрывает соединение с базой данных."""
        if self._connection:
            self._connection.close()
            self._connection = None

    def __del__(self):
        """Деструктор: автоматически закрывает соединение при удалении объекта."""
        self.close()