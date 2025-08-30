import sys
import time
from datetime import datetime
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QTextEdit, 
                             QListWidget, QListWidgetItem, QSplitter, 
                             QFrame, QMessageBox, QMenu, QDialog,
                             QInputDialog, QScrollArea, QSizePolicy)
from PySide6.QtCore import Qt, Signal, QTimer, QThread, Slot
from PySide6.QtGui import QFont, QPixmap, QPalette, QColor, QIcon, QPainter, QBrush, QAction, QTextCursor
import sys
import os
# Добавляем путь к src в PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from src.config import client_config as config
except ImportError:
    # Если client_config не найден, используем встроенный config
    from src.config import config
from src.database.database import Database
from src.network.network_manager import NetworkManager
from src.audio.audio_manager import AudioManager

class ContactItem(QWidget):
    """Виджет элемента контакта в списке"""
    
    def __init__(self, contact_data: dict, parent=None):
        super().__init__(parent)
        self.contact_data = contact_data
        self.new_message_count = 0
        self.init_ui()
    
    def init_ui(self):
        """Инициализация интерфейса элемента контакта"""
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(10)
        
        # Индикатор онлайн-статуса
        self.status_indicator = QLabel()
        self.status_indicator.setFixedSize(12, 12)
        self.status_indicator.setStyleSheet("""
            QLabel {
                border-radius: 6px;
                background-color: #95a5a6;
            }
        """)
        
        # Информация о контакте
        contact_info = QVBoxLayout()
        contact_info.setSpacing(2)
        
        self.name_label = QLabel(self.contact_data.get('display_name', self.contact_data['contact_id']))
        self.name_label.setFont(QFont("Arial", 10, QFont.Bold))
        self.name_label.setStyleSheet("color: #2c3e50;")
        
        self.status_label = QLabel("Офлайн")
        self.status_label.setFont(QFont("Arial", 8))
        self.status_label.setStyleSheet("color: #7f8c8d;")
        
        contact_info.addWidget(self.name_label)
        contact_info.addWidget(self.status_label)
        
        # Индикатор новых сообщений
        self.new_message_indicator = QLabel()
        self.new_message_indicator.setFixedSize(20, 20)
        self.new_message_indicator.setStyleSheet("""
            QLabel {
                border-radius: 10px;
                background-color: #e74c3c;
                color: white;
                font-size: 10px;
                font-weight: bold;
                text-align: center;
                padding: 2px;
            }
        """)
        self.new_message_indicator.setAlignment(Qt.AlignCenter)
        self.new_message_indicator.hide()  # Скрыт по умололчанию
        
        # Кнопки действий
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(5)
        
        # Кнопка звонка
        self.call_button = QPushButton("📞")
        self.call_button.setFixedSize(30, 30)
        self.call_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 15px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)
        
        # Кнопка чата
        self.chat_button = QPushButton("💬")
        self.chat_button.setFixedSize(30, 30)
        self.chat_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 15px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1f5f8b;
            }
        """)
        
        actions_layout.addWidget(self.call_button)
        actions_layout.addWidget(self.chat_button)
        
        # Добавление всех элементов в layout
        layout.addWidget(self.status_indicator)
        layout.addLayout(contact_info)
        layout.addStretch()
        layout.addWidget(self.new_message_indicator)
        layout.addLayout(actions_layout)
        
        self.setLayout(layout)
        
        # Подключение сигналов
        self.call_button.clicked.connect(self.call_contact)
        self.chat_button.clicked.connect(self.chat_with_contact)
        
        # Обновление статуса после создания всех элементов
        self.update_status()
    
    def add_new_message_indicator(self):
        """Добавление индикатора новых сообщений"""
        self.new_message_count += 1
        self.new_message_indicator.setText(str(self.new_message_count))
        self.new_message_indicator.show()
    
    def update_new_message_indicator(self):
        """Обновление счетчика новых сообщений"""
        self.new_message_count += 1
        self.new_message_indicator.setText(str(self.new_message_count))
        self.new_message_indicator.show()
    
    def clear_new_message_indicator(self):
        """Очистка индикатора новых сообщений"""
        self.new_message_count = 0
        self.new_message_indicator.hide()
    
    def update_status(self):
        """Обновление онлайн-статуса"""
        is_online = self.contact_data.get('is_online', False)
        
        if is_online:
            self.status_indicator.setStyleSheet("""
                QLabel {
                    border-radius: 6px;
                    background-color: #27ae60;
                }
            """)
            self.status_label.setText("Онлайн")
            self.status_label.setStyleSheet("color: #27ae60; font-weight: bold;")
        else:
            self.status_indicator.setStyleSheet("""
                QLabel {
                    border-radius: 6px;
                    background-color: #95a5a6;
                }
            """)
            self.status_label.setText("Офлайн")
            self.status_label.setStyleSheet("color: #7f8c8d;")
    
    def call_contact(self):
        """Начало звонка контакта"""
        # Найти главное окно через иерархию родителей
        main_window = self.find_main_window()
        if main_window:
            main_window.start_call.emit(self.contact_data['contact_id'])
    
    def chat_with_contact(self):
        """Открытие чата с контактом"""
        # Найти главное окно через иерархию родителей
        main_window = self.find_main_window()
        if main_window:
            main_window.open_chat.emit(self.contact_data['contact_id'])
    
    def find_main_window(self):
        """Поиск главного окна через иерархию родителей"""
        parent = self.parent()
        while parent:
            if hasattr(parent, 'start_call') and hasattr(parent, 'open_chat'):
                return parent
            parent = parent.parent()
        return None

class ChatWidget(QWidget):
    """Виджет чата с конкретным пользователем"""
    
    def __init__(self, contact_id: str, database: Database, parent=None):
        super().__init__(parent)
        self.contact_id = contact_id
        self.database = database
        self.last_message_timestamp = None
        self._processed_messages = set()  # Инициализация множества обработанных сообщений
        self.init_ui()
        self.load_messages()
        
        # Таймер для автоматического обновления чата
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.check_for_new_messages)
        self.update_timer.start(config.CHAT_UPDATE_INTERVAL)  # Используем настройку из конфига
    
    def init_ui(self):
        """Инициализация интерфейса чата"""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Заголовок чата
        header_layout = QHBoxLayout()
        
        self.contact_name_label = QLabel(f"Чат с {self.contact_id}")
        self.contact_name_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.contact_name_label.setStyleSheet("color: #2c3e50;")
        
        # Кнопка звонка в заголовке
        self.header_call_button = QPushButton("📞")
        self.header_call_button.setFixedSize(30, 30)
        self.header_call_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 15px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        
        header_layout.addWidget(self.contact_name_label)
        header_layout.addStretch()
        header_layout.addWidget(self.header_call_button)
        
        # Область сообщений
        self.messages_area = QTextEdit()
        self.messages_area.setReadOnly(True)
        self.messages_area.setStyleSheet("""
            QTextEdit {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                background-color: white;
                color: #2c3e50;
                padding: 10px;
                font-family: Arial, sans-serif;
                font-size: 10px;
            }
        """)
        
        # Область ввода сообщения
        input_layout = QHBoxLayout()
        
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Введите сообщение...")
        self.message_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                padding: 8px;
                font-size: 10px;
                color: #2c3e50;
                background-color: white;
            }
        """)
        
        self.send_button = QPushButton("Отправить")
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        
        input_layout.addWidget(self.message_input)
        input_layout.addWidget(self.send_button)
        
        # Добавление элементов в layout
        layout.addLayout(header_layout)
        layout.addWidget(self.messages_area)
        layout.addLayout(input_layout)
        
        self.setLayout(layout)
        
        # Подключение сигналов
        self.send_button.clicked.connect(self.send_message)
        self.message_input.returnPressed.connect(self.send_message)
        self.header_call_button.clicked.connect(self.call_contact)
    
    def load_messages(self):
        """Загрузка истории сообщений"""
        main_window = self.find_main_window()
        if main_window:
            messages = self.database.get_messages(main_window.current_user_id, self.contact_id)
            
            for message in messages:
                self.add_message_to_chat(message)
                
            # Установка времени последнего сообщения
            if messages:
                last_message = messages[-1]
                self.last_message_timestamp = last_message.get('timestamp')
    
    def check_for_new_messages(self):
        """Проверка новых сообщений"""
        main_window = self.find_main_window()
        if not main_window:
            return
            
        # Получение новых сообщений с момента последней проверки
        if self.last_message_timestamp:
            new_messages = self.database.get_messages_since(
                main_window.current_user_id, 
                self.contact_id, 
                self.last_message_timestamp
            )
        else:
            # Если это первая проверка, загружаем все сообщения
            new_messages = self.database.get_messages(main_window.current_user_id, self.contact_id)
        
        # Добавление новых сообщений в чат (только тех, которые не были обработаны через handle_incoming_message)
        for message in new_messages:
            # Проверяем, не было ли это сообщение уже обработано
            message_key = f"{message['sender_id']}_{message['message_text']}_{message['timestamp']}"
            if not hasattr(self, '_processed_messages') or message_key not in self._processed_messages:
                self.add_message_to_chat(message)
            
        # Обновление времени последнего сообщения
        if new_messages:
            last_message = new_messages[-1]
            self.last_message_timestamp = last_message.get('timestamp')
    
    def add_message_to_chat(self, message: dict):
        """Добавление сообщения в чат"""
        sender_id = message['sender_id']
        message_text = message['message_text']
        timestamp = message['timestamp']
        
        # Проверка на дублирование сообщений (упрощенная)
        message_key = f"{sender_id}_{message_text}_{timestamp}"
        if not hasattr(self, '_processed_messages'):
            self._processed_messages = set()
        
        if message_key in self._processed_messages:
            return  # Сообщение уже обработано
        
        self._processed_messages.add(message_key)
        
        # Ограничиваем размер множества обработанных сообщений
        if len(self._processed_messages) > 100:
            self._processed_messages.clear()
        
        # Форматирование времени
        try:
            if isinstance(timestamp, str):
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            else:
                dt = datetime.fromtimestamp(timestamp)
            time_str = dt.strftime("%H:%M")
        except:
            time_str = str(timestamp)
        
        # Определение стиля сообщения
        main_window = self.find_main_window()
        if not main_window:
            print("Ошибка: не удалось найти главное окно")
            return
            
        # Надёжное определение собственного сообщения
        current_user_id = main_window.current_user_id
        print(f"Текущий пользователь: '{current_user_id}' (тип: {type(current_user_id)})")
        
        # Детальное сравнение
        sender_clean = str(sender_id).strip()
        current_clean = str(current_user_id).strip()
        direct_comparison = (sender_id == current_user_id)
        string_comparison = (sender_clean == current_clean)
        
        print(f"Прямое сравнение: {sender_id} == {current_user_id} = {direct_comparison}")
        print(f"Строковое сравнение: '{sender_clean}' == '{current_clean}' = {string_comparison}")
        
        is_own_message = string_comparison
        
        print(f"Итоговое решение: собственное сообщение = {is_own_message}")
        
        if is_own_message:
            # Собственное сообщение (справа)
            print(f"✓ Отображаем СОБСТВЕННОЕ сообщение СПРАВА")
            message_html = f"""
                <div style="text-align: right; margin: 5px 0;">
                    <div style="display: inline-block; max-width: 70%; background-color: #3498db; color: white; 
                                padding: 8px 12px; border-radius: 15px; text-align: left;">
                        {message_text}
                    </div>
                    <div style="font-size: 8px; color: #7f8c8d; margin-top: 2px;">{time_str}</div>
                </div>
            """
        else:
            # Сообщение собеседника (слева)
            print(f"✓ Отображаем сообщение СОБЕСЕДНИКА СЛЕВА")
            message_html = f"""
                <div style="text-align: left; margin: 5px 0;">
                    <div style="display: inline-block; max-width: 70%; background-color: #ecf0f1; color: #2c3e50; 
                                padding: 8px 12px; border-radius: 15px;">
                        {message_text}
                    </div>
                    <div style="font-size: 8px; color: #7f8c8d; margin-top: 2px;">{time_str}</div>
                </div>
            """
        
        # Немедленное добавление в область сообщений
        self.messages_area.append(message_html)
        
        # Прокрутка к последнему сообщению
        self.messages_area.ensureCursorVisible()
        
        # Обновление времени последнего сообщения для следующей проверки
        self.last_message_timestamp = timestamp
        
        print(f"Сообщение успешно добавлено в чат")
        print(f"=== КОНЕЦ ОТЛАДКИ ===")
    
    def send_message(self):
        """Отправка сообщения"""
        message_text = self.message_input.text().strip()
        
        if not message_text:
            return
        
        main_window = self.find_main_window()
        if not main_window:
            return
        
        # Надёжное получение ID текущего пользователя
        current_user_id = main_window.current_user_id
        if not current_user_id:
            print("Ошибка: не удалось определить ID текущего пользователя")
            return
        
        # Очистка поля ввода
        self.message_input.clear()
        
        # Создание сообщения
        message = {
            'sender_id': current_user_id,
            'receiver_id': self.contact_id,
            'message_text': message_text,
            'timestamp': datetime.now().isoformat()
        }
        
        # Отправка через сеть (если подключены)
        if hasattr(main_window, 'network_manager'):
            network_message = {
                'type': 'message',
                'sender_id': message['sender_id'],
                'receiver_id': message['receiver_id'],
                'message_text': message['message_text']
            }
            main_window.network_manager.send_client_message(network_message)
        else:
            print("Ошибка: сетевой менеджер не найден")
    
    def call_contact(self):
        """Начало звонка контакту"""
        # Найти главное окно через иерархию родителей
        main_window = self.find_main_window()
        if main_window:
            main_window.start_call.emit(self.contact_id)
    
    def find_main_window(self):
        """Поиск главного окна через иерархию родителей"""
        parent = self.parent()
        while parent:
            if hasattr(parent, 'start_call') and hasattr(parent, 'open_chat'):
                return parent
            parent = parent.parent()
        return None
    
    def closeEvent(self, event):
        """Обработка закрытия виджета чата"""
        if hasattr(self, 'update_timer'):
            self.update_timer.stop()
        event.accept()

class MainWindow(QMainWindow):
    """Главное окно мессенджера"""
    
    # Сигналы
    start_call = Signal(str)
    open_chat = Signal(str)
    
    def __init__(self, user_id: str):
        super().__init__()
        
        try:
            self.current_user_id = user_id
            self.database = Database()
            self.network_manager = None
            self.audio_manager = None
            self.current_chat = None
            
            self.init_ui()
            self.setup_network()
            self.setup_audio()
            self.load_contacts()
            
            # Подключение сигналов
            self.start_call.connect(self.handle_call_request)
            self.open_chat.connect(self.handle_chat_request)
            
            # Таймер для обновления статуса контактов
            self.contacts_update_timer = QTimer()
            self.contacts_update_timer.timeout.connect(self.update_contacts_status)
            self.contacts_update_timer.start(config.CONTACTS_UPDATE_INTERVAL)  # Используем настройку из конфига
            
        except Exception as e:
            print(f"Ошибка инициализации MainWindow: {e}")
            raise
    
    def init_ui(self):
        """Инициализация пользовательского интерфейса"""
        self.setWindowTitle(f"{config.APP_NAME} - {self.current_user_id}")
        self.setGeometry(100, 100, 1000, 700)
        
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Основной layout
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Создание сплиттера для разделения панелей
        splitter = QSplitter(Qt.Horizontal)
        
        # Левая панель - список контактов
        self.contacts_panel = self.create_contacts_panel()
        
        # Правая панель - чат
        self.chat_panel = self.create_chat_panel()
        
        # Добавление панелей в сплиттер
        splitter.addWidget(self.contacts_panel)
        splitter.addWidget(self.chat_panel)
        
        # Установка пропорций панелей
        splitter.setSizes([300, 700])
        
        main_layout.addWidget(splitter)
        central_widget.setLayout(main_layout)
        
        # Применение стилей
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ecf0f1;
            }
            QTextEdit {
                color: #2c3e50;
                background-color: white;
            }
            QLineEdit {
                color: #2c3e50;
                background-color: white;
            }
            QLabel {
                color: #2c3e50;
            }
        """)
    
    def create_contacts_panel(self):
        """Создание панели контактов"""
        panel = QWidget()
        panel.setStyleSheet("""
            QWidget {
                background-color: white;
                border-right: 1px solid #bdc3c7;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Заголовок панели
        header = QLabel("Контакты")
        header.setAlignment(Qt.AlignCenter)
        header.setFont(QFont("Arial", 14, QFont.Bold))
        header.setStyleSheet("""
            QLabel {
                background-color: #3498db;
                color: white;
                padding: 15px;
                border-bottom: 1px solid #2980b9;
            }
        """)
        
        # Список контактов
        self.contacts_list = QListWidget()
        self.contacts_list.setStyleSheet("""
            QListWidget {
                border: none;
                background-color: white;
            }
            QListWidget::item {
                border-bottom: 1px solid #ecf0f1;
                padding: 5px;
            }
            QListWidget::item:selected {
                background-color: #ecf0f1;
            }
        """)
        
        # Кнопка добавления контакта
        add_contact_button = QPushButton("+ Добавить контакт")
        add_contact_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 10px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        add_contact_button.clicked.connect(self.add_contact)
        
        # Добавление элементов в layout
        layout.addWidget(header)
        layout.addWidget(self.contacts_list)
        layout.addWidget(add_contact_button)
        
        panel.setLayout(layout)
        return panel
    
    def create_chat_panel(self):
        """Создание панели чата"""
        panel = QWidget()
        panel.setStyleSheet("""
            QWidget {
                background-color: white;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Заголовок чата
        self.chat_header = QLabel("Выберите контакт для начала чата")
        self.chat_header.setAlignment(Qt.AlignCenter)
        self.chat_header.setFont(QFont("Arial", 14, QFont.Bold))
        self.chat_header.setStyleSheet("""
            QLabel {
                background-color: #34495e;
                color: white;
                padding: 20px;
                border-bottom: 1px solid #2c3e50;
            }
        """)
        
        # Область чата
        self.chat_area = QWidget()
        self.chat_area.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
            }
        """)
        
        # Создание виджета приветствия
        welcome_widget = QWidget()
        welcome_layout = QVBoxLayout()
        welcome_layout.setAlignment(Qt.AlignCenter)
        
        welcome_label = QLabel("Добро пожаловать в чат!")
        welcome_label.setFont(QFont("Arial", 16))
        welcome_label.setStyleSheet("color: #7f8c8d;")
        welcome_label.setAlignment(Qt.AlignCenter)
        
        instruction_label = QLabel("Выберите контакт из списка слева для начала общения")
        instruction_label.setFont(QFont("Arial", 12))
        instruction_label.setStyleSheet("color: #95a5a6;")
        instruction_label.setAlignment(Qt.AlignCenter)
        instruction_label.setWordWrap(True)
        
        welcome_layout.addWidget(welcome_label)
        welcome_layout.addWidget(instruction_label)
        welcome_widget.setLayout(welcome_layout)
        
        # Установка приветственного виджета
        self.chat_area_layout = QVBoxLayout()
        self.chat_area_layout.addWidget(welcome_widget)
        self.chat_area.setLayout(self.chat_area_layout)
        
        # Добавление элементов в layout
        layout.addWidget(self.chat_header)
        layout.addWidget(self.chat_area)
        
        panel.setLayout(layout)
        return panel
    
    def setup_network(self):
        """Настройка сетевого подключения"""
        try:
            self.network_manager = NetworkManager(self.database)
            
            # Установка обработчика входящих сообщений
            self.network_manager.message_callback = self.handle_incoming_message
            
            # Попытка подключения к серверу
            if self.network_manager.connect_to_server(config.SERVER_HOST, config.SERVER_PORT):
                print(f"Подключение к серверу {config.SERVER_HOST}:{config.SERVER_PORT} установлено")
                
                # Отправка информации о статусе
                status_message = {
                    'type': 'status_update',
                    'user_id': self.current_user_id,
                    'is_online': True
                }
                self.network_manager.send_client_message(status_message)
                
                # Запрос списка пользователей
                user_list_request = {
                    'type': 'user_list_request',
                    'user_id': self.current_user_id
                }
                self.network_manager.send_client_message(user_list_request)
                
            else:
                print("Не удалось подключиться к серверу")
                
        except Exception as e:
            print(f"Ошибка настройки сети: {e}")
    
    def handle_incoming_message(self, message: dict):
        """Обработка входящих сообщений от сервера"""
        message_type = message.get('type')
        
        if message_type == 'message':
            # Обработка текстового сообщения
            sender_id = message.get('sender_id')
            receiver_id = message.get('receiver_id')
            message_text = message.get('message_text')
            timestamp = message.get('timestamp', time.time())
            
            # Надёжная проверка на собственные сообщения
            current_user_id = self.current_user_id
            
            # Детальное сравнение
            sender_clean = str(sender_id).strip()
            current_clean = str(current_user_id).strip()
            is_own_message = (sender_clean == current_clean)
            
                        # Сохранение сообщения в БД
            if sender_id and receiver_id and message_text:
                self.database.add_message(sender_id, receiver_id, message_text)
                
                # Немедленное обновление активного чата, если это относится к текущему чату
                if self.current_chat and hasattr(self.current_chat, 'contact_id'):
                    chat_contact_id = self.current_chat.contact_id
                    
                    # Показываем сообщение, если:
                    # 1. Это сообщение от контакта к нам
                    # 2. Это наше сообщение к контакту
                    if ((sender_id == chat_contact_id and receiver_id == self.current_user_id) or
                        (sender_id == self.current_user_id and receiver_id == chat_contact_id)):
                        
                        message_data = {
                            'sender_id': sender_id,
                            'receiver_id': receiver_id,
                            'message_text': message_text,
                            'timestamp': datetime.fromtimestamp(timestamp).isoformat()
                        }
                        
                        # Немедленно добавляем сообщение в чат
                        self.current_chat.add_message_to_chat(message_data)
                        
                        # Обновление времени последнего сообщения в чате
                        self.current_chat.last_message_timestamp = message_data['timestamp']
                        
                        # Воспроизведение звука уведомления только для входящих сообщений
                        if (sender_id != self.current_user_id and 
                            self.audio_manager and 
                            config.ENABLE_SOUND_NOTIFICATIONS):
                            try:
                                self.audio_manager.play_notification_sound()
                            except:
                                pass  # Игнорируем ошибки воспроизведения звука
                
                # Обновление индикатора новых сообщений в списке контактов
                if config.ENABLE_VISUAL_NOTIFICATIONS:
                    self.update_contact_message_indicator(sender_id, receiver_id)
        
        elif message_type == 'user_list_response':
            # Обновление списка пользователей
            users = message.get('users', [])
            # Можно добавить логику обновления онлайн-статуса контактов
            pass
    
    def update_contact_message_indicator(self, sender_id: str, receiver_id: str):
        """Обновление индикатора новых сообщений в списке контактов"""
        try:
            # Определяем, какой контакт отправил сообщение
            contact_id = sender_id if sender_id != self.current_user_id else receiver_id
            
            # Обновляем индикатор в списке контактов
            for i in range(self.contacts_list.count()):
                item = self.contacts_list.item(i)
                contact_widget = self.contacts_list.itemWidget(item)
                
                if (hasattr(contact_widget, 'contact_data') and 
                    contact_widget.contact_data['contact_id'] == contact_id):
                    
                    # Добавляем индикатор новых сообщений
                    if not hasattr(contact_widget, 'new_message_indicator'):
                        contact_widget.add_new_message_indicator()
                    else:
                        contact_widget.update_new_message_indicator()
                    break
                    
        except Exception as e:
            print(f"Ошибка обновления индикатора сообщений: {e}")
    
    def setup_audio(self):
        """Настройка аудио"""
        try:
            self.audio_manager = AudioManager()
            print("Аудио менеджер инициализирован")
        except Exception as e:
            print(f"Ошибка инициализации аудио: {e}")
    
    def load_contacts(self):
        """Загрузка списка контактов"""
        try:
            # Получение всех пользователей (кроме текущего)
            all_users = self.database.get_all_users()
            contacts = [user for user in all_users if user['user_id'] != self.current_user_id]
            
            # Очистка списка
            self.contacts_list.clear()
            
            # Добавление контактов
            for contact in contacts:
                # Преобразование данных пользователя в формат контакта
                contact_data = {
                    'contact_id': contact['user_id'],
                    'display_name': contact.get('display_name', contact['user_id']),
                    'is_online': contact.get('is_online', False)
                }
                
                # Создание виджета контакта
                contact_widget = ContactItem(contact_data)
                
                # Создание элемента списка
                item = QListWidgetItem()
                item.setSizeHint(contact_widget.sizeHint())
                
                self.contacts_list.addItem(item)
                self.contacts_list.setItemWidget(item, contact_widget)
                
                # Обновление статуса
                contact_widget.update_status()
            
            print(f"Загружено {len(contacts)} контактов")
            
        except Exception as e:
            print(f"Ошибка загрузки контактов: {e}")
    
    def add_contact(self):
        """Добавление нового контакта"""
        try:
            contact_id, ok = QInputDialog.getText(
                self, 
                "Добавить контакт", 
                "Введите ID пользователя:"
            )
            
            if ok and contact_id.strip():
                contact_id = contact_id.strip()
                
                # Проверка существования пользователя
                user = self.database.get_user(contact_id)
                
                if user:
                    # Добавление в контакты
                    self.database.add_contact(self.current_user_id, contact_id)
                    
                    # Перезагрузка списка контактов
                    self.load_contacts()
                    
                    QMessageBox.information(
                        self, 
                        "Успех", 
                        f"Контакт {contact_id} добавлен!"
                    )
                else:
                    QMessageBox.warning(
                        self, 
                        "Ошибка", 
                        f"Пользователь {contact_id} не найден"
                    )
                    
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Ошибка", 
                f"Ошибка при добавлении контакта: {str(e)}"
            )
    
    def handle_call_request(self, contact_id: str):
        """Обработка запроса на звонок"""
        try:
            reply = QMessageBox.question(
                self,
                "Голосовой звонок",
                f"Начать звонок с {contact_id}?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if reply == QMessageBox.Yes:
                self.start_voice_call(contact_id)
                
        except Exception as e:
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Ошибка при начале звонка: {str(e)}"
            )
    
    def start_voice_call(self, contact_id: str):
        """Начало голосового звонка"""
        try:
            if self.audio_manager:
                # Простой порт для аудио (в реальном приложении нужна более сложная логика)
                audio_port = 5001
                
                # Начало звонка
                success = self.audio_manager.start_audio_call(
                    config.HOST, 
                    audio_port, 
                    is_caller=True
                )
                
                if success:
                    QMessageBox.information(
                        self,
                        "Звонок",
                        f"Звонок с {contact_id} начат. Нажмите OK для завершения."
                    )
                    
                    # Завершение звонка
                    self.audio_manager.stop_audio_call()
                else:
                    QMessageBox.warning(
                        self,
                        "Ошибка",
                        "Не удалось начать звонок"
                    )
            else:
                QMessageBox.warning(
                    self,
                    "Ошибка",
                    "Аудио не инициализировано"
                )
                
        except Exception as e:
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Ошибка при звонке: {str(e)}"
            )
    
    def handle_chat_request(self, contact_id: str):
        """Обработка запроса на открытие чата"""
        try:
            # Обновление заголовка чата
            self.chat_header.setText(f"Чат с {contact_id}")
            
            # Очистка области чата
            for i in reversed(range(self.chat_area_layout.count())):
                child = self.chat_area_layout.itemAt(i).widget()
                if child:
                    child.deleteLater()
            
            # Создание виджета чата
            chat_widget = ChatWidget(contact_id, self.database, self.chat_area)
            self.chat_area_layout.addWidget(chat_widget)
            
            # Сохранение ссылки на текущий чат
            self.current_chat = chat_widget
            
            # Очистка индикатора новых сообщений для этого контакта
            self.clear_contact_message_indicator(contact_id)
            
            print(f"Чат с {contact_id} открыт")
            print(f"Текущий пользователь: {self.current_user_id}")
            
        except Exception as e:
            print(f"Ошибка открытия чата: {e}")
    
    def clear_contact_message_indicator(self, contact_id: str):
        """Очистка индикатора новых сообщений для конкретного контакта"""
        try:
            for i in range(self.contacts_list.count()):
                item = self.contacts_list.item(i)
                contact_widget = self.contacts_list.itemWidget(item)
                
                if (hasattr(contact_widget, 'contact_data') and 
                    contact_widget.contact_data['contact_id'] == contact_id):
                    
                    if hasattr(contact_widget, 'clear_new_message_indicator'):
                        contact_widget.clear_new_message_indicator()
                    break
                    
        except Exception as e:
            print(f"Ошибка очистки индикатора сообщений: {e}")
    
    def update_contacts_status(self):
        """Обновление статуса контактов"""
        try:
            # Получение актуального статуса пользователей из БД
            all_users = self.database.get_all_users()
            user_statuses = {user['user_id']: user.get('is_online', False) for user in all_users}
            
            # Обновление статуса в списке контактов
            for i in range(self.contacts_list.count()):
                item = self.contacts_list.item(i)
                contact_widget = self.contacts_list.itemWidget(item)
                
                if hasattr(contact_widget, 'contact_data'):
                    contact_id = contact_widget.contact_data['contact_id']
                    new_status = user_statuses.get(contact_id, False)
                    
                    # Обновление статуса только если он изменился
                    if contact_widget.contact_data.get('is_online') != new_status:
                        contact_widget.contact_data['is_online'] = new_status
                        contact_widget.update_status()
                        
        except Exception as e:
            print(f"Ошибка обновления статуса контактов: {e}")
    
    def closeEvent(self, event):
        """Обработка закрытия окна"""
        try:
            # Остановка таймеров
            if hasattr(self, 'contacts_update_timer'):
                self.contacts_update_timer.stop()
            
            # Отправка статуса офлайн
            if self.network_manager:
                status_message = {
                    'type': 'status_update',
                    'user_id': self.current_user_id,
                    'is_online': False
                }
                self.network_manager.send_client_message(status_message)
                self.network_manager.stop_server()
            
            # Очистка аудио
            if self.audio_manager:
                self.audio_manager.cleanup()
            
            # Обновление статуса в БД
            self.database.update_user_status(self.current_user_id, False)
            
        except Exception as e:
            print(f"Ошибка при закрытии: {e}")
        
        event.accept()
