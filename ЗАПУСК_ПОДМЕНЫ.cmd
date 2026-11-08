@echo off
chcp 65001 >nul 2>&1
title mkusha - Подмена локации iPhone

echo.
echo ========================================================
echo   mkusha - Подмена геопозиции iPhone
echo   Работает напрямую через USB (БЕЗ паролей и БЕЗ Apple ID!)
echo ========================================================
echo.

python "%~dp0spoofer_server.py"

pause
