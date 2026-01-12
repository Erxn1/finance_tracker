"""
Работа с базой данных SQLite
"""

import sqlite3
from datetime import datetime
from typing import List, Optional, Tuple
from models import Category, Operation, OperationType


class Database:
    """Управление базой данных"""

    def __init__(self, db_path: str = "finance.db"):
        self.db_path = db_path
        self.connection = None
        self._connect()

    def _connect(self):
        """Установка соединения с базой данных"""
        self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        """Создание таблиц если они не существуют"""
        cursor = self.connection.cursor()

        # Таблица категорий
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT DEFAULT '',
                is_active BOOLEAN DEFAULT 1
            )
        """)

        # Таблица операций
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS operations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL,
                type TEXT NOT NULL,
                category_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                comment TEXT DEFAULT '',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES categories(id)
            )
        """)

        # Создаем индекс для быстрого поиска по дате
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_operations_date ON operations(date)
        """)

        self.connection.commit()

    # === Работа с категориями ===

    def save_category(self, category: Category) -> int:
        """Сохранение категории"""
        cursor = self.connection.cursor()

        if category.id is None:
            cursor.execute("""
                INSERT INTO categories (name, description, is_active)
                VALUES (?, ?, ?)
            """, (category.name, category.description, 1 if category.is_active else 0))
            category.id = cursor.lastrowid
        else:
            cursor.execute("""
                UPDATE categories 
                SET name = ?, description = ?, is_active = ?
                WHERE id = ?
            """, (category.name, category.description,
                  1 if category.is_active else 0, category.id))

        self.connection.commit()
        return category.id

    def get_category(self, category_id: int) -> Optional[Category]:
        """Получение категории по ID"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM categories WHERE id = ?", (category_id,))
        row = cursor.fetchone()

        if row:
            return Category(
                id=row['id'],
                name=row['name'],
                description=row['description'],
                is_active=bool(row['is_active'])
            )
        return None

    def get_all_categories(self) -> List[Category]:
        """Получение всех категорий"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM categories ORDER BY name")

        categories = []
        for row in cursor.fetchall():
            categories.append(Category(
                id=row['id'],
                name=row['name'],
                description=row['description'],
                is_active=bool(row['is_active'])
            ))

        return categories

    # === Работа с операциями ===

    def save_operation(self, operation: Operation) -> int:
        """Сохранение операции"""
        # Сначала сохраняем категорию если нужно
        if operation.category.id is None:
            self.save_category(operation.category)

        cursor = self.connection.cursor()

        if operation.id is None:
            cursor.execute("""
                INSERT INTO operations (amount, type, category_id, date, comment)
                VALUES (?, ?, ?, ?, ?)
            """, (operation.amount, operation.type.value,
                  operation.category.id,
                  operation.date.strftime("%Y-%m-%d %H:%M:%S"),
                  operation.comment))
            operation.id = cursor.lastrowid
        else:
            cursor.execute("""
                UPDATE operations 
                SET amount = ?, type = ?, category_id = ?, date = ?, comment = ?
                WHERE id = ?
            """, (operation.amount, operation.type.value,
                  operation.category.id,
                  operation.date.strftime("%Y-%m-%d %H:%M:%S"),
                  operation.comment, operation.id))

        self.connection.commit()
        return operation.id

    def get_operation(self, operation_id: int) -> Optional[Operation]:
        """Получение операции по ID"""
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT o.*, c.name as category_name, c.description as category_description
            FROM operations o
            JOIN categories c ON o.category_id = c.id
            WHERE o.id = ?
        """, (operation_id,))

        row = cursor.fetchone()
        if row:
            date_str = row['date']
            try:
                # Пробуем ISO формат с разделителем 'T'
                op_date = datetime.fromisoformat(date_str)
            except ValueError:
                try:
                    # Пробуем формат без времени
                    op_date = datetime.strptime(date_str, "%Y-%m-%d")
                except ValueError:
                    # Пробуем наш формат с пробелом
                    op_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")

            category = Category(
                id=row['category_id'],
                name=row['category_name'],
                description=row['category_description']
            )

            return Operation(
                id=row['id'],
                amount=row['amount'],
                type=OperationType(row['type']),
                category=category,
                date=op_date,
                comment=row['comment']
            )
        return None

    def get_all_operations(self,
                           start_date: Optional[datetime] = None,
                           end_date: Optional[datetime] = None) -> List[Operation]:
        """Получение всех операций с фильтрацией по дате"""
        cursor = self.connection.cursor()

        query = """
            SELECT o.*, c.name as category_name, c.description as category_description
            FROM operations o
            JOIN categories c ON o.category_id = c.id
        """
        params = []

        if start_date or end_date:
            query += " WHERE "
            conditions = []
            if start_date:
                conditions.append("date(o.date) >= date(?)")
                params.append(start_date.strftime("%Y-%m-%d"))
            if end_date:
                conditions.append("date(o.date) <= date(?)")
                params.append(end_date.strftime("%Y-%m-%d"))
            query += " AND ".join(conditions)

        query += " ORDER BY o.date DESC"
        cursor.execute(query, params)

        operations = []
        for row in cursor.fetchall():
            date_str = row['date']
            try:
                # Пробуем ISO формат с разделителем 'T'
                op_date = datetime.fromisoformat(date_str)
            except ValueError:
                try:
                    # Пробуем формат без времени
                    op_date = datetime.strptime(date_str, "%Y-%m-%d")
                except ValueError:
                    # Пробуем наш формат с пробелом
                    op_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")

            category = Category(
                id=row['category_id'],
                name=row['category_name'],
                description=row['category_description']
            )

            operations.append(Operation(
                id=row['id'],
                amount=row['amount'],
                type=OperationType(row['type']),
                category=category,
                date=op_date,
                comment=row['comment']
            ))

        return operations

    def delete_operation(self, operation_id: int) -> bool:
        """Удаление операции"""
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM operations WHERE id = ?", (operation_id,))
        self.connection.commit()
        return cursor.rowcount > 0

    def get_balance(self) -> Tuple[float, float, float]:
        """Получение баланса: доходы, расходы, итог"""
        cursor = self.connection.cursor()

        cursor.execute("""
            SELECT 
                SUM(CASE WHEN type = 'доход' THEN amount ELSE 0 END) as income,
                SUM(CASE WHEN type = 'расход' THEN amount ELSE 0 END) as expense
            FROM operations
        """)

        row = cursor.fetchone()
        income = row[0] if row[0] is not None else 0.0
        expense = row[1] if row[1] is not None else 0.0

        return float(income), float(expense), float(income - expense)

    def close(self):
        """Закрытие соединения с базой"""
        if self.connection:
            self.connection.close()