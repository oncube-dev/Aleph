@echo off
echo ==================================================
echo Сборка Aleph Messenger v1.0.0
echo ==================================================

echo.
echo Очистка предыдущих сборок...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"

echo.
echo Сборка приложения...
pyinstaller build.spec --distpath builds

echo.
echo Проверка результата...
if exist "builds\AlephMessenger.exe" (
    echo ✓ Сборка завершена успешно!
    echo.
    echo Файл: builds\AlephMessenger.exe
    echo Размер: 
    dir "builds\AlephMessenger.exe" | find "AlephMessenger.exe"
    echo.
    echo Приложение готово к использованию!
    echo IP сервера: 31.131.220.221:47990
) else (
    echo ❌ Ошибка сборки!
)

echo.
pause
