import socket
import json
import threading
import time
from typing import Dict, List, Callable, Optional
import config
from database import Database

class NetworkManager:
    def __init__(self, database: Database):
        self.database = database
        self.socket = None
        self.is_running = False
        self.connected_users = {}  # user_id -> (socket, address)
        self.message_handlers = {}
        self.heartbeat_thread = None
        self.current_user_id = None
        self.message_callback = None  # Callback для обработки сообщений на клиенте
        
        # Регистрация обработчиков сообщений
        self.register_message_handlers()
    
    def register_message_handlers(self):
        """Регистрация обработчиков различных типов сообщений"""
        self.message_handlers = {
            'message': self.handle_text_message,
            'status_update': self.handle_status_update,
            'heartbeat': self.handle_heartbeat,
            'call_request': self.handle_call_request,
            'call_response': self.handle_call_response,
            'call_end': self.handle_call_end,
            'user_list_request': self.handle_user_list_request,
            'user_list_response': self.handle_user_list_response
        }
    
    def start_server(self, host: str = None, port: int = None):
        """Запуск сервера"""
        host = host or config.HOST
        port = port or config.PORT
        
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((host, port))
            self.socket.listen(5)
            self.is_running = True
            
            print(f"Сервер запущен на {host}:{port}")
            
            # Запуск потока для принятия подключений
            accept_thread = threading.Thread(target=self.accept_connections)
            accept_thread.daemon = True
            accept_thread.start()
            
            # Запуск потока для heartbeat
            self.heartbeat_thread = threading.Thread(target=self.heartbeat_loop)
            self.heartbeat_thread.daemon = True
            self.heartbeat_thread.start()
            
            return True
        except Exception as e:
            print(f"Ошибка запуска сервера: {e}")
            return False
    
    def accept_connections(self):
        """Принятие входящих подключений"""
        while self.is_running:
            try:
                client_socket, address = self.socket.accept()
                print(f"Новое подключение от {address}")
                
                # Запуск потока для обработки клиента
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, address)
                )
                client_thread.daemon = True
                client_thread.start()
                
            except Exception as e:
                if self.is_running:
                    print(f"Ошибка принятия подключения: {e}")
    
    def handle_client(self, client_socket: socket.socket, address: tuple):
        """Обработка клиентского подключения"""
        try:
            while self.is_running:
                data = client_socket.recv(4096)
                if not data:
                    break
                
                try:
                    message = json.loads(data.decode('utf-8'))
                    self.process_message(message, client_socket, address)
                except json.JSONDecodeError:
                    print(f"Ошибка декодирования JSON от {address}")
                    
        except Exception as e:
            print(f"Ошибка обработки клиента {address}: {e}")
        finally:
            # Удаление пользователя из списка подключенных
            for user_id, (sock, addr) in list(self.connected_users.items()):
                if sock == client_socket:
                    del self.connected_users[user_id]
                    self.database.update_user_status(user_id, False)
                    print(f"Пользователь {user_id} отключился")
                    break
            
            client_socket.close()
    
    def process_message(self, message: Dict, client_socket: socket.socket, address: tuple):
        """Обработка входящего сообщения"""
        message_type = message.get('type')
        handler = self.message_handlers.get(message_type)
        
        if handler:
            handler(message, client_socket, address)
        else:
            print(f"Неизвестный тип сообщения: {message_type}")
    
    def handle_text_message(self, message: Dict, client_socket: socket.socket, address: tuple):
        """Обработка текстового сообщения"""
        sender_id = message.get('sender_id')
        receiver_id = message.get('receiver_id')
        message_text = message.get('message_text')
        
        print(f"Сервер получил сообщение: {sender_id} -> {receiver_id}: {message_text}")
        print(f"Подключенные пользователи: {list(self.connected_users.keys())}")
        
        if sender_id and receiver_id and message_text:
            # Сохранение сообщения в БД
            self.database.add_message(sender_id, receiver_id, message_text)
            print(f"Сообщение сохранено в БД")
            
            # Подготовка ответа
            response = {
                'type': 'message',
                'sender_id': sender_id,
                'receiver_id': receiver_id,
                'message_text': message_text,
                'timestamp': time.time()
            }
            
            # Отправка сообщения отправителю (для отображения в его чате)
            if sender_id in self.connected_users:
                sender_socket, _ = self.connected_users[sender_id]
                self.send_message(sender_socket, response)
                print(f"Сообщение отправлено отправителю {sender_id}")
            else:
                print(f"Отправитель {sender_id} не найден в подключенных пользователях")
            
            # Пересылка сообщения получателю
            if receiver_id in self.connected_users and receiver_id != sender_id:
                receiver_socket, _ = self.connected_users[receiver_id]
                self.send_message(receiver_socket, response)
                print(f"Сообщение переслано получателю {receiver_id}")
            elif receiver_id != sender_id:
                print(f"Получатель {receiver_id} не найден в подключенных пользователях")
    
    def handle_status_update(self, message: Dict, client_socket: socket.socket, address: tuple):
        """Обработка обновления статуса пользователя"""
        user_id = message.get('user_id')
        is_online = message.get('is_online', True)
        
        if user_id:
            # Обновление статуса в БД
            self.database.update_user_status(user_id, is_online)
            
            # Добавление в список подключенных пользователей
            if is_online:
                self.connected_users[user_id] = (client_socket, address)
                print(f"Пользователь {user_id} подключился. Всего подключено: {len(self.connected_users)}")
                print(f"Подключенные пользователи: {list(self.connected_users.keys())}")
            else:
                if user_id in self.connected_users:
                    del self.connected_users[user_id]
                    print(f"Пользователь {user_id} отключился. Всего подключено: {len(self.connected_users)}")
    
    def handle_heartbeat(self, message: Dict, client_socket: socket.socket, address: tuple):
        """Обработка heartbeat сообщения"""
        user_id = message.get('user_id')
        if user_id:
            # Обновление времени последней активности
            self.database.update_user_status(user_id, True)
            
            # Отправка подтверждения
            response = {
                'type': 'heartbeat_ack',
                'timestamp': time.time()
            }
            self.send_message(client_socket, response)
    
    def handle_call_request(self, message: Dict, client_socket: socket.socket, address: tuple):
        """Обработка запроса на звонок"""
        caller_id = message.get('caller_id')
        receiver_id = message.get('receiver_id')
        
        if caller_id and receiver_id and receiver_id in self.connected_users:
            receiver_socket, _ = self.connected_users[receiver_id]
            
            # Пересылка запроса на звонок
            call_request = {
                'type': 'call_request',
                'caller_id': caller_id,
                'timestamp': time.time()
            }
            self.send_message(receiver_socket, call_request)
    
    def handle_call_response(self, message: Dict, client_socket: socket.socket, address: tuple):
        """Обработка ответа на звонок"""
        caller_id = message.get('caller_id')
        receiver_id = message.get('receiver_id')
        accepted = message.get('accepted', False)
        
        if caller_id and receiver_id and caller_id in self.connected_users:
            caller_socket, _ = self.connected_users[caller_id]
            
            # Пересылка ответа звонящему
            call_response = {
                'type': 'call_response',
                'receiver_id': receiver_id,
                'accepted': accepted,
                'timestamp': time.time()
            }
            self.send_message(caller_socket, call_response)
    
    def handle_call_end(self, message: Dict, client_socket: socket.socket, address: tuple):
        """Обработка завершения звонка"""
        caller_id = message.get('caller_id')
        receiver_id = message.get('receiver_id')
        
        # Уведомление обеих сторон о завершении звонка
        for user_id in [caller_id, receiver_id]:
            if user_id and user_id in self.connected_users:
                user_socket, _ = self.connected_users[user_id]
                call_end = {
                    'type': 'call_end',
                    'timestamp': time.time()
                }
                self.send_message(user_socket, call_end)
    
    def handle_user_list_request(self, message: Dict, client_socket: socket.socket, address: tuple):
        """Обработка запроса списка пользователей"""
        user_id = message.get('user_id')
        if user_id:
            # Получение списка всех пользователей
            users = self.database.get_all_users()
            
            response = {
                'type': 'user_list_response',
                'users': users,
                'timestamp': time.time()
            }
            self.send_message(client_socket, response)
    
    def handle_user_list_response(self, message: Dict, client_socket: socket.socket, address: tuple):
        """Обработка ответа со списком пользователей"""
        # Этот обработчик может использоваться для логирования
        pass
    
    def send_message(self, client_socket: socket.socket, message: Dict):
        """Отправка сообщения клиенту"""
        try:
            data = json.dumps(message).encode('utf-8')
            client_socket.send(data)
        except Exception as e:
            print(f"Ошибка отправки сообщения: {e}")
    
    def heartbeat_loop(self):
        """Цикл отправки heartbeat сообщений"""
        while self.is_running:
            time.sleep(config.HEARTBEAT_INTERVAL)
            
            # Проверка активности пользователей
            current_time = time.time()
            for user_id, (socket, address) in list(self.connected_users.items()):
                try:
                    # Отправка heartbeat
                    heartbeat = {
                        'type': 'heartbeat',
                        'user_id': user_id,
                        'timestamp': current_time
                    }
                    self.send_message(socket, heartbeat)
                except Exception as e:
                    print(f"Ошибка heartbeat для {user_id}: {e}")
                    # Удаление неактивного пользователя
                    del self.connected_users[user_id]
                    self.database.update_user_status(user_id, False)
    
    def stop_server(self):
        """Остановка сервера"""
        self.is_running = False
        
        # Закрытие всех клиентских подключений
        for user_id, (socket, address) in list(self.connected_users.items()):
            try:
                socket.close()
            except:
                pass
            self.database.update_user_status(user_id, False)
        
        # Закрытие серверного сокета
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        
        print("Сервер остановлен")
    
    def connect_to_server(self, host: str, port: int) -> bool:
        """Подключение к серверу как клиент"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((host, port))
            self.is_running = True
            
            # Запуск потока для приема сообщений
            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.daemon = True
            receive_thread.start()
            
            return True
        except Exception as e:
            print(f"Ошибка подключения к серверу: {e}")
            return False
    
    def receive_messages(self):
        """Прием сообщений от сервера"""
        while self.is_running:
            try:
                data = self.socket.recv(4096)
                if not data:
                    break
                
                try:
                    message = json.loads(data.decode('utf-8'))
                    self.process_client_message(message)
                except json.JSONDecodeError:
                    print("Ошибка декодирования JSON")
                    
            except Exception as e:
                if self.is_running:
                    print(f"Ошибка приема сообщений: {e}")
                break
        
        self.is_running = False
    
    def process_client_message(self, message: Dict):
        """Обработка сообщения на стороне клиента"""
        print(f"Получено сообщение: {message}")
        
        # Вызов callback для обработки сообщения в главном окне
        if self.message_callback:
            self.message_callback(message)
    
    def send_client_message(self, message: Dict):
        """Отправка сообщения на сервер"""
        if self.socket and self.is_running:
            try:
                data = json.dumps(message).encode('utf-8')
                self.socket.send(data)
                return True
            except Exception as e:
                print(f"Ошибка отправки сообщения: {e}")
                return False
        return False
