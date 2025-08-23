import os

# Настройки сервера
APP_NAME = "Aleph Messenger Server"
APP_VERSION = "1.0.0"

# Настройки базы данных
DATABASE_PATH = "messenger.db"

# Настройки сети для сервера
HOST = "0.0.0.0"  # Слушаем на всех интерфейсах для внешних подключений
PORT = 47990       # Порт сервера
HEARTBEAT_INTERVAL = 30  # секунды
ONLINE_TIMEOUT = 60  # секунды

# Внешний IP (для информации)
EXTERNAL_IP = "31.131.220.221"
EXTERNAL_PORT = 47990

# Настройки аудио
AUDIO_SAMPLE_RATE = 44100
AUDIO_CHUNK_SIZE = 1024
AUDIO_CHANNELS = 1

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

# Настройки безопасности
MAX_CONNECTIONS = 100  # Максимальное количество одновременных подключений
CONNECTION_TIMEOUT = 300  # Таймаут неактивного подключения (5 минут)
