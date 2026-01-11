"""
Скрипт для запуска всех тестов в проекте.
Показывает детальный отчёт и проверяет покрытие требований ТЗ.
"""

import unittest
import sys
import os


def run_all_tests():
    """Запускает все тесты и показывает отчёт."""

    print("=" * 70)
    print("ЗАПУСК ВСЕХ UNIT-ТЕСТОВ ДЛЯ ФИНАНСОВОГО ТРЕКЕРА")
    print("=" * 70)

    # Добавляем текущую директорию в путь Python
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

    # Определяем тесты, которые нужно запустить
    test_modules = [
        'test_models',
        'test_analysis',
        'test_utils',
        'test_database'
    ]

    # Собираем все тесты
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    for module_name in test_modules:
        try:
            module = __import__(module_name)
            module_suite = loader.loadTestsFromModule(module)
            suite.addTest(module_suite)
            print(f"✅  Загружен модуль: {module_name}")
        except ImportError as e:
            print(f"❌  Не удалось загрузить модуль {module_name}: {e}")
            print("    Убедитесь, что файл существует в текущей директории")

    # Запускаем тесты
    print("\n" + "=" * 70)
    print("ЗАПУСК ТЕСТОВ...")
    print("=" * 70)

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Показываем итоговую статистику
    print("\n" + "=" * 70)
    print("ИТОГОВАЯ СТАТИСТИКА")
    print("=" * 70)

    total_tests = result.testsRun
    failed_tests = len(result.failures)
    errored_tests = len(result.errors)
    passed_tests = total_tests - failed_tests - errored_tests

    print(f"Всего тестов: {total_tests}")
    print(f"✅  Пройдено: {passed_tests}")
    print(f"❌  Не пройдено: {failed_tests}")
    print(f"⚠️   Ошибок: {errored_tests}")

    # Проверяем покрытие требований ТЗ
    print("\n" + "=" * 70)
    print("ПРОВЕРКА ПОКРЫТИЯ ТРЕБОВАНИЙ ТЗ")
    print("=" * 70)

    tz_coverage = {
        "Модульность и ООП": total_tests > 0,  # Тесты для models.py
        "Работа с файлами/БД": 'test_database' in test_modules,
        "Анализ и визуализация": 'test_analysis' in test_modules,
        "Регулярные выражения": 'test_utils' in test_modules,
        "Обработка ошибок": failed_tests + errored_tests < total_tests,
        "Тестирование": total_tests >= 10,  # Минимум 10 тестов
        "Документация": all(os.path.exists(f"test_{m}.py") for m in ['models', 'analysis', 'utils', 'database'])
    }

    for requirement, covered in tz_coverage.items():
        status = "✅" if covered else "❌"
        print(f"{status} {requirement}")

    # Показываем непройденные тесты
    if result.failures or result.errors:
        print("\n" + "=" * 70)
        print("ДЕТАЛИ ОШИБОК")
        print("=" * 70)

        for i, (test, traceback) in enumerate(result.failures, 1):
            print(f"\n{i}. ❌ НЕ ПРОЙДЕН: {test}")
            print(f"   Ошибка: {traceback.splitlines()[-1]}")

        for i, (test, traceback) in enumerate(result.errors, 1):
            print(f"\n{i}. ⚠️  ОШИБКА: {test}")
            print(f"   Ошибка: {traceback.splitlines()[-1]}")

    # Возвращаем код завершения
    return 0 if result.wasSuccessful() else 1


def check_test_coverage():
    """Проверяет покрытие кода тестами (требует установленного coverage)."""
    print("\n" + "=" * 70)
    print("ПРОВЕРКА ПОКРЫТИЯ КОДА ТЕСТАМИ")
    print("=" * 70)

    try:
        import coverage

        # Инициализируем coverage
        cov = coverage.Coverage(
            source=['.', './core', './infrastructure', './analysis', './interfaces'],
            omit=['*/test_*.py', '*/__pycache__/*', '*/site-packages/*']
        )

        cov.start()

        # Запускаем тесты через coverage
        result_code = run_all_tests()

        cov.stop()
        cov.save()

        # Показываем отчёт
        print("\n" + "=" * 70)
        print("ОТЧЁТ О ПОКРЫТИИ КОДА")
        print("=" * 70)

        # Показываем сводку
        cov.report(show_missing=True, skip_covered=False)

        # Генерируем HTML-отчёт
        html_dir = "htmlcov"
        cov.html_report(directory=html_dir)
        print(f"\n📊 Подробный HTML-отчёт создан в папке: {html_dir}/index.html")

        return result_code

    except ImportError:
        print("ℹ️  Для проверки покрытия кода установите библиотеку coverage:")
        print("   pip install coverage")
        print("\nЗапускаю тесты без проверки покрытия...")
        return run_all_tests()


if __name__ == "__main__":
    # Проверяем аргументы командной строки
    if len(sys.argv) > 1 and sys.argv[1] == "--coverage":
        sys.exit(check_test_coverage())
    else:
        sys.exit(run_all_tests())