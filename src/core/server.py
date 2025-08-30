#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aleph Messenger - Сервер для тестирования
"""

import sys
import os
import signal
import threading
import time

# Добавляем путь к корню проекта в PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(current_dir, '..', '..')
sys.path.insert(0, project_root)

from src.database.database import Database
from src.network.network_manager import NetworkManager
from src.config import server_config as config

def signal_handler(signum, frame):
    """Обработчик сигналов для корректного завершения"""
    print(f"\nПолучен сигнал {signum}. Завершение сервера...")
    sys.exit(0)

def main():
    """Главная функция сервера"""
    print("=" * 50)
    print(f"Запуск {config.APP_NAME} Server v{config.APP_VERSION}")
    print("=" * 50)
    
    # Регистрация обработчиков сигналов
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Создание базы данных
        print("Инициализация базы данных...")
        database = Database()
        print("✓ База данных инициализирована")
        
        # Создание сетевого менеджера
        print("Инициализация сетевого менеджера...")
        network_manager = NetworkManager(database)
        print("✓ Сетевой менеджер инициализирован")
        
        # Запуск сервера
        print(f"Запуск сервера на {config.HOST}:{config.PORT}...")
        print(f"Внешний IP: {config.EXTERNAL_IP}:{config.EXTERNAL_PORT}")
        print("Сервер будет доступен из интернета")
        
        if network_manager.start_server():
            print("✓ Сервер успешно запущен")
            print(f"Локальный адрес: {config.HOST}:{config.PORT}")
            print(f"Внешний адрес: {config.EXTERNAL_IP}:{config.EXTERNAL_PORT}")
            print("Ожидание подключений...")
            print("\nДля остановки сервера нажмите Ctrl+C")
            
            # Основной цикл сервера
            try:
                while network_manager.is_running:
                    time.sleep(1)
                    
                    # Вывод статистики каждые 30 секунд
                    if int(time.time()) % 30 == 0:
                        connected_users = len(network_manager.connected_users)
                        print(f"Подключенных пользователей: {connected_users}")
                        
            except KeyboardInterrupt:
                print("\nПолучен сигнал остановки...")
                
        else:
            print("✗ Не удалось запустить сервер")
            return 1
            
    except Exception as e:
        print(f"✗ Критическая ошибка: {e}")
        return 1
    
    finally:
        # Остановка сервера
        if 'network_manager' in locals():
            print("Остановка сервера...")
            network_manager.stop_server()
            print("✓ Сервер остановлен")
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")
        sys.exit(1)
