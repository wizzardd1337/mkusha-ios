@echo off
chcp 65001 >nul 2>&1
title mkusha ios — установка
cd /d "%~dp0"

:: ──────────────────────────────────────────────
:: mkusha ios installer launcher
:: Автоматически создаёт venv и ставит pymobiledevice3
:: ──────────────────────────────────────────────

:: Выбираем Python: py -3.12, потом py -3, потом python
set "PY="
where py >nul 2>&1 && (
    py -3.12 --version >nul 2>&1 && set "PY=py -3.12" || (
        py -3 --version >nul 2>&1 && set "PY=py -3"
    )
)
if not defined PY (
    where python >nul 2>&1 && set "PY=python"
)
if not defined PY (
    echo [mkusha] Python не найден. Установи Python 3.10+ и попробуй снова.
    echo          https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [mkusha] Python: %PY%

if not exist ".venv\Scripts\python.exe" (
    echo [mkusha] Создаю виртуальное окружение...
    %PY% -m venv .venv
    if errorlevel 1 (
        echo [mkusha] Ошибка создания venv.
        pause
        exit /b 1
    )
)

echo [mkusha] Проверяю зависимости...
".venv\Scripts\python.exe" -c "import pymobiledevice3" 2>nul
if errorlevel 1 (
    echo [mkusha] Устанавливаю pymobiledevice3...
    ".venv\Scripts\python.exe" -m pip install --upgrade pip >nul 2>&1
    ".venv\Scripts\python.exe" -m pip install pymobiledevice3
    if errorlevel 1 (
        echo [mkusha] Ошибка установки pymobiledevice3.
        pause
        exit /b 1
    )
)

echo [mkusha] Запускаю установщик...
echo.
".venv\Scripts\python.exe" install.py %*
if errorlevel 1 (
    echo.
    echo [mkusha] Установщик завершился с ошибкой.
    pause
)
