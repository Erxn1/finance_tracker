"""
Графический интерфейс финансового трекера.
Основной класс приложения.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Импорт наших модулей
from models import Operation, OperationType, Category
from database import Database
from analysis import (
    get_category_stats,
    get_monthly_stats,
    get_financial_summary,
    get_recent_operations
)
from utils import validate_date, validate_amount, format_currency


class FinanceTrackerApp:
    """Основной класс графического интерфейса приложения."""

    def __init__(self, root):
        """Инициализация главного окна приложения."""
        self.root = root
        self.root.title("Финансовый трекер")
        self.root.geometry("1100x700")

        # Инициализация базы данных
        self.db = Database()

        # Загружаем категории и операции
        self.categories = self.db.get_all_categories()
        self.operations = []

        # Настройка стилей
        self._setup_styles()

        # Создание интерфейса
        self._create_widgets()

        # Загрузка данных
        self.refresh_data()

    def _setup_styles(self):
        """Настройка цветов и стилей виджетов."""
        self.style = ttk.Style()
        self.style.configure('Title.TLabel', font=('Arial', 14, 'bold'))
        self.style.configure('Balance.TLabel', font=('Arial', 16, 'bold'))
        self.style.configure('Accent.TButton', font=('Arial', 10))

        # Цвета
        self.colors = {
            'income': '#2ecc71',    # Зеленый
            'expense': '#e74c3c',   # Красный
            'bg_light': '#f8f9fa',
            'text_dark': '#2c3e50'
        }

    def _create_widgets(self):
        """Создание всех элементов интерфейса."""
        # Главный контейнер
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Левая панель (навигация и баланс)
        left_panel = ttk.Frame(main_container, width=200)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        # Заголовок
        title_label = ttk.Label(
            left_panel,
            text="💰 Финансовый\nТрекер",
            style='Title.TLabel'
        )
        title_label.pack(pady=(0, 20))

        # Кнопки навигации
        nav_buttons = [
            ("📝 Новая операция", self.show_add_operation),
            ("📋 Все операции", self.show_operations),
            ("📊 Аналитика", self.show_analytics),
            ("🔄 Обновить", self.refresh_data)
        ]

        for text, command in nav_buttons:
            btn = ttk.Button(
                left_panel,
                text=text,
                command=command,
                style='Accent.TButton',
                width=20
            )
            btn.pack(pady=5)

        # Отображение баланса
        self.balance_frame = ttk.LabelFrame(left_panel, text="Текущий баланс")
        self.balance_frame.pack(fill=tk.X, pady=20)

        self.balance_label = ttk.Label(
            self.balance_frame,
            text="0.00 ₽",
            style='Balance.TLabel'
        )
        self.balance_label.pack(pady=10)

        # Правая панель (основное содержимое)
        self.main_area = ttk.Frame(main_container)
        self.main_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Изначально показываем добавление операции
        self.show_add_operation()

    def refresh_data(self):
        """Обновление всех данных в интерфейсе."""
        try:
            self.categories = self.db.get_all_categories()
            self.operations = self.db.get_all_operations()
            self._update_balance()
            messagebox.showinfo("Обновлено", "Данные успешно загружены")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {str(e)}")

    def _update_balance(self):
        """Обновление отображения баланса."""
        try:
            income, expense, balance = self.db.get_balance()
            color = self.colors['income'] if balance >= 0 else self.colors['expense']
            self.balance_label.configure(
                text=f"{balance:,.2f} ₽",
                foreground=color
            )
        except Exception as e:
            self.balance_label.configure(text="Ошибка", foreground='red')

    def show_add_operation(self):
        """Показать форму добавления операции."""
        self._clear_main_area()

        title = ttk.Label(
            self.main_area,
            text="Добавить новую операцию",
            style='Title.TLabel'
        )
        title.pack(pady=20)

        # Форма
        form = ttk.Frame(self.main_area)
        form.pack(pady=10, padx=20, fill=tk.X)

        # Тип операции
        ttk.Label(form, text="Тип операции:").grid(row=0, column=0, sticky=tk.W, pady=10)
        self.op_type_var = tk.StringVar(value="расход")
        ttk.Radiobutton(form, text="Доход", variable=self.op_type_var,
                       value="доход").grid(row=0, column=1, padx=10)
        ttk.Radiobutton(form, text="Расход", variable=self.op_type_var,
                       value="расход").grid(row=0, column=2, padx=10)

        # Сумма
        ttk.Label(form, text="Сумма (₽):").grid(row=1, column=0, sticky=tk.W, pady=10)
        self.amount_entry = ttk.Entry(form, width=20)
        self.amount_entry.grid(row=1, column=1, columnspan=2, sticky=tk.W, pady=10)

        # Категория
        ttk.Label(form, text="Категория:").grid(row=2, column=0, sticky=tk.W, pady=10)
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(
            form,
            textvariable=self.category_var,
            values=[c.name for c in self.categories],
            state="readonly",
            width=18
        )
        self.category_combo.grid(row=2, column=1, columnspan=2, sticky=tk.W, pady=10)

        # Дата
        ttk.Label(form, text="Дата:").grid(row=3, column=0, sticky=tk.W, pady=10)
        self.date_entry = ttk.Entry(form, width=20)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.date_entry.grid(row=3, column=1, columnspan=2, sticky=tk.W, pady=10)

        # Комментарий
        ttk.Label(form, text="Комментарий:").grid(row=4, column=0, sticky=tk.W, pady=10)
        self.comment_text = tk.Text(form, height=3, width=30)
        self.comment_text.grid(row=4, column=1, columnspan=2, sticky=tk.W, pady=10)

        # Кнопки
        btn_frame = ttk.Frame(form)
        btn_frame.grid(row=5, column=0, columnspan=3, pady=20)

        ttk.Button(btn_frame, text="Добавить",
                   command=self._add_operation).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Очистить",
                   command=self._clear_form).pack(side=tk.LEFT, padx=5)

    def _add_operation(self):
        """Добавление новой операции в базу данных."""
        try:
            # Валидация данных
            amount_str = self.amount_entry.get().strip()
            if not validate_amount(amount_str):
                messagebox.showerror("Ошибка", "Неверная сумма")
                return

            date_str = self.date_entry.get().strip()
            if not validate_date(date_str):
                messagebox.showerror("Ошибка", "Неверная дата. Формат: ГГГГ-ММ-ДД")
                return

            # Получение или создание категории
            category_name = self.category_var.get().strip()
            if not category_name:
                messagebox.showerror("Ошибка", "Выберите категорию")
                return

            category = next((c for c in self.categories if c.name == category_name), None)
            if not category:
                category = Category(name=category_name)
                self.db.save_category(category)
                self.categories.append(category)

            # Создание операции
            operation = Operation(
                amount=float(amount_str),
                type=OperationType(self.op_type_var.get()),
                category=category,
                date=datetime.strptime(date_str, "%Y-%m-%d"),
                comment=self.comment_text.get("1.0", tk.END).strip()
            )

            # Сохранение
            self.db.save_operation(operation)

            # Обновление интерфейса
            self._clear_form()
            self.refresh_data()
            messagebox.showinfo("Успех", "Операция добавлена")

        except ValueError as e:
            messagebox.showerror("Ошибка", f"Ошибка в данных: {str(e)}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось добавить операцию: {str(e)}")

    def _clear_form(self):
        """Очистка формы ввода."""
        self.amount_entry.delete(0, tk.END)
        self.category_var.set('')
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.comment_text.delete("1.0", tk.END)

    def show_operations(self):
        """Показать список всех операций."""
        self._clear_main_area()

        title = ttk.Label(
            self.main_area,
            text="Все операции",
            style='Title.TLabel'
        )
        title.pack(pady=20)

        # Фильтры
        filter_frame = ttk.Frame(self.main_area)
        filter_frame.pack(fill=tk.X, padx=20, pady=10)

        ttk.Label(filter_frame, text="Показать:").pack(side=tk.LEFT, padx=5)
        self.filter_var = tk.StringVar(value="all")
        ttk.Radiobutton(filter_frame, text="Все", variable=self.filter_var,
                       value="all", command=self._apply_filters).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(filter_frame, text="Доходы", variable=self.filter_var,
                       value="income", command=self._apply_filters).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(filter_frame, text="Расходы", variable=self.filter_var,
                       value="expense", command=self._apply_filters).pack(side=tk.LEFT, padx=5)

        # Таблица операций
        columns = ("Дата", "Тип", "Категория", "Сумма", "Комментарий")
        self.tree = ttk.Treeview(self.main_area, columns=columns, show="headings", height=15)

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)

        # Загрузка данных
        self._load_operations_table()

        # Скроллбар
        scrollbar = ttk.Scrollbar(self.main_area, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Размещение
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(20, 0), pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 20), pady=10)

        # Кнопки управления
        btn_frame = ttk.Frame(self.main_area)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="Удалить выбранное",
                   command=self._delete_operation).pack(side=tk.LEFT, padx=5)

    def _load_operations_table(self, operations=None):
        """Загрузка операций в таблицу."""
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)

        if operations is None:
            operations = self.operations

        for op in operations:
            self.tree.insert("", tk.END, values=(
                op.date.strftime("%d.%m.%Y"),
                op.type.value,
                op.category.name,
                op.formatted_amount,
                op.comment[:50] + "..." if len(op.comment) > 50 else op.comment
            ), tags=(op.type.value,))

        # Настройка цветов
        self.tree.tag_configure('доход', foreground=self.colors['income'])
        self.tree.tag_configure('расход', foreground=self.colors['expense'])

    def _apply_filters(self):
        """Применение фильтров к таблице операций."""
        filter_type = self.filter_var.get()

        if filter_type == "all":
            filtered = self.operations
        elif filter_type == "income":
            filtered = [op for op in self.operations if op.type == OperationType.INCOME]
        else:  # expense
            filtered = [op for op in self.operations if op.type == OperationType.EXPENSE]

        self._load_operations_table(filtered)

    def _delete_operation(self):
        """Удаление выбранной операции."""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите операцию для удаления")
            return

        if messagebox.askyesno("Подтверждение", "Удалить выбранную операцию?"):
            try:
                item = self.tree.item(selection[0])
                # Поиск операции по значениям в таблице
                op_date = datetime.strptime(item['values'][0], "%d.%m.%Y").date()
                op_type = item['values'][1]
                op_amount = float(item['values'][3][1:])  # Убираем знак +/-

                # Поиск и удаление операции из БД
                for op in self.operations:
                    if (op.date.date() == op_date and
                        op.type.value == op_type and
                        op.amount == op_amount):
                        self.db.delete_operation(op.id)
                        break

                # Обновление интерфейса
                self.tree.delete(selection[0])
                self._update_balance()
                messagebox.showinfo("Успех", "Операция удалена")

            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось удалить операцию: {str(e)}")

    def show_analytics(self):
        """Показать панель аналитики."""
        self._clear_main_area()

        title = ttk.Label(
            self.main_area,
            text="Финансовая аналитика",
            style='Title.TLabel'
        )
        title.pack(pady=20)

        # Кнопки графиков
        graph_frame = ttk.Frame(self.main_area)
        graph_frame.pack(pady=10)

        ttk.Button(graph_frame, text="📊 Расходы по категориям",
                   command=self._show_category_chart).pack(side=tk.LEFT, padx=5)
        ttk.Button(graph_frame, text="📈 Доходы vs Расходы",
                   command=self._show_income_expense_chart).pack(side=tk.LEFT, padx=5)

        # Область для графиков
        self.chart_frame = ttk.Frame(self.main_area)
        self.chart_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Текстовая статистика
        self._show_summary_stats()

    def _show_category_chart(self):
        """Построение графика расходов по категориям."""
        if not self.operations:
            messagebox.showinfo("Инфо", "Нет данных для анализа")
            return

        # Очистка области
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        # Получение данных
        expenses_data = get_category_stats(self.operations)

        if not expenses_data:
            ttk.Label(self.chart_frame, text="Нет данных о расходах").pack(pady=50)
            return

        # Создание графика
        fig, ax = plt.subplots(figsize=(8, 6))
        labels = list(expenses_data.keys())
        values = list(expenses_data.values())

        colors = plt.cm.Set3(range(len(labels)))
        ax.pie(values, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90)
        ax.set_title('Распределение расходов по категориям')

        # Встраивание в Tkinter
        canvas = FigureCanvasTkAgg(fig, self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def _show_income_expense_chart(self):
        """Построение графика доходов и расходов по месяцам."""
        if not self.operations:
            messagebox.showinfo("Инфо", "Нет данных для анализа")
            return

        # Очистка области
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        # Получение данных
        monthly_data = get_monthly_stats(self.operations)

        if not monthly_data:
            ttk.Label(self.chart_frame, text="Недостаточно данных").pack(pady=50)
            return

        # Создание графика
        fig, ax = plt.subplots(figsize=(10, 6))
        months = list(monthly_data.keys())
        incomes = [monthly_data[m]['income'] for m in months]
        expenses = [monthly_data[m]['expense'] for m in months]

        x = range(len(months))
        width = 0.35

        ax.bar(x, incomes, width, label='Доходы', color=self.colors['income'])
        ax.bar([i + width for i in x], expenses, width, label='Расходы', color=self.colors['expense'])

        ax.set_xlabel('Месяц')
        ax.set_ylabel('Сумма (₽)')
        ax.set_title('Доходы и расходы по месяцам')
        ax.set_xticks([i + width/2 for i in x])
        ax.set_xticklabels(months, rotation=45, ha='right')
        ax.legend()
        ax.grid(axis='y', alpha=0.3)

        plt.tight_layout()

        # Встраивание в Tkinter
        canvas = FigureCanvasTkAgg(fig, self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def _show_summary_stats(self):
        """Отображение сводной статистики."""
        if not self.operations:
            return

        stats = get_financial_summary(self.operations)

        stats_text = tk.Text(self.main_area, height=10, width=60, font=('Arial', 10))
        stats_text.pack(pady=10, padx=20, fill=tk.X)

        stats_text.insert(tk.END, "📈 СВОДНАЯ СТАТИСТИКА\n")
        stats_text.insert(tk.END, "=" * 40 + "\n\n")
        stats_text.insert(tk.END, f"Общий доход: {stats['total_income']:,.2f} ₽\n")
        stats_text.insert(tk.END, f"Общие расходы: {stats['total_expense']:,.2f} ₽\n")
        stats_text.insert(tk.END, f"Баланс: {stats['balance']:,.2f} ₽\n\n")
        stats_text.insert(tk.END, f"Средний доход в месяц: {stats['avg_income']:,.2f} ₽\n")
        stats_text.insert(tk.END, f"Средний расход в месяц: {stats['avg_expense']:,.2f} ₽\n\n")

        if stats['top_categories']:
            stats_text.insert(tk.END, "Топ-5 категорий расходов:\n")
            for cat, amount in stats['top_categories'].items():
                stats_text.insert(tk.END, f"  • {cat}: {amount:,.2f} ₽\n")

        stats_text.config(state=tk.DISABLED)

    def _clear_main_area(self):
        """Очистка основной области контента."""
        for widget in self.main_area.winfo_children():
            widget.destroy()