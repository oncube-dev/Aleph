# Конфигурация клиента Aleph Messenger
# Этот файл должен находиться в той же папке, что и exe файл

# Настройки сервера
SERVER_HOST = "127.0.0.1"  # IP-адрес сервера (по умолчанию localhost)
SERVER_PORT = 47990         # Порт сервера (по умолчанию 47990)

# Настройки приложения
APP_NAME = "Aleph Messenger"
APP_VERSION = "1.0.0"

# Настройки уведомлений
ENABLE_SOUND_NOTIFICATIONS = True
ENABLE_VISUAL_NOTIFICATIONS = True

# Настройки автоматического обновления
CHAT_UPDATE_INTERVAL = 1000  # миллисекунды (1 секунда)
CONTACTS_UPDATE_INTERVAL = 5000  # миллисекунды (5 секунд)

# Настройки аудио
AUDIO_SAMPLE_RATE = 44100
AUDIO_CHUNK_SIZE = 1024
AUDIO_CHANNELS = 1

# Пути к файлам
ASSETS_DIR = "assets"
ICONS_DIR = "assets/icons"
SOUNDS_DIR = "assets/sounds"
