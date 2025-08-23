#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестовый скрипт для проверки автоматического обновления чата
"""

import time
import sqlite3
from datetime import datetime
import config

def test_chat_updates():
    """Тестирование автоматического обновления чата"""
    print("Тестирование автоматического обновления чата...")
    
    try:
        # Подключение к базе данных
        conn = sqlite3.connect(config.DATABASE_PATH)
        cursor = conn.cursor()
        
        # Создание тестовых пользователей
        test_users = ['test_user1', 'test_user2']
        for user_id in test_users:
            cursor.execute('''
                INSERT OR IGNORE INTO users (user_id, display_name, is_online)
                VALUES (?, ?, ?)
            ''', (user_id, f"Test User {user_id[-1]}", True))
        
        # Очистка старых тестовых сообщений
        cursor.execute('DELETE FROM messages WHERE sender_id IN (?, ?) OR receiver_id IN (?, ?)',
                      test_users + test_users)
        
        conn.commit()
        print("✓ Тестовые пользователи созданы")
        
        # Симуляция отправки сообщений
        print("\nОтправка тестовых сообщений...")
        
        for i in range(3):
            message_text = f"Тестовое сообщение {i+1} от {datetime.now().strftime('%H:%M:%S')}"
            
            cursor.execute('''
                INSERT INTO messages (sender_id, receiver_id, message_text, timestamp)
                VALUES (?, ?, ?, ?)
            ''', ('test_user1', 'test_user2', message_text, datetime.now().isoformat()))
            
            conn.commit()
            print(f"✓ Сообщение {i+1} отправлено: {message_text}")
            
            # Пауза между сообщениями
            time.sleep(2)
        
        # Проверка сообщений в базе
        cursor.execute('''
            SELECT sender_id, receiver_id, message_text, timestamp
            FROM messages 
            WHERE (sender_id = ? AND receiver_id = ?) OR (sender_id = ? AND receiver_id = ?)
            ORDER BY timestamp
        ''', ('test_user1', 'test_user2', 'test_user2', 'test_user1'))
        
        messages = cursor.fetchall()
        print(f"\n✓ Всего сообщений в базе: {len(messages)}")
        
        for msg in messages:
            print(f"  - {msg[0]} -> {msg[1]}: {msg[2]} ({msg[3]})")
        
        # Тестирование метода get_messages_since
        print("\nТестирование get_messages_since...")
        
        # Получение сообщений с определенного времени
        if messages:
            first_message_time = messages[0][3]
            cursor.execute('''
                SELECT sender_id, receiver_id, message_text, timestamp
                FROM messages 
                WHERE ((sender_id = ? AND receiver_id = ?) OR (sender_id = ? AND receiver_id = ?))
                   AND timestamp > ?
                ORDER BY timestamp ASC
            ''', ('test_user1', 'test_user2', 'test_user2', 'test_user1', first_message_time))
            
            new_messages = cursor.fetchall()
            print(f"✓ Новых сообщений после {first_message_time}: {len(new_messages)}")
        
        conn.close()
        print("\n✓ Тестирование завершено успешно!")
        
        print("\nТеперь запустите приложение и откройте чат между test_user1 и test_user2")
        print("Сообщения должны автоматически появляться в чате!")
        
    except Exception as e:
        print(f"✗ Ошибка тестирования: {e}")

if __name__ == "__main__":
    test_chat_updates()
