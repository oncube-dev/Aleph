#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестовый скрипт для проверки компонентов Aleph Messenger
"""

import sys
import os

def test_imports():
    """Тест импорта модулей"""
    print("Тестирование импорта модулей...")
    
    try:
        import config
        print("✓ config.py импортирован")
    except ImportError as e:
        print(f"✗ Ошибка импорта config.py: {e}")
        return False
    
    try:
        from database import Database
        print("✓ database.py импортирован")
    except ImportError as e:
        print(f"✗ Ошибка импорта database.py: {e}")
        return False
    
    try:
        from network_manager import NetworkManager
        print("✓ network_manager.py импортирован")
    except ImportError as e:
        print(f"✗ Ошибка импорта network_manager.py: {e}")
        return False
    
    try:
        from audio_manager import AudioManager
        print("✓ audio_manager.py импортирован")
    except ImportError as e:
        print(f"✗ Ошибка импорта audio_manager.py: {e}")
        return False
    
    try:
        from auth_window import AuthWindow
        print("✓ auth_window.py импортирован")
    except ImportError as e:
        print(f"✗ Ошибка импорта auth_window.py: {e}")
        return False
    
    try:
        from main_window import MainWindow
        print("✓ main_window.py импортирован")
    except ImportError as e:
        print(f"✗ Ошибка импорта main_window.py: {e}")
        return False
    
    return True

def test_database():
    """Тест базы данных"""
    print("\nТестирование базы данных...")
    
    try:
        from database import Database
        
        # Создание временной БД
        test_db_path = "test_messenger.db"
        db = Database(test_db_path)
        print("✓ База данных создана")
        
        # Тест добавления пользователя
        success = db.add_user("test_user", "Test User")
        if success:
            print("✓ Пользователь добавлен")
        else:
            print("✗ Ошибка добавления пользователя")
            return False
        
        # Тест получения пользователя
        user = db.get_user("test_user")
        if user and user['user_id'] == "test_user":
            print("✓ Пользователь получен")
        else:
            print("✗ Ошибка получения пользователя")
            return False
        
        # Тест добавления сообщения
        success = db.add_message("test_user", "other_user", "Test message")
        if success:
            print("✓ Сообщение добавлено")
        else:
            print("✗ Ошибка добавления сообщения")
            return False
        
        # Тест получения сообщений
        messages = db.get_messages("test_user", "other_user")
        if messages and len(messages) > 0:
            print("✓ Сообщения получены")
        else:
            print("✗ Ошибка получения сообщений")
            return False
        
        # Очистка тестовой БД
        try:
            os.remove(test_db_path)
            print("✓ Тестовая БД удалена")
        except:
            pass
        
        return True
        
    except Exception as e:
        print(f"✗ Ошибка тестирования БД: {e}")
        return False

def test_config():
    """Тест конфигурации"""
    print("\nТестирование конфигурации...")
    
    try:
        import config
        
        # Проверка основных настроек
        required_settings = [
            'APP_NAME', 'APP_VERSION', 'DATABASE_PATH',
            'HOST', 'PORT', 'HEARTBEAT_INTERVAL',
            'AUDIO_SAMPLE_RATE', 'AUDIO_CHUNK_SIZE',
            'DEFAULT_USERS'
        ]
        
        for setting in required_settings:
            if hasattr(config, setting):
                print(f"✓ {setting} = {getattr(config, setting)}")
            else:
                print(f"✗ {setting} не найден")
                return False
        
        # Проверка тестовых пользователей
        if len(config.DEFAULT_USERS) >= 3:
            print(f"✓ Тестовых пользователей: {len(config.DEFAULT_USERS)}")
        else:
            print("✗ Недостаточно тестовых пользователей")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Ошибка тестирования конфигурации: {e}")
        return False

def test_network_manager():
    """Тест сетевого менеджера"""
    print("\nТестирование сетевого менеджера...")
    
    try:
        from database import Database
        from network_manager import NetworkManager
        
        # Создание тестовой БД
        test_db = Database("test_network.db")
        
        # Создание сетевого менеджера
        network = NetworkManager(test_db)
        print("✓ Сетевой менеджер создан")
        
        # Проверка обработчиков сообщений
        if hasattr(network, 'message_handlers') and len(network.message_handlers) > 0:
            print(f"✓ Обработчиков сообщений: {len(network.message_handlers)}")
        else:
            print("✗ Обработчики сообщений не найдены")
            return False
        
        # Очистка
        try:
            os.remove("test_network.db")
        except:
            pass
        
        return True
        
    except Exception as e:
        print(f"✗ Ошибка тестирования сетевого менеджера: {e}")
        return False

def main():
    """Главная функция тестирования"""
    print("=" * 50)
    print("Тестирование Aleph Messenger")
    print("=" * 50)
    
    tests = [
        ("Импорт модулей", test_imports),
        ("Конфигурация", test_config),
        ("База данных", test_database),
        ("Сетевой менеджер", test_network_manager),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                print(f"✓ {test_name} - ПРОЙДЕН")
                passed += 1
            else:
                print(f"✗ {test_name} - ПРОВАЛЕН")
        except Exception as e:
            print(f"✗ {test_name} - ОШИБКА: {e}")
    
    print("\n" + "=" * 50)
    print(f"РЕЗУЛЬТАТ: {passed}/{total} тестов пройдено")
    
    if passed == total:
        print("🎉 Все тесты пройдены успешно!")
        print("Приложение готово к запуску!")
        return 0
    else:
        print("⚠️  Некоторые тесты не пройдены")
        print("Проверьте ошибки выше")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"Критическая ошибка тестирования: {e}")
        sys.exit(1)
