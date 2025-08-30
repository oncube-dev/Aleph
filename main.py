#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aleph Messenger - Главный файл приложения
"""

import sys
import os
import signal
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import QTimer
# Добавляем путь к src в PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from src.config import client_config as config
except ImportError:
    try:
        from src.config import server_config as config
    except ImportError:
        from src.config import config
from src.ui.auth_window import AuthWindow
from src.ui.main_window import MainWindow
from src.database.database import Database

def signal_handler(signum, frame):
    """Обработчик сигналов для корректного завершения"""
    print(f"\nПолучен сигнал {signum}. Завершение приложения...")
    sys.exit(0)

def check_dependencies():
    """Проверка зависимостей"""
    try:
        import PySide6
        print("✓ PySide6 найден")
    except ImportError:
        print("✗ PySide6 не найден. Установите: pip install PySide6")
        return False
    
    try:
        import pyaudio
        print("✓ PyAudio найден")
    except ImportError:
        print("✗ PyAudio не найден. Установите: pip install PyAudio")
        return False
    
    try:
        import sqlite3
        print("✓ SQLite3 найден")
    except ImportError:
        print("✗ SQLite3 не найден")
        return False
    
    return True

def create_database():
    """Создание и инициализация базы данных"""
    try:
        db = Database()
        print("✓ База данных инициализирована")
        return db
    except Exception as e:
        print(f"✗ Ошибка инициализации БД: {e}")
        return None

def main():
    """Главная функция приложения"""
    print("=" * 50)
    print(f"Запуск {config.APP_NAME} v{config.APP_VERSION}")
    print("=" * 50)
    
    # Регистрация обработчиков сигналов
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Проверка зависимостей
    if not check_dependencies():
        print("Ошибка: Не все зависимости установлены")
        return 1
    
    # Создание базы данных
    db = create_database()
    if not db:
        print("Ошибка: Не удалось создать базу данных")
        return 1
    
    # Создание Qt приложения
    app = QApplication(sys.argv)
    app.setApplicationName(config.APP_NAME)
    app.setApplicationVersion(config.APP_VERSION)
    
    # Установка стилей приложения
    app.setStyle('Fusion')
    
    # Создание окна аутентификации
    try:
        auth_window = AuthWindow()
        print("Окно аутентификации создано")
    except Exception as e:
        print(f"Ошибка создания окна аутентификации: {e}")
        return 1
    
    def on_auth_successful(user_id):
        """Обработка успешной аутентификации"""
        print(f"Пользователь {user_id} успешно аутентифицирован")
        
        # Создание главного окна
        try:
            main_window = MainWindow(user_id)
            
            # Сохранить ссылку на главное окно в приложении
            app.main_window = main_window
            
            # Показ главного окна
            main_window.show()
            main_window.raise_()  # Поднять окно на передний план
            main_window.activateWindow()  # Активировать окно
        except Exception as e:
            print(f"Ошибка создания/показа главного окна: {e}")
            return
        
        # Скрытие окна аутентификации
        auth_window.hide()
        
        # Подключение сигнала закрытия главного окна
        def on_main_window_closed():
            print("Главное окно закрыто, завершение приложения...")
            app.quit()
        
        # Подключить сигнал закрытия окна (используем destroyed вместо closed)
        main_window.destroyed.connect(on_main_window_closed)
        
        # Убедиться, что главное окно остается активным
        QTimer.singleShot(100, lambda: main_window.raise_())
    
    # Подключение сигнала успешной аутентификации
    auth_window.auth_successful.connect(on_auth_successful)
    
    # Показ окна аутентификации
    try:
        auth_window.show()
        print("Окно аутентификации показано")
    except Exception as e:
        print(f"Ошибка показа окна аутентификации: {e}")
        return 1
    
    # Запуск главного цикла приложения
    try:
        return app.exec()
    except KeyboardInterrupt:
        print("\nПриложение прервано пользователем")
        return 0
    except Exception as e:
        print(f"Критическая ошибка: {e}")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")
        sys.exit(1)
