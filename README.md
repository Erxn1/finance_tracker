
# Финансовый трекер

Простое приложение для отслеживания личных финансов с графическим интерфейсом.

## Возможности

- 📝 Добавление доходов и расходов
- 📊 Категоризация операций
- 📈 Аналитика и визуализация данных
- 💾 Сохранение данных в SQLite базе данных
- 📱 Графический интерфейс на Tkinter

## Установка

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/Erxn1/finance_tracker.git
   cd finance_tracker
Установите зависимости:

bash
pip install -r requirements.txt
Запустите приложение:

bash
python main.py
Структура проекта
main.py - точка входа в приложение

models.py - модели данных (Operation, Category)

database.py - работа с базой данных SQLite

analysis.py - функции анализа финансовых данных

gui.py - графический интерфейс

utils.py - вспомогательные функции

tests/ - юнит-тесты

Запуск тестов

## Все тесты 
```bash

pytest tests/
```
## С покрытием кода
``` bash

pytest --cov=. --cov-report=html tests/
```
## Через unittest    
```bash

python -m unittest discover tests
```
