import sqlite3
import datetime
from typing import List, Dict, Optional
try:
    import server_config as config
except ImportError:
    try:
        import client_config as config
    except ImportError:
        import config

class Database:
    def __init__(self, db_path: str = None):
        self.db_path = db_path or config.DATABASE_PATH
        self.init_database()
        self.create_default_users()
    
    def init_database(self):
        """Инициализация базы данных и создание таблиц"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Таблица пользователей
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT UNIQUE NOT NULL,
                    display_name TEXT,
                    is_online BOOLEAN DEFAULT FALSE,
                    last_seen TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Таблица сообщений
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sender_id TEXT NOT NULL,
                    receiver_id TEXT NOT NULL,
                    message_text TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_read BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (sender_id) REFERENCES users (user_id),
                    FOREIGN KEY (receiver_id) REFERENCES users (user_id)
                )
            ''')
            
            # Таблица контактов
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS contacts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    contact_id TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id),
                    FOREIGN KEY (contact_id) REFERENCES users (user_id),
                    UNIQUE(user_id, contact_id)
                )
            ''')
            
            conn.commit()
    
    def create_default_users(self):
        """Создание тестовых пользователей по умолчанию"""
        for user_id in config.DEFAULT_USERS:
            self.add_user(user_id)
    
    def add_user(self, user_id: str, display_name: str = None) -> bool:
        """Добавление нового пользователя"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR IGNORE INTO users (user_id, display_name)
                    VALUES (?, ?)
                ''', (user_id, display_name or user_id))
                conn.commit()
                return True
        except Exception as e:
            print(f"Ошибка добавления пользователя: {e}")
            return False
    
    def get_user(self, user_id: str) -> Optional[Dict]:
        """Получение информации о пользователе"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT user_id, display_name, is_online, last_seen, created_at
                    FROM users WHERE user_id = ?
                ''', (user_id,))
                row = cursor.fetchone()
                if row:
                    return {
                        'user_id': row[0],
                        'display_name': row[1],
                        'is_online': bool(row[2]),
                        'last_seen': row[3],
                        'created_at': row[4]
                    }
                return None
        except Exception as e:
            print(f"Ошибка получения пользователя: {e}")
            return None
    
    def get_all_users(self) -> List[Dict]:
        """Получение списка всех пользователей"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT user_id, display_name, is_online, last_seen, created_at
                    FROM users ORDER BY display_name
                ''')
                rows = cursor.fetchall()
                return [{
                    'user_id': row[0],
                    'display_name': row[1],
                    'is_online': bool(row[2]),
                    'last_seen': row[3],
                    'created_at': row[4]
                } for row in rows]
        except Exception as e:
            print(f"Ошибка получения пользователей: {e}")
            return []
    
    def update_user_status(self, user_id: str, is_online: bool):
        """Обновление онлайн-статуса пользователя"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE users 
                    SET is_online = ?, last_seen = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                ''', (is_online, user_id))
                conn.commit()
        except Exception as e:
            print(f"Ошибка обновления статуса: {e}")
    
    def add_message(self, sender_id: str, receiver_id: str, message_text: str) -> bool:
        """Добавление нового сообщения"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO messages (sender_id, receiver_id, message_text)
                    VALUES (?, ?, ?)
                ''', (sender_id, receiver_id, message_text))
                conn.commit()
                return True
        except Exception as e:
            print(f"Ошибка добавления сообщения: {e}")
            return False
    
    def get_messages(self, user1_id: str, user2_id: str, limit: int = 100) -> List[Dict]:
        """Получение истории сообщений между двумя пользователями"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT sender_id, receiver_id, message_text, timestamp, is_read
                    FROM messages 
                    WHERE (sender_id = ? AND receiver_id = ?) 
                       OR (sender_id = ? AND receiver_id = ?)
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (user1_id, user2_id, user2_id, user1_id, limit))
                rows = cursor.fetchall()
                return [{
                    'sender_id': row[0],
                    'receiver_id': row[1],
                    'message_text': row[2],
                    'timestamp': row[3],
                    'is_read': bool(row[4])
                } for row in reversed(rows)]  # Возвращаем в хронологическом порядке
        except Exception as e:
            print(f"Ошибка получения сообщений: {e}")
            return []
    
    def get_messages_since(self, user1_id: str, user2_id: str, since_timestamp: str, limit: int = 100) -> List[Dict]:
        """Получение новых сообщений между двумя пользователями с определенного времени"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT sender_id, receiver_id, message_text, timestamp, is_read
                    FROM messages 
                    WHERE ((sender_id = ? AND receiver_id = ?) 
                        OR (sender_id = ? AND receiver_id = ?))
                       AND timestamp > ?
                    ORDER BY timestamp ASC
                    LIMIT ?
                ''', (user1_id, user2_id, user2_id, user1_id, since_timestamp, limit))
                rows = cursor.fetchall()
                return [{
                    'sender_id': row[0],
                    'receiver_id': row[1],
                    'message_text': row[2],
                    'timestamp': row[3],
                    'is_read': bool(row[4])
                } for row in rows]  # Возвращаем в хронологическом порядке
        except Exception as e:
            print(f"Ошибка получения новых сообщений: {e}")
            return []
    
    def mark_messages_as_read(self, sender_id: str, receiver_id: str):
        """Отметка сообщений как прочитанные"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE messages 
                    SET is_read = TRUE
                    WHERE sender_id = ? AND receiver_id = ?
                ''', (sender_id, receiver_id))
                conn.commit()
        except Exception as e:
            print(f"Ошибка отметки сообщений: {e}")
    
    def add_contact(self, user_id: str, contact_id: str) -> bool:
        """Добавление контакта"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR IGNORE INTO contacts (user_id, contact_id)
                    VALUES (?, ?)
                ''', (user_id, contact_id))
                conn.commit()
                return True
        except Exception as e:
            print(f"Ошибка добавления контакта: {e}")
            return False
    
    def get_contacts(self, user_id: str) -> List[Dict]:
        """Получение списка контактов пользователя"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT c.contact_id, u.display_name, u.is_online, u.last_seen
                    FROM contacts c
                    JOIN users u ON c.contact_id = u.user_id
                    WHERE c.user_id = ?
                    ORDER BY u.display_name
                ''', (user_id,))
                rows = cursor.fetchall()
                return [{
                    'contact_id': row[0],
                    'display_name': row[1],
                    'is_online': bool(row[2]),
                    'last_seen': row[3]
                } for row in rows]
        except Exception as e:
            print(f"Ошибка получения контактов: {e}")
            return []
