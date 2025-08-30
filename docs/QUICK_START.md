# Быстрый старт Aleph Messenger

## Что это за приложение?

**Aleph Messenger** - это десктопный мессенджер с поддержкой:
- 📝 Текстовых сообщений в реальном времени
- 📞 Голосовых звонков
- 👥 Списка контактов
- 🟢 Индикаторов онлайн-статуса

## Быстрая установка

### 1. Проверка Python
```bash
python --version  # Должен быть Python 3.7+
```

### 2. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 3. Запуск сервера
```bash
python src/core/server.py
```

### 4. Запуск клиента (в новом терминале)
```bash
python main.py
```

## Тестирование

### Создание тестовых пользователей
При первом запуске автоматически создаются:
- `user1`, `user2`, `user3`
- `admin`, `test`

### Проверка работы
1. Запустите сервер
2. Запустите первый клиент с ID `user1`
3. Запустите второй клиент с ID `user2`
4. Добавьте `user2` в контакты `user1`
5. Отправьте сообщение

## Структура для разработчиков

### Основные файлы
- `main.py` - точка входа клиента
- `src/core/server.py` - сервер
- `src/ui/main_window.py` - главное окно
- `src/network/network_manager.py` - сеть
- `src/database/database.py` - база данных

### Добавление новой функции
1. **Новый тип сообщения**: добавьте в `NetworkManager`
2. **Новый UI элемент**: создайте в `src/ui/`
3. **Новая таблица БД**: добавьте в `Database.init_database()`

## Отладка

### Логи сервера
```bash
python src/core/server.py
# Следите за выводом в консоли
```

### Логи клиента
```bash
python main.py
# Ошибки отображаются в консоли
```

### Проверка портов
```bash
# Windows
netstat -an | findstr 47990

# Linux/macOS
netstat -an | grep 47990
```

## Частые проблемы

### PyAudio не устанавливается
**Windows:**
```bash
pip install pipwin
pipwin install pyaudio
```

**Linux:**
```bash
sudo apt-get install portaudio19-dev
pip install pyaudio
```

### Порт занят
```bash
# Остановите другие приложения на порту 47990
# Или измените порт в src/config/config.py
```

### База данных повреждена
```bash
# Удалите messenger.db и перезапустите
rm messenger.db
python main.py
```

## Следующие шаги

1. **Изучите код** в `src/` папке
2. **Добавьте новую функцию** (например, файлы)
3. **Напишите тесты** в папке `tests/`
4. **Улучшите UI** в `src/ui/`

## Полезные команды

### Запуск тестов
```bash
python tests/test_app.py
```

### Сборка приложения
```bash
# Windows
src\utils\build.bat

# Linux/macOS
pyinstaller --onefile main.py
```

### Очистка
```bash
# Удалить кэш Python
find . -name "__pycache__" -exec rm -rf {} +
find . -name "*.pyc" -delete
```
