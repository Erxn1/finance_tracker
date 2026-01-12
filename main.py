#!/usr/bin/env python3
"""
Главная точка входа в приложение Финансовый трекер.
Запускает графический интерфейс.
"""

import sys
import tkinter as tk
from gui import FinanceTrackerApp

def main():
    """Создает и запускает главное окно приложения."""
    root = tk.Tk()
    app = FinanceTrackerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()