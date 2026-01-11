"""
Модуль gui.py
Графический интерфейс приложения финансового трекера на Tkinter.
Связывает пользовательский интерфейс с бизнес-логикой (models.py) и базой данных (database.py).
"""

import tkinter as tk
from datetime import datetime
from tkinter import ttk, messagebox, filedialog

# Импорты для графиков matplotlib
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
matplotlib.use('TkAgg')  # Важно: указываем использовать Tkinter backend
import matplotlib.pyplot as plt

# Импорты ваших модулей
from models import Operation, OperationType, Category
from database import DatabaseManager
from analysis import analyze_expenses_by_category, analyze_income_vs_expenses_over_time
from utils import validate_date, validate_amount


class FinanceTrackerGUI:
    """
    Главный класс графического интерфейса приложения.
    Реализует основные функции: добавление, просмотр, анализ операций.
    """

    def __init__(self, root):
        """
        Инициализация главного окна и всех компонентов.

        Args:
            root: главное окно Tkinter
        """
        self.root = root
        self.root.title("Финансовый Трекер v1.0")
        self.root.geometry("1200x700")

        # Инициализируем менеджер базы данных
        self.db = DatabaseManager()

        # Цветовая схема приложения
        self.COLORS = {
            'bg_light': '#f0f0f0',
            'bg_dark': '#2c3e50',
            'income': '#27ae60',  # Зелёный для доходов
            'expense': '#e74c3c',  # Красный для расходов
            'text_light': '#ffffff',
            'text_dark': '#2c3e50'
        }

        # Настраиваем стиль ttk
        self._setup_styles()

        # Создаём интерфейс
        self._create_widgets()

        # Загружаем начальные данные
        self._load_initial_data()

        # Биндим события
        self._bind_events()

    def _setup_styles(self):
        """Настройка стилей для виджетов ttk."""
        style = ttk.Style()

        # Стиль для заголовков
        style.configure('Title.TLabel',
                        font=('Arial', 16, 'bold'),
                        foreground=self.COLORS['text_dark'])

        # Стиль для кнопок
        style.configure('Accent.TButton',
                        font=('Arial', 10, 'bold'),
                        padding=10)

        # Стиль для Treeview (таблицы)
        style.configure('Treeview',
                        font=('Arial', 10),
                        rowheight=25)
        style.configure('Treeview.Heading',
                        font=('Arial', 11, 'bold'))

    def _create_widgets(self):
        """Создаёт все виджеты интерфейса."""

        # 1. Панель навигации (слева)
        self.nav_frame = ttk.Frame(self.root, width=200)
        self.nav_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        # Заголовок приложения
        title_label = ttk.Label(self.nav_frame,
                                text="💰 Финансовый\nТрекер",
                                style='Title.TLabel')
        title_label.pack(pady=(0, 20))

        # Кнопки навигации
        nav_buttons = [
            ("📝 Добавить операцию", self.show_add_operation),
            ("📊 Просмотр операций", self.show_operations_list),
            ("📈 Аналитика", self.show_analytics),
            ("⚙️ Настройки", self.show_settings),
            ("📤 Экспорт данных", self.export_data),
            ("🔄 Обновить", self.refresh_data)
        ]

        for text, command in nav_buttons:
            btn = ttk.Button(self.nav_frame,
                             text=text,
                             command=command,
                             style='Accent.TButton')
            btn.pack(fill=tk.X, pady=5)

        # Текущий баланс
        self.balance_frame = ttk.LabelFrame(self.nav_frame, text="Текущий баланс")
        self.balance_frame.pack(fill=tk.X, pady=20)

        self.balance_label = ttk.Label(self.balance_frame,
                                       text="Загрузка...",
                                       font=('Arial', 14, 'bold'))
        self.balance_label.pack(pady=10)

        # 2. Основная рабочая область (справа)
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Notebook (вкладки) для основной работы
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Создаём вкладки
        self._create_add_operation_tab()
        self._create_operations_list_tab()
        self._create_analytics_tab()
        self._create_settings_tab()

        # Скрываем Notebook изначально - показываем через навигацию
        self.notebook.pack_forget()

    def _create_add_operation_tab(self):
        """Создаёт вкладку для добавления новых операций."""
        self.add_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.add_tab, text="Добавить операцию")

        # Заголовок
        ttk.Label(self.add_tab,
                  text="Добавить новую операцию",
                  style='Title.TLabel').pack(pady=20)

        # Форма ввода
        form_frame = ttk.Frame(self.add_tab)
        form_frame.pack(pady=20, padx=50, fill=tk.X)

        # Тип операции
        ttk.Label(form_frame, text="Тип операции:").grid(row=0, column=0, sticky=tk.W, pady=10)
        self.operation_type = tk.StringVar(value="расход")
        ttk.Radiobutton(form_frame, text="Доход", variable=self.operation_type,
                        value="доход", command=self._on_type_change).grid(row=0, column=1, padx=10)
        ttk.Radiobutton(form_frame, text="Расход", variable=self.operation_type,
                        value="расход", command=self._on_type_change).grid(row=0, column=2, padx=10)

        # Сумма
        ttk.Label(form_frame, text="Сумма:").grid(row=1, column=0, sticky=tk.W, pady=10)
        self.amount_entry = ttk.Entry(form_frame, font=('Arial', 12))
        self.amount_entry.grid(row=1, column=1, columnspan=2, sticky=tk.W + tk.E, pady=10)

        # Категория
        ttk.Label(form_frame, text="Категория:").grid(row=2, column=0, sticky=tk.W, pady=10)
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(form_frame,
                                           textvariable=self.category_var,
                                           font=('Arial', 12))
        self.category_combo.grid(row=2, column=1, columnspan=2, sticky=tk.W + tk.E, pady=10)

        # Новая категория (показывается при необходимости)
        self.new_category_frame = ttk.Frame(form_frame)
        self.new_category_frame.grid(row=3, column=0, columnspan=3, sticky=tk.W + tk.E, pady=5)
        self.new_category_frame.grid_remove()  # Скрываем изначально

        ttk.Label(self.new_category_frame, text="Новая категория:").pack(side=tk.LEFT, padx=5)
        self.new_category_entry = ttk.Entry(self.new_category_frame, font=('Arial', 12))
        self.new_category_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # Дата
        ttk.Label(form_frame, text="Дата:").grid(row=4, column=0, sticky=tk.W, pady=10)
        date_frame = ttk.Frame(form_frame)
        date_frame.grid(row=4, column=1, columnspan=2, sticky=tk.W + tk.E, pady=10)

        self.date_entry = ttk.Entry(date_frame, font=('Arial', 12))
        self.date_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        ttk.Button(date_frame, text="Сегодня",
                   command=self._set_today).pack(side=tk.LEFT, padx=5)

        # Комментарий
        ttk.Label(form_frame, text="Комментарий:").grid(row=5, column=0, sticky=tk.W, pady=10)
        self.comment_text = tk.Text(form_frame, height=4, font=('Arial', 12))
        self.comment_text.grid(row=5, column=1, columnspan=2, sticky=tk.W + tk.E, pady=10)

        # Кнопки формы
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=6, column=0, columnspan=3, pady=30)

        ttk.Button(button_frame, text="Добавить операцию",
                   command=self._add_operation, style='Accent.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Очистить форму",
                   command=self._clear_form).pack(side=tk.LEFT, padx=5)

    def _create_operations_list_tab(self):
        """Создаёт вкладку для просмотра и управления операциями."""
        self.list_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.list_tab, text="Операции")

        # Панель фильтров
        filter_frame = ttk.LabelFrame(self.list_tab, text="Фильтры")
        filter_frame.pack(fill=tk.X, padx=10, pady=10)

        # Период
        ttk.Label(filter_frame, text="Период:").grid(row=0, column=0, padx=5, pady=5)

        self.period_var = tk.StringVar(value="месяц")
        periods = [("Неделя", "неделя"), ("Месяц", "месяц"), ("Квартал", "квартал"), ("Год", "год"), ("Все", "все")]

        for i, (text, value) in enumerate(periods):
            ttk.Radiobutton(filter_frame, text=text, variable=self.period_var,
                            value=value, command=self._apply_filters).grid(row=0, column=i + 1, padx=5)

        # Тип операции
        ttk.Label(filter_frame, text="Тип:").grid(row=1, column=0, padx=5, pady=5)
        self.filter_type_var = tk.StringVar(value="все")
        ttk.Radiobutton(filter_frame, text="Все", variable=self.filter_type_var,
                        value="все", command=self._apply_filters).grid(row=1, column=1, padx=5)
        ttk.Radiobutton(filter_frame, text="Доходы", variable=self.filter_type_var,
                        value="доход", command=self._apply_filters).grid(row=1, column=2, padx=5)
        ttk.Radiobutton(filter_frame, text="Расходы", variable=self.filter_type_var,
                        value="расход", command=self._apply_filters).grid(row=1, column=3, padx=5)

        # Кнопки управления
        button_frame = ttk.Frame(filter_frame)
        button_frame.grid(row=2, column=0, columnspan=len(periods) + 1, pady=10)

        ttk.Button(button_frame, text="Применить фильтры",
                   command=self._apply_filters).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Сбросить фильтры",
                   command=self._reset_filters).pack(side=tk.LEFT, padx=5)

        # Таблица операций
        columns = ("ID", "Дата", "Тип", "Категория", "Сумма", "Комментарий")
        self.operations_tree = ttk.Treeview(self.list_tab, columns=columns, show="headings", height=15)

        # Настройка колонок
        for col in columns:
            self.operations_tree.heading(col, text=col)
            self.operations_tree.column(col, width=100)

        self.operations_tree.column("Дата", width=120)
        self.operations_tree.column("Комментарий", width=200)
        self.operations_tree.column("Сумма", width=100)

        # Скроллбар для таблицы
        scrollbar = ttk.Scrollbar(self.list_tab, orient=tk.VERTICAL,
                                  command=self.operations_tree.yview)
        self.operations_tree.configure(yscrollcommand=scrollbar.set)

        # Панель для таблицы и скроллбара
        tree_frame = ttk.Frame(self.list_tab)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        self.operations_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Кнопки управления записями
        record_buttons = ttk.Frame(self.list_tab)
        record_buttons.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(record_buttons, text="Удалить выбранное",
                   command=self._delete_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(record_buttons, text="Редактировать",
                   command=self._edit_selected).pack(side=tk.LEFT, padx=5)

    def _create_analytics_tab(self):
        """Создаёт вкладку для аналитики и графиков."""
        self.analytics_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.analytics_tab, text="Аналитика")

        # Верхняя панель с кнопками графиков
        graph_buttons_frame = ttk.Frame(self.analytics_tab)
        graph_buttons_frame.pack(fill=tk.X, padx=10, pady=10)

        graph_types = [
            ("📊 Расходы по категориям", self._show_expenses_by_category),
            ("📈 Доходы vs Расходы", self._show_income_vs_expenses),
            ("💰 Топ расходов", self._show_top_expenses),
            ("📅 Динамика за период", self._show_trend_over_time)
        ]

        for text, command in graph_types:
            btn = ttk.Button(graph_buttons_frame, text=text, command=command)
            btn.pack(side=tk.LEFT, padx=5)

        # Область для графиков
        self.graph_frame = ttk.Frame(self.analytics_tab)
        self.graph_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Текстовый блок для статистики
        self.stats_text = tk.Text(self.analytics_tab, height=8, font=('Arial', 10))
        self.stats_text.pack(fill=tk.X, padx=10, pady=10)

    def _create_settings_tab(self):
        """Создаёт вкладку настроек."""
        self.settings_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_tab, text="Настройки")

        ttk.Label(self.settings_tab,
                  text="Настройки приложения",
                  style='Title.TLabel').pack(pady=20)

        # Настройка категорий
        categories_frame = ttk.LabelFrame(self.settings_tab, text="Управление категориями")
        categories_frame.pack(fill=tk.X, padx=20, pady=10)

        # Список категорий
        self.categories_listbox = tk.Listbox(categories_frame, height=10, font=('Arial', 11))
        self.categories_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        scrollbar = ttk.Scrollbar(categories_frame, orient=tk.VERTICAL,
                                  command=self.categories_listbox.yview)
        self.categories_listbox.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Кнопки управления категориями
        cat_buttons = ttk.Frame(categories_frame)
        cat_buttons.pack(side=tk.RIGHT, padx=10)

        ttk.Button(cat_buttons, text="Добавить",
                   command=self._add_category_dialog).pack(fill=tk.X, pady=2)
        ttk.Button(cat_buttons, text="Удалить",
                   command=self._delete_category).pack(fill=tk.X, pady=2)
        ttk.Button(cat_buttons, text="Обновить",
                   command=self._refresh_categories).pack(fill=tk.X, pady=2)

        # Настройки базы данных
        db_frame = ttk.LabelFrame(self.settings_tab, text="База данных")
        db_frame.pack(fill=tk.X, padx=20, pady=10)

        ttk.Button(db_frame, text="Создать резервную копию",
                   command=self._backup_database).pack(pady=5)
        ttk.Button(db_frame, text="Восстановить из резервной копии",
                   command=self._restore_database).pack(pady=5)
        ttk.Button(db_frame, text="Очистить все данные",
                   command=self._clear_database).pack(pady=5)

    def _load_initial_data(self):
        """Загружает начальные данные в интерфейс."""
        # Загружаем категории
        self._refresh_categories()

        # Загружаем баланс
        self._update_balance()

        # Загружаем операции в таблицу
        self._load_operations_to_table()

    def _bind_events(self):
        """Привязывает события к виджетам."""
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

        # Двойной клик по операции для редактирования
        self.operations_tree.bind("<Double-1>", lambda e: self._edit_selected())

    # ===== МЕТОДЫ ДЛЯ РАБОТЫ С ДАННЫМИ =====

    def _refresh_categories(self):
        """Обновляет список категорий из базы данных."""
        categories = self.db.get_all_categories()
        self.categories = categories

        # Обновляем combobox
        category_names = [cat.name for cat in categories]
        self.category_combo['values'] = category_names

        # Обновляем listbox
        self.categories_listbox.delete(0, tk.END)
        for cat in categories:
            status = "✓" if cat.is_active else "✗"
            self.categories_listbox.insert(tk.END, f"{status} {cat.name}")

    def _update_balance(self):
        """Обновляет отображение текущего баланса."""
        try:
            balance = self.db.get_balance()
            total = balance.get("баланс", 0)

            # Цвет в зависимости от баланса
            color = self.COLORS['income'] if total >= 0 else self.COLORS['expense']

            self.balance_label.configure(
                text=f"{total:,.2f} ₽",
                foreground=color
            )
        except Exception:
            self.balance_label.configure(text="Ошибка загрузки")

    def _load_operations_to_table(self, filters=None):
        """Загружает операции в таблицу с учётом фильтров."""
        # Очищаем таблицу
        for item in self.operations_tree.get_children():
            self.operations_tree.delete(item)

        try:
            # Получаем операции из БД
            operations = self.db.get_all_operations()

            # Добавляем операции в таблицу
            for op in operations:
                values = (
                    op.id,
                    op.date.strftime("%d.%m.%Y %H:%M"),
                    op.type.value,
                    op.category.name,
                    f"{op.formatted_amount} ₽",
                    op.comment[:50] + "..." if len(op.comment) > 50 else op.comment
                )

                # Цвет строки в зависимости от типа
                tags = ('income' if op.type == OperationType.INCOME else 'expense',)
                self.operations_tree.insert('', tk.END, values=values, tags=tags)

            # Настраиваем цвета строк
            self.operations_tree.tag_configure('income', foreground=self.COLORS['income'])
            self.operations_tree.tag_configure('expense', foreground=self.COLORS['expense'])

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить операции: {str(e)}")

    # ===== ОБРАБОТЧИКИ СОБЫТИЙ =====

    def _on_type_change(self):
        """Обработчик изменения типа операции."""
        # Можно добавить логику изменения интерфейса при смене типа
        pass

    def _set_today(self):
        """Устанавливает сегодняшнюю дату в поле ввода."""
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

    def _add_operation(self):
        """Добавляет новую операцию в базу данных."""
        try:
            # Валидация данных
            amount_text = self.amount_entry.get().strip()
            if not validate_amount(amount_text):
                messagebox.showerror("Ошибка", "Неверный формат суммы!")
                return

            amount = float(amount_text)

            date_text = self.date_entry.get().strip()
            if not validate_date(date_text):
                messagebox.showerror("Ошибка", "Неверный формат даты! Используйте ГГГГ-ММ-ДД")
                return

            # Получаем или создаём категорию
            category_name = self.category_var.get().strip()
            if not category_name:
                # Пробуем получить новую категорию
                category_name = self.new_category_entry.get().strip()
                if not category_name:
                    messagebox.showerror("Ошибка", "Укажите категорию!")
                    return

            # Ищем категорию или создаём новую
            category = next((cat for cat in self.categories if cat.name == category_name), None)
            if not category:
                category = Category(name=category_name)
                self.db.save_category(category)
                self._refresh_categories()

            # Создаём операцию
            operation = Operation(
                amount=amount,
                type=OperationType(self.operation_type.get()),
                category=category,
                date=datetime.strptime(date_text, "%Y-%m-%d"),
                comment=self.comment_text.get("1.0", tk.END).strip()
            )

            # Сохраняем в БД
            self.db.save_operation(operation)

            # Обновляем интерфейс
            self._clear_form()
            self._update_balance()
            self._load_operations_to_table()

            messagebox.showinfo("Успех", "Операция успешно добавлена!")

        except ValueError as e:
            messagebox.showerror("Ошибка", f"Ошибка в данных: {str(e)}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось добавить операцию: {str(e)}")

    def _clear_form(self):
        """Очищает форму добавления операции."""
        self.amount_entry.delete(0, tk.END)
        self.category_var.set("")
        self.new_category_entry.delete(0, tk.END)
        self.new_category_frame.grid_remove()
        self.comment_text.delete("1.0", tk.END)
        self._set_today()

    def _apply_filters(self):
        """Применяет фильтры к таблице операций."""
        # Здесь будет реализация фильтрации
        messagebox.showinfo("Инфо", "Фильтрация будет реализована в следующей версии")

    def _reset_filters(self):
        """Сбрасывает все фильтры."""
        self.period_var.set("месяц")
        self.filter_type_var.set("все")
        self._load_operations_to_table()

    def _delete_selected(self):
        """Удаляет выбранную операцию."""
        selection = self.operations_tree.selection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите операцию для удаления")
            return

        if messagebox.askyesno("Подтверждение", "Удалить выбранную операцию?"):
            try:
                # Получаем ID операции из таблицы
                item = self.operations_tree.item(selection[0])
                operation_id = item['values'][0]  # Первый столбец - ID

                self.db.delete_operation(operation_id)
                self.operations_tree.delete(selection[0])
                self._update_balance()

                messagebox.showinfo("Успех", "Операция удалена")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось удалить операцию: {str(e)}")

    def _edit_selected(self):
        """Редактирует выбранную операцию."""
        selection = self.operations_tree.selection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите операцию для редактирования")
            return

        messagebox.showinfo("Инфо", "Редактирование будет реализовано в следующей версии")

    # ===== МЕТОДЫ АНАЛИТИКИ =====

    def _show_expenses_by_category(self):
        """Показывает график расходов по категориям."""
        try:
            # Получаем данные для анализа
            operations = self.db.get_all_operations()

            if not operations:
                messagebox.showinfo("Инфо", "Нет данных для анализа")
                return

            # Очищаем область графика
            for widget in self.graph_frame.winfo_children():
                widget.destroy()

            # Создаём график
            fig, ax = plt.subplots(figsize=(8, 6))

            # Анализируем данные
            expense_data = analyze_expenses_by_category(operations)

            if expense_data:
                # Создаём круговую диаграмму
                labels = list(expense_data.keys())
                sizes = list(expense_data.values())

                ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
                ax.set_title('Расходы по категориям')

                # Отображаем график в Tkinter
                canvas = FigureCanvasTkAgg(fig, self.graph_frame)
                canvas.draw()
                canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

                # Показываем статистику
                self._show_stats(expense_data)
            else:
                messagebox.showinfo("Инфо", "Нет данных о расходах")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка построения графика: {str(e)}")

    def _show_income_vs_expenses(self):
        """Показывает график доходов vs расходов."""
        try:
            operations = self.db.get_all_operations()

            if not operations:
                messagebox.showinfo("Инфо", "Нет данных для анализа")
                return

            # Очищаем область графика
            for widget in self.graph_frame.winfo_children():
                widget.destroy()

            # Создаём график
            fig, ax = plt.subplots(figsize=(8, 6))

            # Анализируем данные
            trend_data = analyze_income_vs_expenses_over_time(operations)

            if trend_data:
                # Создаём линейный график
                dates = list(trend_data.keys())
                incomes = [data.get('income', 0) for data in trend_data.values()]
                expenses = [data.get('expense', 0) for data in trend_data.values()]

                ax.plot(dates, incomes, label='Доходы', color=self.COLORS['income'], marker='o')
                ax.plot(dates, expenses, label='Расходы', color=self.COLORS['expense'], marker='s')

                ax.set_xlabel('Дата')
                ax.set_ylabel('Сумма (₽)')
                ax.set_title('Динамика доходов и расходов')
                ax.legend()
                ax.grid(True, alpha=0.3)

                # Поворачиваем подписи дат
                plt.xticks(rotation=45)
                plt.tight_layout()

                # Отображаем график
                canvas = FigureCanvasTkAgg(fig, self.graph_frame)
                canvas.draw()
                canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            else:
                messagebox.showinfo("Инфо", "Недостаточно данных для построения графика")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка построения графика: {str(e)}")

    def _show_top_expenses(self):
        """Показывает топ расходов."""
        messagebox.showinfo("Инфо", "График топ расходов будет реализован")

    def _show_trend_over_time(self):
        """Показывает динамику за период."""
        messagebox.showinfo("Инфо", "График динамики будет реализован")

    def _show_stats(self, data):
        """Показывает статистику в текстовом поле."""
        self.stats_text.delete("1.0", tk.END)

        if isinstance(data, dict):
            total = sum(data.values())
            self.stats_text.insert("1.0", f"Общая сумма: {total:,.2f} ₽\n\n")

            for category, amount in sorted(data.items(), key=lambda x: x[1], reverse=True):
                percentage = (amount / total * 100) if total > 0 else 0
                self.stats_text.insert(tk.END,
                                       f"{category}: {amount:,.2f} ₽ ({percentage:.1f}%)\n")

    # ===== МЕТОДЫ НАВИГАЦИИ =====

    def show_add_operation(self):
        """Показывает вкладку добавления операции."""
        self.notebook.pack(fill=tk.BOTH, expand=True)
        self.notebook.select(self.add_tab)

    def show_operations_list(self):
        """Показывает вкладку списка операций."""
        self.notebook.pack(fill=tk.BOTH, expand=True)
        self.notebook.select(self.list_tab)
        self._load_operations_to_table()

    def show_analytics(self):
        """Показывает вкладку аналитики."""
        self.notebook.pack(fill=tk.BOTH, expand=True)
        self.notebook.select(self.analytics_tab)

    def show_settings(self):
        """Показывает вкладку настроек."""
        self.notebook.pack(fill=tk.BOTH, expand=True)
        self.notebook.select(self.settings_tab)

    def export_data(self):
        """Экспортирует данные в файл."""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )

        if filepath:
            try:
                count = self.db.export_to_csv(filepath)
                messagebox.showinfo("Успех", f"Экспортировано {count} операций в {filepath}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось экспортировать данные: {str(e)}")

    def refresh_data(self):
        """Обновляет все данные в интерфейсе."""
        self._refresh_categories()
        self._update_balance()
        self._load_operations_to_table()
        messagebox.showinfo("Обновлено", "Данные успешно обновлены")

    # ===== МЕТОДЫ ДЛЯ РАБОТЫ С КАТЕГОРИЯМИ =====

    def _add_category_dialog(self):
        """Диалог добавления новой категории."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавить категорию")
        dialog.geometry("400x200")
        dialog.transient(self.root)
        dialog.grab_set()

        ttk.Label(dialog, text="Название категории:").pack(pady=10)
        name_entry = ttk.Entry(dialog, font=('Arial', 12))
        name_entry.pack(pady=5, padx=20, fill=tk.X)

        ttk.Label(dialog, text="Описание (необязательно):").pack(pady=10)
        desc_entry = ttk.Entry(dialog, font=('Arial', 12))
        desc_entry.pack(pady=5, padx=20, fill=tk.X)

        def save_category():
            name = name_entry.get().strip()
            if not name:
                messagebox.showerror("Ошибка", "Введите название категории")
                return

            try:
                category = Category(name=name, description=desc_entry.get().strip())
                self.db.save_category(category)
                self._refresh_categories()
                dialog.destroy()
                messagebox.showinfo("Успех", "Категория добавлена")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось добавить категорию: {str(e)}")

        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=20)

        ttk.Button(button_frame, text="Добавить", command=save_category).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="Отмена", command=dialog.destroy).pack(side=tk.LEFT, padx=10)

    def _delete_category(self):
        """Удаляет выбранную категорию."""
        selection = self.categories_listbox.curselection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите категорию для удаления")
            return

        if messagebox.askyesno("Подтверждение", "Удалить выбранную категорию?"):
            try:
                # Здесь нужно реализовать удаление категории из БД
                # Пока просто показываем сообщение
                messagebox.showinfo("Инфо", "Удаление категорий будет реализовано")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось удалить категорию: {str(e)}")

    # ===== МЕТОДЫ ДЛЯ РАБОТЫ С БАЗОЙ ДАННЫХ =====

    def _backup_database(self):
        """Создаёт резервную копию базы данных."""
        import shutil

        filepath = filedialog.asksaveasfilename(
            defaultextension=".db",
            filetypes=[("Database files", "*.db"), ("All files", "*.*")],
            initialfile="finance_backup.db"
        )

        if filepath:
            try:
                shutil.copy2("finance.db", filepath)
                messagebox.showinfo("Успех", f"Резервная копия создана: {filepath}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось создать резервную копию: {str(e)}")

    def _restore_database(self):
        """Восстанавливает базу данных из резервной копии."""
        filepath = filedialog.askopenfilename(
            filetypes=[("Database files", "*.db"), ("All files", "*.*")]
        )

        if filepath:
            if messagebox.askyesno("Подтверждение",
                                   "Восстановить базу данных? Все текущие данные будут заменены."):
                try:
                    import shutil
                    shutil.copy2(filepath, "finance.db")
                    self.refresh_data()
                    messagebox.showinfo("Успех", "База данных восстановлена")
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Не удалось восстановить базу данных: {str(e)}")

    def _clear_database(self):
        """Очищает всю базу данных."""
        if messagebox.askyesno("Внимание",
                               "Очистить ВСЕ данные? Это действие нельзя отменить."):
            try:
                # Здесь нужно реализовать очистку БД
                messagebox.showinfo("Инфо", "Очистка БД будет реализована")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось очистить базу данных: {str(e)}")

    # ===== СИСТЕМНЫЕ МЕТОДЫ =====

    def _on_closing(self):
        """Обработчик закрытия окна."""
        if messagebox.askokcancel("Выход", "Закрыть приложение?"):
            try:
                self.db.close()
            except:
                pass
            finally:
                self.root.destroy()


# Функции анализа (заглушки, нужно реализовать в analysis.py)
def analyze_expenses_by_category(operations):
    """Анализирует расходы по категориям. ЗАГЛУШКА."""
    expenses = {}
    for op in operations:
        if op.type == OperationType.EXPENSE:
            cat_name = op.category.name
            expenses[cat_name] = expenses.get(cat_name, 0) + op.amount
    return expenses


def analyze_income_vs_expenses_over_time(operations):
    """Анализирует доходы и расходы по времени. ЗАГЛУШКА."""
    trend = {}
    for op in operations:
        date_str = op.date.strftime("%Y-%m-%d")
        if date_str not in trend:
            trend[date_str] = {'income': 0, 'expense': 0}

        if op.type == OperationType.INCOME:
            trend[date_str]['income'] += op.amount
        else:
            trend[date_str]['expense'] += op.amount

    # Сортируем по дате
    return dict(sorted(trend.items()))


# Функции валидации (заглушки, нужно реализовать в utils.py)
def validate_date(date_str):
    """Проверяет формат даты. ЗАГЛУШКА."""
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def validate_amount(amount_str):
    """Проверяет формат суммы. ЗАГЛУШКА."""
    try:
        float(amount_str)
        return True
    except ValueError:
        return False


def main():
    """Точка входа в приложение."""
    root = tk.Tk()
    app = FinanceTrackerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()