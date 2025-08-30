@echo off
echo ========================================
echo Aleph Messenger - Запуск приложения
echo ========================================
echo.

REM Проверка наличия Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ОШИБКА: Python не найден!
    echo Установите Python 3.7+ и добавьте в PATH
    pause
    exit /b 1
)

REM Установка базовых зависимостей
echo Установка базовых зависимостей...
pip install -r requirements_basic.txt

echo.
echo Попытка установки PyAudio для голосовых звонков...
echo.

REM Попытка установки PyAudio
echo Вариант 1: Стандартная установка...
pip install pyaudio

if errorlevel 1 (
    echo.
    echo PyAudio не установился стандартным способом.
    echo Пробуем альтернативные варианты...
    echo.
    
    echo Вариант 2: Попытка установки предварительно скомпилированной версии...
    pip install --only-binary=all pyaudio
    
    if errorlevel 1 (
        echo.
        echo Все варианты установки PyAudio не удались.
        echo.
        echo РЕШЕНИЕ: Скачайте wheel файл PyAudio для Python 3.12:
        echo https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
        echo.
        echo Пример: pip install PyAudio-0.2.11-cp312-cp312-win_amd64.whl
        echo.
        echo Примечание: Без PyAudio голосовые звонки будут отключены,
        echo но текстовый чат будет работать нормально.
        echo.
    )
)

if errorlevel 1 (
    echo ОШИБКА: Не удалось установить зависимости!
    echo Попробуйте: pip install PyQt5 PyAudio
    pause
    exit /b 1
)

echo.
echo Зависимости установлены успешно!
echo.
echo Для запуска мессенджера:
echo 1. Запустите сервер: python server.py
echo 2. В новом окне запустите клиент: python main.py
echo.
pause
