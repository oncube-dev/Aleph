import os

# Настройки приложения
APP_NAME = "Aleph Messenger"
APP_VERSION = "1.0.0"

# Настройки базы данных
DATABASE_PATH = "messenger.db"

# Настройки сети
SERVER_HOST = "127.0.0.1"  # IP-адрес сервера для подключения клиентов
SERVER_PORT = 47990         # Порт сервера (TCP)
HOST = "0.0.0.0"           # Слушаем на всех интерфейсах для внешних подключений (только для сервера)
PORT = 47990                # Порт сервера (дублирует SERVER_PORT для совместимости)
HEARTBEAT_INTERVAL = 30     # секунды
ONLINE_TIMEOUT = 60         # секунды

# Настройки аудио
AUDIO_SAMPLE_RATE = 44100
AUDIO_CHUNK_SIZE = 1024
AUDIO_CHANNELS = 1

# Настройки уведомлений
ENABLE_SOUND_NOTIFICATIONS = True
ENABLE_VISUAL_NOTIFICATIONS = True

# Настройки автоматического обновления
CHAT_UPDATE_INTERVAL = 1000  # миллисекунды (1 секунда)
CONTACTS_UPDATE_INTERVAL = 5000  # миллисекунды (5 секунд)

# Тестовые пользователи по умолчанию
DEFAULT_USERS = ["user1", "user2", "user3", "admin", "test"]

# Пути к файлам
ASSETS_DIR = "assets"
ICONS_DIR = os.path.join(ASSETS_DIR, "icons")
SOUNDS_DIR = os.path.join(ASSETS_DIR, "sounds")

# Создание директорий если не существуют
for directory in [ASSETS_DIR, ICONS_DIR, SOUNDS_DIR]:
    if not os.path.exists(directory):
        os.makedirs(directory)
