import sys
import os
import json
import socket
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QMessageBox, QFrame)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont, QPixmap, QPalette, QColor

# Добавляем путь к корню проекта в PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(current_dir, '..', '..')
sys.path.insert(0, project_root)

try:
    from src.config import client_config as config
except ImportError:
    # Если client_config не найден, используем встроенный config
    from src.config import config

class AuthWindow(QWidget):
    """Окно аутентификации пользователя"""
    
    # Сигнал успешной аутентификации
    auth_successful = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.socket = None
        self.init_ui()
        
    def init_ui(self):
        """Инициализация пользовательского интерфейса"""
        self.setWindowTitle(f"{config.APP_NAME} - Вход")
        self.setFixedSize(500, 480)
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint)
        
        # Центрирование окна
        self.center_window()
        
        # Основной layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(45, 40, 45, 40)
        
        # Иконка приложения
        icon_label = QLabel()
        icon_label.setFixedSize(72, 72)
        icon_label.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #4facfe, stop:1 #00f2fe);
                border-radius: 36px;
                color: white;
                font-size: 36px;
                font-weight: bold;
                border: 3px solid #ffffff;
            }
        """)
        icon_label.setText("A")
        icon_label.setAlignment(Qt.AlignCenter)
        
        # Заголовок приложения
        title_label = QLabel(config.APP_NAME)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Segoe UI", 22, QFont.Bold))
        title_label.setStyleSheet("""
            color: #2c3e50; 
            margin-bottom: 15px;
            font-weight: 700;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
        """)
        
        # Подзаголовок
        subtitle_label = QLabel("Войдите в систему, используя ваш ID\n(новые пользователи создаются автоматически)")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setFont(QFont("Segoe UI", 10))
        subtitle_label.setStyleSheet("""
            color: #7f8c8d; 
            margin-bottom: 30px;
            line-height: 1.4;
        """)
        
        # Поле для ввода ID пользователя
        user_id_label = QLabel("ID пользователя")
        user_id_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        user_id_label.setStyleSheet("""
            color: #2c3e50; 
            margin-bottom: 8px;
            font-weight: 600;
        """)
        
        self.user_id_input = QLineEdit()
        self.user_id_input.setPlaceholderText("Введите ID: user1, user2, user3, admin, test")
        self.user_id_input.setFont(QFont("Segoe UI", 12))
        self.user_id_input.setFixedHeight(45)
        self.user_id_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e8f4fd;
                border-radius: 10px;
                padding: 14px 18px;
                font-size: 12px;
                background-color: #fafbfc;
                color: #2c3e50;
                selection-background-color: #3498db;
            }
            QLineEdit:focus {
                border-color: #4facfe;
                background-color: white;
            }
            QLineEdit:hover {
                border-color: #4facfe;
                background-color: white;
            }
        """)
        
        # Кнопка входа
        self.login_button = QPushButton("Войти в систему")
        self.login_button.setFont(QFont("Segoe UI", 13, QFont.Bold))
        self.login_button.setFixedHeight(50)
        self.login_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #4facfe, stop:1 #00f2fe);
                color: white;
                border: none;
                border-radius: 10px;
                padding: 14px 28px;
                font-size: 13px;
                font-weight: 600;
                min-height: 50px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #00f2fe, stop:1 #4facfe);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #00d4e6, stop:1 #3d9bfe);
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        self.login_button.clicked.connect(self.login)
        
        # Добавление элементов в основной layout
        main_layout.addWidget(icon_label, alignment=Qt.AlignCenter)
        main_layout.addWidget(title_label)
        main_layout.addWidget(subtitle_label)
        main_layout.addWidget(user_id_label)
        main_layout.addWidget(self.user_id_input)
        
        # Подсказка о разрешенных пользователях
        hint_label = QLabel("Разрешенные ID: user1, user2, user3, admin, test")
        hint_label.setFont(QFont("Segoe UI", 10))
        hint_label.setStyleSheet("""
            color: #7f8c8d;
            margin-top: 5px;
            font-style: italic;
        """)
        hint_label.setAlignment(Qt.AlignCenter)
        
        main_layout.addWidget(hint_label)
        main_layout.addSpacing(20)
        main_layout.addWidget(self.login_button)
        
        # Добавление растягивающегося пространства
        main_layout.addStretch()
        
        self.setLayout(main_layout)
        
        # Подключение Enter к кнопке входа
        self.user_id_input.returnPressed.connect(self.login)
        
        # Установка фокуса на поле ввода
        self.user_id_input.setFocus()
        
        # Применение стилей к окну
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #ffffff, stop:1 #f8f9fa);
                font-family: "Segoe UI", "Arial", sans-serif;
            }
        """)
    
    def center_window(self):
        """Центрирование окна на экране"""
        screen = self.screen()
        screen_geometry = screen.geometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)
    
    def login(self):
        """Обработка входа пользователя"""
        user_id = self.user_id_input.text().strip()
        
        if not user_id:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, введите ID пользователя")
            return
        
        # Подключение к серверу для аутентификации
        if self.connect_to_server():
            # Отправка запроса аутентификации
            auth_request = {
                'type': 'auth_request',
                'user_id': user_id
            }
            
            try:
                self.send_message(auth_request)
                
                # Ждем ответ от сервера
                response = self.receive_message()
                
                if response and response.get('success'):
                    QMessageBox.information(self, "Успех", f"Добро пожаловать, {user_id}!")
                    self.auth_successful.emit(user_id)
                    # НЕ закрываем соединение здесь - оно нужно для работы мессенджера
                else:
                    error_msg = response.get('message', 'Ошибка аутентификации') if response else 'Нет ответа от сервера'
                    QMessageBox.critical(self, "Ошибка", f"Ошибка аутентификации: {error_msg}")
                    self.disconnect_from_server()
                    
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка при аутентификации: {str(e)}")
                self.disconnect_from_server()
        else:
            QMessageBox.critical(self, "Ошибка", "Не удалось подключиться к серверу")
    
    def connect_to_server(self):
        """Подключение к серверу"""
        try:
            print(f"Подключение к серверу {config.SERVER_HOST}:{config.SERVER_PORT}...")
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10)  # 10 секунд таймаут
            self.socket.connect((config.SERVER_HOST, config.SERVER_PORT))
            print("✓ Подключение к серверу установлено")
            return True
        except Exception as e:
            print(f"Ошибка подключения к серверу: {e}")
            return False
    
    def disconnect_from_server(self):
        """Отключение от сервера"""
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
    
    def send_message(self, message):
        """Отправка сообщения на сервер"""
        if self.socket:
            try:
                data = json.dumps(message).encode('utf-8')
                self.socket.send(data)
                print(f"Отправлено на сервер: {message}")
            except Exception as e:
                print(f"Ошибка отправки сообщения: {e}")
                raise
    
    def receive_message(self):
        """Получение ответа от сервера"""
        if self.socket:
            try:
                print("Ожидание ответа от сервера...")
                data = self.socket.recv(4096)
                if data:
                    response = json.loads(data.decode('utf-8'))
                    print(f"Получен ответ от сервера: {response}")
                    return response
                else:
                    print("Сервер закрыл соединение")
                    return None
            except socket.timeout:
                print("Таймаут ожидания ответа от сервера")
                return None
            except Exception as e:
                print(f"Ошибка получения ответа: {e}")
                return None
        return None
    

    
    def keyPressEvent(self, event):
        """Обработка нажатий клавиш"""
        if event.key() == Qt.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)
    
    def closeEvent(self, event):
        """Обработка закрытия окна"""
        # Если окно закрывается без входа, завершаем приложение
        if not hasattr(self, 'auth_successful'):
            sys.exit(0)
        event.accept()
