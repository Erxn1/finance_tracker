#!/usr/bin/env python3
"""
Запуск всех тестов проекта
"""

import unittest
import sys

if __name__ == "__main__":
    # Находим все тесты в папке tests
    loader = unittest.TestLoader()
    suite = loader.discover('tests', pattern='test_*.py')

    # Запускаем тесты
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Возвращаем код выхода
    sys.exit(0 if result.wasSuccessful() else 1)