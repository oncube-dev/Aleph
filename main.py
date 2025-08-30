#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aleph Messenger - Запуск клиента
"""

import sys
import os

# Добавляем путь к src в PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Импортируем и запускаем главную функцию из src/core/main.py
from src.core.main import main

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")
        sys.exit(1)
