import sys
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QMessageBox, QFrame)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap, QPalette, QColor
import config
from database import Database

class AuthWindow(QWidget):
    """Окно аутентификации пользователя"""
    
    # Сигнал успешной аутентификации
    auth_successful = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.database = Database()
        self.init_ui()
        
    def init_ui(self):
        """Инициализация пользовательского интерфейса"""
        self.setWindowTitle(f"{config.APP_NAME} - Вход")
        self.setFixedSize(400, 300)
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint)
        
        # Центрирование окна
        self.center_window()
        
        # Основной layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(40, 40, 40, 40)
        
        # Заголовок приложения
        title_label = QLabel(config.APP_NAME)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        
        # Подзаголовок
        subtitle_label = QLabel("Войдите в систему, используя ваш ID")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setFont(QFont("Arial", 10))
        subtitle_label.setStyleSheet("color: #7f8c8d; margin-bottom: 20px;")
        
        # Форма входа
        form_frame = QFrame()
        form_frame.setFrameStyle(QFrame.Box)
        form_frame.setStyleSheet("""
            QFrame {
                border: 2px solid #bdc3c7;
                border-radius: 10px;
                background-color: #f8f9fa;
                padding: 20px;
            }
        """)
        
        form_layout = QVBoxLayout()
        form_layout.setSpacing(15)
        
        # Поле для ввода ID пользователя
        user_id_label = QLabel("ID пользователя:")
        user_id_label.setFont(QFont("Arial", 10, QFont.Bold))
        user_id_label.setStyleSheet("color: #2c3e50;")
        
        self.user_id_input = QLineEdit()
        self.user_id_input.setPlaceholderText("Введите ваш уникальный ID")
        self.user_id_input.setFont(QFont("Arial", 11))
        self.user_id_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                padding: 10px;
                font-size: 11px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
        
        # Кнопка входа
        self.login_button = QPushButton("Войти")
        self.login_button.setFont(QFont("Arial", 12, QFont.Bold))
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 12px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1f5f8b;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        self.login_button.clicked.connect(self.login)
        
        # Кнопка создания нового пользователя
        self.create_user_button = QPushButton("Создать нового пользователя")
        self.create_user_button.setFont(QFont("Arial", 10))
        self.create_user_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #3498db;
                border: 1px solid #3498db;
                border-radius: 5px;
                padding: 8px;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #3498db;
                color: white;
            }
        """)
        self.create_user_button.clicked.connect(self.create_new_user)
        
        # Добавление элементов в форму
        form_layout.addWidget(user_id_label)
        form_layout.addWidget(self.user_id_input)
        form_layout.addWidget(self.login_button)
        form_layout.addWidget(self.create_user_button)
        
        form_frame.setLayout(form_layout)
        
        # Информация о тестовых пользователях
        info_frame = QFrame()
        info_frame.setFrameStyle(QFrame.Box)
        info_frame.setStyleSheet("""
            QFrame {
                border: 1px solid #ecf0f1;
                border-radius: 5px;
                background-color: #ecf0f1;
                padding: 15px;
            }
        """)
        
        info_layout = QVBoxLayout()
        
        info_label = QLabel("Тестовые пользователи:")
        info_label.setFont(QFont("Arial", 9, QFont.Bold))
        info_label.setStyleSheet("color: #2c3e50; margin-bottom: 5px;")
        
        test_users_text = ", ".join(config.DEFAULT_USERS)
        test_users_label = QLabel(test_users_text)
        test_users_label.setFont(QFont("Arial", 9))
        test_users_label.setStyleSheet("color: #7f8c8d;")
        test_users_label.setWordWrap(True)
        
        info_layout.addWidget(info_label)
        info_layout.addWidget(test_users_label)
        info_frame.setLayout(info_layout)
        
        # Добавление всех элементов в основной layout
        main_layout.addWidget(title_label)
        main_layout.addWidget(subtitle_label)
        main_layout.addWidget(form_frame)
        main_layout.addWidget(info_frame)
        
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
                background-color: #ecf0f1;
                font-family: Arial, sans-serif;
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
        
        # Проверка существования пользователя
        user = self.database.get_user(user_id)
        
        if user:
            # Пользователь существует - вход выполнен
            self.database.update_user_status(user_id, True)
            QMessageBox.information(self, "Успех", f"Добро пожаловать, {user_id}!")
            self.auth_successful.emit(user_id)
            self.close()
        else:
            # Пользователь не существует - предложение создать
            reply = QMessageBox.question(
                self, 
                "Пользователь не найден", 
                f"Пользователь '{user_id}' не существует. Хотите создать новый профиль?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if reply == QMessageBox.Yes:
                self.create_user_profile(user_id)
    
    def create_new_user(self):
        """Создание нового пользователя"""
        user_id = self.user_id_input.text().strip()
        
        if not user_id:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, введите ID пользователя")
            return
        
        self.create_user_profile(user_id)
    
    def create_user_profile(self, user_id: str):
        """Создание профиля пользователя"""
        try:
            # Создание пользователя в БД
            success = self.database.add_user(user_id)
            
            if success:
                # Обновление статуса
                self.database.update_user_status(user_id, True)
                
                QMessageBox.information(
                    self, 
                    "Профиль создан", 
                    f"Профиль пользователя '{user_id}' успешно создан!"
                )
                
                # Автоматический вход
                self.auth_successful.emit(user_id)
                self.close()
            else:
                QMessageBox.critical(
                    self, 
                    "Ошибка", 
                    "Не удалось создать профиль пользователя"
                )
                
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Ошибка", 
                f"Ошибка при создании профиля: {str(e)}"
            )
    
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
