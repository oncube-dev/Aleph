@echo off
echo ========================================
echo Установка зависимостей Aleph Messenger
echo ========================================
echo.

echo Проверка Python...
python --version
if errorlevel 1 (
    echo.
    echo ОШИБКА: Python не найден в PATH!
    echo.
    echo Попытка найти Python в стандартных местах...
    
    if exist "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python313\python.exe" (
        echo Найден Python в AppData\Local\Programs\Python\Python313
        set PYTHON_PATH=C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python313
        set PATH=%PYTHON_PATH%;%PYTHON_PATH%\Scripts;%PATH%
    ) else if exist "C:\Program Files\Python313\python.exe" (
        echo Найден Python в Program Files\Python313
        set PYTHON_PATH=C:\Program Files\Python313
        set PATH=%PYTHON_PATH%;%PYTHON_PATH%\Scripts;%PATH%
    ) else if exist "C:\Python313\python.exe" (
        echo Найден Python в C:\Python313
        set PYTHON_PATH=C:\Python313
        set PATH=%PYTHON_PATH%;%PYTHON_PATH%\Scripts;%PATH%
    ) else (
        echo Python не найден!
        echo Установите Python с https://python.org
        echo Или добавьте Python в PATH вручную
        pause
        exit /b 1
    )
    
    echo Проверка Python после настройки PATH...
    python --version
    if errorlevel 1 (
        echo ОШИБКА: Python все еще не найден!
        echo Добавьте Python в PATH вручную
        pause
        exit /b 1
    )
)

echo.
echo Проверка pip...
pip --version
if errorlevel 1 (
    echo pip не найден, попытка установки...
    python -m ensurepip --upgrade
    python -m pip install --upgrade pip
) else (
    echo Обновление pip...
    python -m pip install --upgrade pip
)

echo.
echo Установка зависимостей...
pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo Попытка установки по отдельности...
    pip install PySide6
    pip install PyAudio
    pip install requests
    pip install numpy
    pip install scipy
    pip install websockets
    pip install cryptography
)

echo.
echo ========================================
echo Установка завершена!
echo ========================================
echo.
echo Для запуска сервера: python src\core\server.py
echo Для запуска клиента: python main.py
echo.
pause
