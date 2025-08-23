#!/bin/bash

echo "========================================"
echo "Aleph Messenger - Запуск приложения"
echo "========================================"
echo

# Проверка наличия Python
if ! command -v python3 &> /dev/null; then
    echo "ОШИБКА: Python3 не найден!"
    echo "Установите Python 3.7+"
    exit 1
fi

# Проверка версии Python
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
required_version="3.7"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "ОШИБКА: Требуется Python $required_version+, найдена версия $python_version"
    exit 1
fi

echo "Python $python_version найден"

# Установка зависимостей
echo "Установка зависимостей..."
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "ОШИБКА: Не удалось установить зависимости!"
    echo "Попробуйте: pip3 install PyQt5 PyAudio"
    exit 1
fi

echo
echo "Зависимости установлены успешно!"
echo
echo "Для запуска мессенджера:"
echo "1. Запустите сервер: python3 server.py"
echo "2. В новом терминале запустите клиент: python3 main.py"
echo

# Сделать скрипт исполняемым
chmod +x run.sh

echo "Нажмите Enter для выхода..."
read
